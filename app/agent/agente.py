"""Ciclo de decisión del agente (escrito a mano, sin agentes prefabricados).

    pregunta
       │
       ▼
  1. CLASIFICAR  ── reglas → (si dudan) modelo por API → (si falla) valor por defecto
       │
       ▼
  2. DECIDIR     ── tabla ACCION_POR_TIPO: rag | herramienta | directa
       │
       ▼
  3. VERIFICAR   ── reglas de corrección: ¿la decisión es coherente con la pregunta?
       │             (ej.: "cálculo" sin ningún número → se corrige a "rag")
       ▼
  4. EJECUTAR    ── rag: recuperar fragmentos; si ninguno supera el umbral → sin_evidencia
       │             herramienta: extraer topología → calcular (con un reintento si falla)
       │             directa: respuesta fija, sin modelo
       ▼
  5. REDACTAR    ── prompt de sistema fijo + [instrucciones y ejemplos del tipo] + fragmentos
       │             + resultado de la herramienta + pregunta
       ▼
  6. REVISAR     ── se comprueba que las citas de la respuesta existan en los fragmentos
       │
       ▼
  respuesta + traza (JSONL)
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field

from app.agent.clasificador import Clasificacion, clasificar
from app.agent.fewshot import SelectorEjemplos, instrucciones_de, mensaje_usuario
from app.agent.prompts import (PROMPT_EXTRACTOR, PROMPT_SISTEMA, RESPUESTA_DIRECTA,
                               RESPUESTA_SIN_EVIDENCIA)
from app.agent.trazas import RegistroTrazas, Traza
from app.rag.indice import Recuperador, Resultado, contexto_para_prompt
from app.tools.disponibilidad import ErrorTopologia, calcular_disponibilidad, resumen_texto

RAG, HERRAMIENTA, DIRECTA = "rag", "herramienta", "directa"

# Paso 2: tabla de decisión. Es la regla central y se explica sola.
ACCION_POR_TIPO = {
    "conceptual": RAG,
    "seleccion": RAG,
    "compromisos": RAG,
    "calculo": HERRAMIENTA,
    "saludo": DIRECTA,
    "fuera_de_dominio": DIRECTA,
}

_HAY_NUMEROS = re.compile(r"\d+(\.\d+)?\s*%|\b0\.\d+\b|\b9\d(\.\d+)?\b")
_INICIO_EXPRESION = re.compile(r"\b(serie|paralelo|kden|replicas)\s*\(", re.I)
_CITA = re.compile(r"\[[A-Z0-9][A-Z0-9\-]*, (?:§[^\]]+|p\. \d+)\]")


def extraer_expresion_explicita(texto: str) -> str | None:
    """Si el usuario escribió serie(...)/paralelo(...), devuelve la expresión con paréntesis balanceados."""
    m = _INICIO_EXPRESION.search(texto)
    if not m:
        return None
    nivel, inicio = 0, m.start()
    for i in range(m.end() - 1, len(texto)):
        if texto[i] == "(":
            nivel += 1
        elif texto[i] == ")":
            nivel -= 1
            if nivel == 0:
                return texto[inicio:i + 1]
    return texto[inicio:]  # paréntesis sin cerrar: el parser de la herramienta reporta el error


@dataclass
class Turno:
    respuesta: str
    traza: Traza
    accion: str
    tipo: str
    fragmentos: list = field(default_factory=list)          # fragmentos entregados al redactor
    resultado_herramienta: str | None = None


class Agente:
    def __init__(self, cfg, recuperador: Recuperador | None, selector: SelectorEjemplos | None,
                 cliente_decision=None, cliente_redaccion=None, registro: RegistroTrazas | None = None):
        self.cfg = cfg
        self.recuperador = recuperador
        self.selector = selector
        self.cliente_decision = cliente_decision
        self.cliente_redaccion = cliente_redaccion
        self.registro = registro

    # ------------------------------------------------------------------ ciclo
    def responder(self, pregunta: str, chat_id=None, fewshot: bool | None = None,
                  fragmentos_fijos: list[Resultado] | None = None, clasificacion_fija: Clasificacion | None = None,
                  guardar: bool = True) -> Turno:
        """fragmentos_fijos y clasificacion_fija permiten a la comparación usar EXACTAMENTE la misma
        clasificación y los mismos fragmentos en las dos versiones: solo varía el elemento evaluado."""
        pregunta = pregunta.strip()
        traza = Traza(pregunta, chat_id)
        fewshot = self.cfg.fewshot_activo if fewshot is None else fewshot

        # 1. Clasificar
        t = time.perf_counter()
        clasif: Clasificacion = clasificacion_fija or clasificar(pregunta, self.cliente_decision)
        traza.latencia("clasificacion", time.perf_counter() - t)
        traza.paso("clasificar", **clasif.a_dict())

        # 2. Decidir
        tipo = clasif.tipo
        accion = ACCION_POR_TIPO[tipo]
        traza.paso("decidir", tipo=tipo, accion=accion)

        # 3. Verificar la decisión (reglas de corrección)
        expresion = extraer_expresion_explicita(pregunta)
        if accion == HERRAMIENTA and not expresion and not _HAY_NUMEROS.search(pregunta):
            tipo, accion = "conceptual", RAG
            traza.paso("corregir", de="herramienta", a="rag",
                       motivo="se clasificó como cálculo pero la pregunta no trae valores numéricos")
        elif accion != HERRAMIENTA and expresion:
            tipo, accion = "calculo", HERRAMIENTA
            traza.paso("corregir", de=ACCION_POR_TIPO[clasif.tipo], a="herramienta",
                       motivo="la pregunta contiene una expresión de topología explícita")

        # 4. Ejecutar
        resultados: list[Resultado] = []
        resultado_herramienta: str | None = None

        if accion == DIRECTA:
            respuesta = RESPUESTA_DIRECTA[tipo]
            traza.paso("responder_directo", tipo=tipo)
            return self._cerrar(traza, respuesta, accion, tipo, guardar)

        if accion == HERRAMIENTA:
            resultado_herramienta, error = self._usar_herramienta(pregunta, expresion, traza)
            if error:
                respuesta = (f"**Respuesta:** No pude calcular la disponibilidad: {error}.\n"
                             "**Explicación:**\n- Escriba la topología con este formato, por ejemplo:\n"
                             "  serie(lb=99.99%, paralelo(app1=0.999, app2=0.999), db=0.9995)\n"
                             "- serie = todos son necesarios; paralelo = basta uno; kden(k, n, a) = k de n réplicas.\n"
                             "**Fuentes:** ninguna.")
                return self._cerrar(traza, respuesta, "herramienta_error", tipo, guardar)
            # Fragmentos de apoyo para citar la fórmula (serie / paralelo)
            resultados = fragmentos_fijos if fragmentos_fijos is not None else self._recuperar(
                "disponibilidad en serie y en paralelo, availability in sequence vs in parallel", traza, k=2)

        if accion == RAG:
            resultados = fragmentos_fijos if fragmentos_fijos is not None else self._recuperar(pregunta, traza)
            if not resultados:
                traza.paso("sin_evidencia", umbral=self.cfg.rag_umbral)
                return self._cerrar(traza, RESPUESTA_SIN_EVIDENCIA, "sin_evidencia", tipo, guardar)

        # 5. Redactar
        mensajes = self._armar_prompt(pregunta, tipo, resultados, resultado_herramienta, fewshot, traza)
        t = time.perf_counter()
        try:
            respuesta, _ = self.cliente_redaccion.chat(mensajes)
        except Exception as e:  # noqa: BLE001
            traza.paso("error_redaccion", error=f"{type(e).__name__}: {e}"[:300])
            respuesta = ("Tuve un problema con el modelo que redacta la respuesta. "
                         "Intente de nuevo en un momento.")
            return self._cerrar(traza, respuesta, "error", tipo, guardar)
        traza.latencia("redaccion", time.perf_counter() - t)

        # 6. Revisar citas
        permitidas = {r.fragmento.cita() for r in resultados}
        usadas = set(_CITA.findall(respuesta))
        traza.paso("revisar_citas", citas_usadas=sorted(usadas), citas_invalidas=sorted(usadas - permitidas),
                   sin_citas=not usadas)
        turno = self._cerrar(traza, respuesta, accion, tipo, guardar)
        turno.fragmentos, turno.resultado_herramienta = resultados, resultado_herramienta
        return turno

    # ------------------------------------------------------------ auxiliares
    def _recuperar(self, consulta: str, traza: Traza, k: int | None = None) -> list[Resultado]:
        if self.recuperador is None:
            traza.paso("recuperar", error="no hay índice cargado")
            return []
        t = time.perf_counter()
        todos = self.recuperador.buscar(consulta, k or self.cfg.rag_k)
        traza.latencia("recuperacion", time.perf_counter() - t)
        utiles = [r for r in todos if r.puntaje >= self.cfg.rag_umbral]
        traza.paso("recuperar", consulta=consulta, k=k or self.cfg.rag_k, umbral=self.cfg.rag_umbral,
                   resultados=[{"pos": r.posicion, "cita": r.fragmento.cita(), "puntaje": round(r.puntaje, 3),
                                "usado": r.puntaje >= self.cfg.rag_umbral} for r in todos])
        return utiles

    def _usar_herramienta(self, pregunta: str, expresion: str | None, traza: Traza) -> tuple[str | None, str | None]:
        """Devuelve (resumen_del_resultado, error). Un reintento si el modelo extrae mal la topología."""
        metodo = "explicita" if expresion else "llm"
        error_previo = None
        for intento in (1, 2):
            if metodo == "llm":
                expresion, falta = self._extraer_con_llm(pregunta, error_previo)
                if not expresion:
                    traza.paso("herramienta", intento=intento, metodo=metodo, error=falta or "no se pudo extraer la topología")
                    return None, falta or "no encontré la topología en la pregunta"
            t = time.perf_counter()
            try:
                r = calcular_disponibilidad(expresion)
            except ErrorTopologia as e:
                traza.paso("herramienta", intento=intento, metodo=metodo, expresion=expresion, error=str(e))
                if metodo == "explicita":
                    return None, str(e)  # el usuario escribió la expresión: se le muestra el error
                error_previo = f"La expresión '{expresion}' es inválida: {e}"
                continue
            traza.latencia("herramienta", time.perf_counter() - t)
            traza.paso("herramienta", intento=intento, metodo=metodo, expresion=expresion,
                       disponibilidad=r["disponibilidad"], spof=r["puntos_unicos_de_falla"])
            return resumen_texto(r), None
        return None, error_previo

    def _extraer_con_llm(self, pregunta: str, error_previo: str | None) -> tuple[str | None, str | None]:
        if self.cliente_decision is None:
            return None, "no hay modelo para interpretar la descripción; escriba la topología con serie(...)/paralelo(...)"
        mensajes = [{"role": "system", "content": PROMPT_EXTRACTOR}, {"role": "user", "content": pregunta}]
        if error_previo:
            mensajes.append({"role": "user", "content": f"{error_previo}. Corrige la expresión."})
        try:
            texto, _ = self.cliente_decision.chat(mensajes, temperatura=0.0, max_tokens=400, json=True)
            datos = json.loads(re.search(r"\{.*\}", texto, re.S).group(0))
            return datos.get("expresion"), datos.get("falta")
        except Exception as e:  # noqa: BLE001
            return None, f"fallo al interpretar la topología ({type(e).__name__})"

    def _armar_prompt(self, pregunta, tipo, resultados, resultado_herramienta, fewshot, traza) -> list[dict]:
        mensajes = [{"role": "system", "content": PROMPT_SISTEMA}]
        ids = []
        if fewshot and self.selector is not None:
            ejemplos = self.selector.seleccionar(pregunta, tipo, self.cfg.fewshot_k, self.cfg.fewshot_criterio)
            ids = [e.id for e in ejemplos]
            instr = instrucciones_de(tipo)
            if instr:
                mensajes.append({"role": "system", "content": instr})
            mensajes += self.selector.mensajes_de(ejemplos)
        traza.paso("armar_prompt", fewshot=fewshot, criterio=self.cfg.fewshot_criterio if fewshot else None,
                   ejemplos=ids, fragmentos=len(resultados), herramienta=bool(resultado_herramienta),
                   modelo=getattr(self.cliente_redaccion, "nombre", None))
        mensajes.append({"role": "user", "content": mensaje_usuario(pregunta, contexto_para_prompt(resultados),
                                                                   resultado_herramienta)})
        return mensajes

    def _cerrar(self, traza: Traza, respuesta: str, accion: str, tipo: str, guardar: bool) -> Turno:
        traza.cerrar(respuesta, accion_final=accion, tipo_final=tipo)
        if guardar and self.registro:
            self.registro.guardar(traza)
        return Turno(respuesta, traza, accion, tipo)
