"""Herramienta propia: disponibilidad compuesta de un sistema.

Calcula la disponibilidad de una topología de componentes en serie, en paralelo
(redundancia activa) y con redundancia k-de-n, y reporta:
  - disponibilidad total, número de "nueves" y tiempo fuera de servicio esperado,
  - el componente más débil y los puntos únicos de falla (componentes en la cadena
    principal que no tienen redundancia).

La topología se describe con una expresión pequeña, por ejemplo:

    serie(lb=99.99%, paralelo(app1=0.999, app2=0.999), db=0.9995)
    serie(api=0.999, kden(2, 3, 0.99))

Gramática (se analiza con un parser descendente recursivo escrito a mano; NUNCA se usa eval):

    expr     := funcion | hoja
    funcion  := ("serie" | "paralelo") "(" expr ("," expr)* ")"
              | "kden" "(" ENTERO "," ENTERO "," hoja ")"
              | "replicas" "(" ENTERO "," hoja ")"
    hoja     := [NOMBRE "="] NUMERO ["%"]      (decimales con punto: 0.999 o 99.9%)

Fórmulas:
    serie:     A = A1 * A2 * ... * An
    paralelo:  A = 1 - (1 - A1)(1 - A2)...(1 - An)
    k-de-n:    A = sum_{i=k}^{n} C(n, i) * a^i * (1 - a)^(n - i)   (n réplicas idénticas, basta con k)
    replicas:  igual a paralelo de n copias idénticas (k-de-n con k = 1)
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

MAX_LONGITUD_EXPRESION = 2000
MAX_PROFUNDIDAD = 10
MAX_COMPONENTES = 200
MAX_REPLICAS = 100

# Año de 365.25 días y mes = año/12, la misma convención de la tabla "Availability in numbers" del corpus [SDP].
MINUTOS_ANIO = 365.25 * 24 * 60
MINUTOS_MES = MINUTOS_ANIO / 12


class ErrorTopologia(ValueError):
    """Entrada inválida. El mensaje es apto para mostrarlo al usuario."""


# ---------------------------------------------------------------------------
# Árbol de la topología
# ---------------------------------------------------------------------------
@dataclass
class Nodo:
    tipo: str                       # "hoja" | "serie" | "paralelo" | "kden"
    nombre: str = ""
    valor: float = 0.0              # solo hojas
    hijos: list["Nodo"] = field(default_factory=list)
    k: int = 0                      # solo kden
    n: int = 0                      # solo kden

    def disponibilidad(self) -> float:
        if self.tipo == "hoja":
            return self.valor
        if self.tipo == "serie":
            return math.prod(h.disponibilidad() for h in self.hijos)
        if self.tipo == "paralelo":
            return 1.0 - math.prod(1.0 - h.disponibilidad() for h in self.hijos)
        if self.tipo == "kden":
            a = self.hijos[0].disponibilidad()
            return sum(math.comb(self.n, i) * a**i * (1 - a) ** (self.n - i) for i in range(self.k, self.n + 1))
        raise ErrorTopologia(f"tipo de nodo desconocido: {self.tipo}")

    def describir(self) -> str:
        if self.tipo == "hoja":
            return f"{self.nombre}={self.valor:g}" if self.nombre else f"{self.valor:g}"
        if self.tipo == "kden":
            if self.k == 1:
                return f"replicas({self.n}, {self.hijos[0].describir()})"
            return f"kden({self.k}, {self.n}, {self.hijos[0].describir()})"
        return f"{self.tipo}(" + ", ".join(h.describir() for h in self.hijos) + ")"


# ---------------------------------------------------------------------------
# Analizador léxico y sintáctico
# ---------------------------------------------------------------------------
_TOKEN = re.compile(r"\s*(?:(?P<num>\d+(?:\.\d+)?(?:[eE]-?\d+)?)|(?P<id>[A-Za-z_][A-Za-z0-9_\-]*)|(?P<sim>[(),=%]))")


def _tokenizar(texto: str) -> list[tuple[str, str]]:
    tokens, pos = [], 0
    texto = texto.strip()
    while pos < len(texto):
        m = _TOKEN.match(texto, pos)
        if not m or m.end() == pos:
            raise ErrorTopologia(f"carácter no válido en la posición {pos + 1}: '{texto[pos]}'")
        clase = m.lastgroup
        tokens.append((clase, m.group(clase)))
        pos = m.end()
        while pos < len(texto) and texto[pos].isspace():
            pos += 1
    return tokens


class _Parser:
    def __init__(self, texto: str):
        self.tokens = _tokenizar(texto)
        self.i = 0
        self.hojas = 0

    # utilidades -------------------------------------------------------------
    def _ver(self, desplazamiento: int = 0):
        j = self.i + desplazamiento
        return self.tokens[j] if j < len(self.tokens) else (None, None)

    def _tomar(self, esperado: str | None = None) -> str:
        clase, valor = self._ver()
        if clase is None:
            raise ErrorTopologia("la expresión terminó antes de tiempo (¿falta cerrar un paréntesis?)")
        if esperado is not None and valor != esperado:
            raise ErrorTopologia(f"se esperaba '{esperado}' y llegó '{valor}'")
        self.i += 1
        return valor

    def _entero(self, que: str) -> int:
        clase, valor = self._ver()
        if clase != "num" or not re.fullmatch(r"\d+", valor):
            raise ErrorTopologia(f"{que} debe ser un entero positivo (llegó '{valor}')")
        self.i += 1
        return int(valor)

    # gramática --------------------------------------------------------------
    def analizar(self) -> Nodo:
        if not self.tokens:
            raise ErrorTopologia("la topología está vacía")
        nodo = self._expr(0)
        if self.i != len(self.tokens):
            raise ErrorTopologia(f"sobra texto después de la expresión: '{self._ver()[1]}'")
        return nodo

    def _expr(self, profundidad: int) -> Nodo:
        if profundidad > MAX_PROFUNDIDAD:
            raise ErrorTopologia(f"la topología supera {MAX_PROFUNDIDAD} niveles de anidamiento")
        clase, valor = self._ver()
        siguiente = self._ver(1)[1]
        if clase == "id" and siguiente == "(":
            return self._funcion(valor.lower(), profundidad)
        return self._hoja()

    def _funcion(self, nombre: str, profundidad: int) -> Nodo:
        self._tomar()           # nombre
        self._tomar("(")
        if nombre in ("serie", "paralelo"):
            if self._ver()[1] == ")":
                raise ErrorTopologia(f"{nombre}() necesita al menos un componente")
            hijos = [self._expr(profundidad + 1)]
            while self._ver()[1] == ",":
                self._tomar(",")
                hijos.append(self._expr(profundidad + 1))
            self._tomar(")")
            return Nodo(tipo=nombre, hijos=hijos)
        if nombre == "kden":
            k = self._entero("k")
            self._tomar(",")
            n = self._entero("n")
            self._tomar(",")
            hoja = self._hoja()
            self._tomar(")")
            self._validar_kn(k, n)
            return Nodo(tipo="kden", k=k, n=n, hijos=[hoja])
        if nombre == "replicas":
            n = self._entero("el número de réplicas")
            self._tomar(",")
            hoja = self._hoja()
            self._tomar(")")
            self._validar_kn(1, n)
            return Nodo(tipo="kden", k=1, n=n, hijos=[hoja])
        raise ErrorTopologia(f"función desconocida '{nombre}'. Use serie, paralelo, kden o replicas")

    @staticmethod
    def _validar_kn(k: int, n: int) -> None:
        if n < 1:
            raise ErrorTopologia("n debe ser al menos 1")
        if n > MAX_REPLICAS:
            raise ErrorTopologia(f"n no puede superar {MAX_REPLICAS} réplicas")
        if k < 1:
            raise ErrorTopologia("k debe ser al menos 1")
        if k > n:
            raise ErrorTopologia(f"k ({k}) no puede ser mayor que n ({n})")

    def _hoja(self) -> Nodo:
        nombre = ""
        clase, valor = self._ver()
        if clase == "id" and self._ver(1)[1] == "=":
            nombre = valor
            self.i += 2
            clase, valor = self._ver()
        if clase != "num":
            raise ErrorTopologia(f"se esperaba un valor de disponibilidad y llegó '{valor}'")
        self.i += 1
        numero = float(valor)
        es_porcentaje = self._ver()[1] == "%"
        if es_porcentaje:
            self.i += 1
            numero /= 100.0
        elif numero > 1.0:
            # 99.9 sin "%" se interpreta como porcentaje si está en (1, 100]
            if numero <= 100.0:
                numero /= 100.0
            else:
                raise ErrorTopologia(f"disponibilidad fuera de rango: {valor}")
        if not 0.0 <= numero <= 1.0:
            raise ErrorTopologia(f"disponibilidad fuera de rango [0, 1]: {valor}")
        self.hojas += 1
        if self.hojas > MAX_COMPONENTES:
            raise ErrorTopologia(f"la topología supera {MAX_COMPONENTES} componentes")
        return Nodo(tipo="hoja", nombre=nombre or f"c{self.hojas}", valor=numero)


def analizar_topologia(expresion: str) -> Nodo:
    if not isinstance(expresion, str):
        raise ErrorTopologia("la topología debe ser un texto")
    if len(expresion) > MAX_LONGITUD_EXPRESION:
        raise ErrorTopologia(f"la expresión supera {MAX_LONGITUD_EXPRESION} caracteres")
    return _Parser(expresion).analizar()


# ---------------------------------------------------------------------------
# Resultado
# ---------------------------------------------------------------------------
def nueves(a: float) -> float:
    """Número de nueves: -log10(1 - A). Infinito si A = 1."""
    if a >= 1.0:
        return math.inf
    if a <= 0.0:
        return 0.0
    return -math.log10(1.0 - a)


def formatear_tiempo(minutos: float) -> str:
    if minutos < 1:
        return f"{minutos * 60:.1f} s"
    if minutos < 120:
        return f"{minutos:.1f} min"
    if minutos < 48 * 60:
        return f"{minutos / 60:.2f} h"
    return f"{minutos / 1440:.2f} días"


def _puntos_unicos_de_falla(raiz: Nodo) -> list[Nodo]:
    """Hojas cuya falla tumba todo el sistema: están en la cadena de serie principal sin redundancia."""
    if raiz.tipo == "hoja":
        return [raiz]
    if raiz.tipo == "serie":
        spof = []
        for h in raiz.hijos:
            spof.extend(_puntos_unicos_de_falla(h))
        return spof
    # paralelo o k-de-n: un componente individual ya no tumba el sistema
    # (salvo paralelo de un solo hijo o k = n, que no aportan redundancia)
    if raiz.tipo == "paralelo" and len(raiz.hijos) == 1:
        return _puntos_unicos_de_falla(raiz.hijos[0])
    if raiz.tipo == "kden" and raiz.k == raiz.n:
        return [raiz.hijos[0]]
    return []


def calcular_disponibilidad(expresion: str) -> dict:
    """Punto de entrada de la herramienta. Devuelve un diccionario serializable."""
    raiz = analizar_topologia(expresion)
    a = raiz.disponibilidad()
    a = min(max(a, 0.0), 1.0)
    indisponibilidad = 1.0 - a

    avisos = []
    hijos_principales = raiz.hijos if raiz.tipo == "serie" else [raiz]
    debil = min(hijos_principales, key=lambda h: h.disponibilidad())
    spof = _puntos_unicos_de_falla(raiz)
    if any(h.tipo == "hoja" and h.valor == 1.0 for h in _hojas(raiz)):
        avisos.append("Hay componentes con disponibilidad 1 (100 %): en la práctica ningún componente es perfecto.")
    if any(h.tipo == "hoja" and h.valor == 0.0 for h in _hojas(raiz)):
        avisos.append("Hay componentes con disponibilidad 0: siempre están caídos.")
    if raiz.tipo == "hoja":
        avisos.append("La topología tiene un solo componente: la disponibilidad es la del componente.")

    return {
        "topologia": raiz.describir(),
        "disponibilidad": a,
        "disponibilidad_pct": round(a * 100, 6),
        "nueves": None if math.isinf(nueves(a)) else round(nueves(a), 2),
        "caida_anual": formatear_tiempo(indisponibilidad * MINUTOS_ANIO),
        "caida_mensual": formatear_tiempo(indisponibilidad * MINUTOS_MES),
        "eslabon_mas_debil": debil.describir(),
        "eslabon_mas_debil_disp": round(debil.disponibilidad(), 6),
        "puntos_unicos_de_falla": [h.nombre for h in spof],
        "componentes": len(_hojas(raiz)),
        "avisos": avisos,
    }


def _hojas(nodo: Nodo) -> list[Nodo]:
    if nodo.tipo == "hoja":
        return [nodo]
    return [h for hijo in nodo.hijos for h in _hojas(hijo)]


def resumen_texto(r: dict) -> str:
    """Texto corto y determinista con el resultado, para pasarlo al modelo y a las trazas."""
    lineas = [
        f"Topología: {r['topologia']}",
        f"Disponibilidad total: {r['disponibilidad_pct']:.4f} %"
        + (f" ({r['nueves']} nueves)" if r["nueves"] is not None else " (100 %)"),
        f"Caída esperada: {r['caida_anual']} al año, {r['caida_mensual']} al mes",
        f"Eslabón más débil de la cadena principal: {r['eslabon_mas_debil']} ({r['eslabon_mas_debil_disp'] * 100:.4f} %)",
        "Puntos únicos de falla: " + (", ".join(r["puntos_unicos_de_falla"]) or "ninguno"),
    ]
    lineas += [f"Aviso: {a}" for a in r["avisos"]]
    return "\n".join(lineas)
