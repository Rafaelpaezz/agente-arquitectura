"""Clasificación de la pregunta: reglas explícitas primero, modelo por API solo si las reglas dudan.

Por qué así (ver docs/adr/0003-criterio-logica-de-decision.md):
  - Las reglas son deterministas, gratis, instantáneas y se pueden explicar línea por línea.
  - Cuando ninguna regla gana con claridad, se pide la clasificación a un modelo por API con
    salida JSON restringida a las categorías válidas.
  - Si el modelo no responde o devuelve algo inválido, se usa un valor por defecto seguro
    ("conceptual"): ir al corpus y, si no hay evidencia, decirlo.
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field

from app.agent.prompts import PROMPT_CLASIFICADOR

TIPOS = ("conceptual", "seleccion", "calculo", "compromisos", "saludo", "fuera_de_dominio")

# Umbrales de la decisión por reglas
PUNTAJE_MINIMO = 2      # el tipo ganador necesita al menos este puntaje
MARGEN_MINIMO = 1       # y ganarle al segundo por al menos este margen


def normalizar(texto: str) -> str:
    """Minúsculas y sin tildes, para que las reglas no dependan de la ortografía."""
    t = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


# Cada regla es (patrón, peso). Los patrones se aplican sobre el texto normalizado.
REGLAS: dict[str, list[tuple[str, int]]] = {
    "calculo": [
        (r"\b(serie|paralelo|kden|replicas)\s*\(", 4),                 # expresión explícita
        (r"\d+(\.\d+)?\s*%|\b0\.\d{2,}\b", 1),                          # valores de disponibilidad
        (r"\b(calcula|calcular|cuanto|cuantos|que disponibilidad|cual es la disponibilidad|nueves)\b", 1),
        (r"\b(en serie|en paralelo|redundan\w*|replica\w*|puntos? unicos? de falla|spof|downtime|tiempo de caida|caida (anual|mensual))\b", 1),
        (r"\bdisponibilidad (total|compuesta|del sistema|resultante)\b", 1),
    ],
    "compromisos": [
        (r"\b(vs\.?|versus|frente a)\b", 2),
        (r"\b(compromiso|compromisos|trade-?offs?|sacrific\w*|a costa de|tension|equilibri\w*|balance)\b", 2),
        (r"\b(latencia|consistencia|disponibilidad|rendimiento|escalabilidad|seguridad|mantenibilidad|costo|throughput)\b.*\b(latencia|consistencia|disponibilidad|rendimiento|escalabilidad|seguridad|mantenibilidad|costo|throughput)\b", 1),
        (r"\b(que se gana|que se pierde|ventajas y desventajas|pros y contras|impacto en)\b", 1),
    ],
    "seleccion": [
        (r"\b(que|cual) (patron|estilo|arquitectura|base de datos|estrategia|tipo de cache|protocolo)\b.*\b(usar|uso|elegir|elijo|conviene|recomiendas?|deberia)\b", 3),
        (r"\b(me conviene|conviene mas|deberia usar|recomiendas?|elegir entre|que me sugieres|cual escojo|cual elegir)\b", 2),
        (r"\b(tengo|necesito|estoy disenando|mi sistema|nuestro sistema|una app|una aplicacion|un sistema)\b", 1),
    ],
    "conceptual": [
        (r"^[\s¿¡]*(que es|que son|que significa|define|defina|explica|explicame|en que consiste|para que sirve|como funciona)\b", 3),
        (r"\b(diferencia entre|concepto de|definicion de)\b", 2),
        (r"\b(adr|arc42|cap|cache-aside|write-through|sharding|cola de mensajes|back pressure|twelve-factor|12 factores|atam|iso 25010)\b", 1),
    ],
    "saludo": [
        (r"^[\s¿¡]*(hola|buenas|buenos dias|buenas tardes|buenas noches|hey|gracias|muchas gracias|ok|listo)\b[\s!.?]*$", 4),
        (r"\b(quien eres|que puedes hacer|como te uso|ayuda)\b", 3),
    ],
}

# Vocabulario del dominio: si la pregunta no contiene NINGUNO de estos términos y ninguna regla
# fuerte se activó, es candidata a fuera de dominio (lo confirma el modelo o el valor por defecto).
VOCABULARIO_DOMINIO = re.compile(
    r"\b(arquitect\w*|software|sistema|servicio\w*|microservicio\w*|monolit\w*|patron\w*|estilo|api|rest|rpc|base de datos|"
    r"cache|cola|mensaje\w*|evento\w*|disponibilidad|latencia|consistencia|escalab\w*|rendimiento|seguridad|"
    r"mantenib\w*|calidad|atributo\w*|despliegue|servidor\w*|balanceador|replica\w*|redundan\w*|adr|decision\w*|"
    r"componente\w*|modulo\w*|acoplamiento|cohesion|capa\w*|cliente|nube|cloud|contenedor\w*|docker|kubernetes|"
    r"sql|nosql|shard\w*|cap|12 factores|twelve|arc42|atam|iso|escenario\w*|falla\w*|sla|slo|uptime|cdn|dns|proxy|"
    r"balanceo|failover|replicacion|particion\w*|http|tcp|udp|grpc|graphql|endpoint\w*|backend|frontend|"
    r"despleg\w*|infraestructura|tolerancia|resiliencia|concurrencia|transaccion\w*|acid|indice\w*|"
    r"desnormaliz\w*|normaliz\w*|federacion|madr|logs?|config\w*|dependencia\w*|stakeholders?|"
    r"interfaz|interfaces|integracion|escalamiento|vertical|horizontal|nodo\w*|cluster|carga|"
    r"tabla\w*|datos|bases?|faiss|agente|embeddings?|rag|busqueda|vector\w*|llm|prompt\w*|fine-?tuning|"
    r"few-?shot|corpus|fragment\w*|trazas?|bot|telegram|qlora|lora|ollama|vps)\b"
)


@dataclass
class Clasificacion:
    tipo: str
    metodo: str                     # "reglas" | "llm" | "defecto"
    puntajes: dict = field(default_factory=dict)
    razon: str = ""

    def a_dict(self) -> dict:
        return {"tipo": self.tipo, "metodo": self.metodo, "puntajes": self.puntajes, "razon": self.razon}


def puntuar(pregunta: str) -> dict[str, int]:
    texto = normalizar(pregunta)
    return {tipo: sum(peso for patron, peso in reglas if re.search(patron, texto))
            for tipo, reglas in REGLAS.items()}


def clasificar_por_reglas(pregunta: str) -> Clasificacion | None:
    """Devuelve la clasificación si las reglas son concluyentes; si no, None."""
    puntajes = puntuar(pregunta)
    orden = sorted(puntajes.items(), key=lambda kv: kv[1], reverse=True)
    (primero, p1), (_, p2) = orden[0], orden[1]
    if p1 >= PUNTAJE_MINIMO and p1 - p2 >= MARGEN_MINIMO:
        return Clasificacion(primero, "reglas", puntajes, f"regla '{primero}' con {p1} puntos (siguiente {p2})")
    return None


def clasificar_con_llm(pregunta: str, cliente) -> Clasificacion | None:
    try:
        texto, _ = cliente.chat(
            [{"role": "system", "content": PROMPT_CLASIFICADOR}, {"role": "user", "content": pregunta}],
            temperatura=0.0, max_tokens=400, json=True,
        )
        datos = json.loads(_extraer_json(texto))
        tipo = str(datos.get("tipo", "")).strip().lower()
        if tipo in TIPOS:
            return Clasificacion(tipo, "llm", razon=str(datos.get("razon", ""))[:200])
    except Exception:  # noqa: BLE001 - cualquier fallo del modelo cae al valor por defecto
        return None
    return None


def _extraer_json(texto: str) -> str:
    m = re.search(r"\{.*\}", texto, re.S)
    return m.group(0) if m else texto


def clasificar(pregunta: str, cliente_llm=None) -> Clasificacion:
    """Punto de entrada: reglas -> LLM -> valor por defecto."""
    por_reglas = clasificar_por_reglas(pregunta)
    if por_reglas:
        return por_reglas
    puntajes = puntuar(pregunta)
    if cliente_llm is not None:
        por_llm = clasificar_con_llm(pregunta, cliente_llm)
        if por_llm:
            por_llm.puntajes = puntajes
            return por_llm
    # Llegamos aquí si las reglas no fueron concluyentes y el modelo no estaba o falló.
    sin_dominio = not VOCABULARIO_DOMINIO.search(normalizar(pregunta)) and max(puntajes.values()) == 0
    if sin_dominio:
        return Clasificacion("fuera_de_dominio", "defecto", puntajes, "sin reglas ni vocabulario del dominio")
    return Clasificacion("conceptual", "defecto", puntajes, "reglas no concluyentes y sin modelo; se consulta el corpus")
