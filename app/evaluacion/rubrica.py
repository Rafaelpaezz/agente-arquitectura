"""Rúbrica automática de la comparación. Implementa el criterio declarado en docs/criterio_comparacion.md.

Mide FORMA, no conocimiento: formato, estructura, uso correcto de la herramienta y citación.
Cada criterio vale 0 o 1; el de herramienta solo aplica a preguntas de cálculo.
"""
from __future__ import annotations

import re

ETIQUETAS = ("**Respuesta:**", "**Explicación:**", "**Fuentes:**")
_CITA = re.compile(r"\[[A-Z0-9][A-Z0-9\-]*, (?:§[^\]]+|p\. \d+)\]")


def _seccion(texto: str, etiqueta: str, siguiente: str | None) -> str:
    ini = texto.find(etiqueta)
    if ini < 0:
        return ""
    ini += len(etiqueta)
    fin = texto.find(siguiente, ini) if siguiente else -1
    return texto[ini:fin if fin >= 0 else None].strip()


def formato(texto: str) -> int:
    """C1. Las tres etiquetas aparecen, cada una una vez y en orden."""
    pos = [texto.find(e) for e in ETIQUETAS]
    return int(all(p >= 0 for p in pos) and pos == sorted(pos) and all(texto.count(e) == 1 for e in ETIQUETAS))


def estructura(texto: str) -> int:
    """C2. La respuesta directa tiene a lo sumo 2 oraciones / 60 palabras y la explicación de 2 a 5 viñetas."""
    directa = _seccion(texto, ETIQUETAS[0], ETIQUETAS[1])
    explic = _seccion(texto, ETIQUETAS[1], ETIQUETAS[2])
    oraciones = len([o for o in re.split(r"(?<=[.!?])\s+", directa) if o.strip()])
    vinetas = len(re.findall(r"^\s*[-•*]\s+", explic, re.M))
    return int(bool(directa) and oraciones <= 2 and len(directa.split()) <= 60 and 2 <= vinetas <= 5)


def herramienta(texto: str, resultado: dict | None) -> int | None:
    """C3. (solo cálculo) La respuesta trae la disponibilidad que dio la herramienta (2 decimales en %)
    y nombra los puntos únicos de falla (o dice que no hay)."""
    if resultado is None:
        return None
    valor = resultado["disponibilidad_pct"]
    candidatos = {f"{valor:.2f}", f"{valor:.3f}", f"{valor:.4f}", f"{valor:.2f}".replace(".", ",")}
    tiene_numero = any(c in texto for c in candidatos)
    spof = resultado["puntos_unicos_de_falla"]
    t = texto.lower()
    nombra_spof = all(n.lower() in t for n in spof) if spof else ("ninguno" in t or "no hay" in t or "no quedan" in t)
    return int(tiene_numero and nombra_spof)


def citacion(texto: str, citas_permitidas: set[str]) -> int:
    """C4. Hay al menos una cita y todas corresponden a fragmentos que se le entregaron al modelo."""
    usadas = set(_CITA.findall(texto))
    return int(bool(usadas) and usadas <= citas_permitidas)


def calificar(texto: str, citas_permitidas: set[str], resultado_herramienta: dict | None) -> dict:
    c = {"formato": formato(texto), "estructura": estructura(texto),
         "herramienta": herramienta(texto, resultado_herramienta), "citacion": citacion(texto, citas_permitidas)}
    aplicables = [v for v in c.values() if v is not None]
    c["puntaje"] = round(sum(aplicables) / len(aplicables), 3)
    return c
