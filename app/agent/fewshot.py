"""Few-shot dinámico: en cada consulta se eligen ejemplos resueltos del banco y se insertan en el prompt.

Criterio por defecto (exigido por el enunciado): CLASIFICACIÓN.
  1. El clasificador decide el tipo de la pregunta.
  2. Se toman solo los ejemplos de ese tipo (data/banco_ejemplos/<tipo>.jsonl).
  3. Dentro del tipo se ordenan por solapamiento de palabras clave con la pregunta (Jaccard),
     así los ejemplos cambian de una pregunta a otra. Empates: por id, para que sea determinista.
  4. Se agregan las instrucciones especializadas del tipo.

Criterio alternativo (para comparar): SIMILITUD vectorial entre la pregunta y TODAS las preguntas
del banco, sin mirar el tipo. Usa el mismo modelo de embeddings del RAG.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.agent.clasificador import normalizar
from app.agent.prompts import INSTRUCCIONES_POR_TIPO
from app.tools.disponibilidad import calcular_disponibilidad, resumen_texto

TIPOS_CON_BANCO = ("conceptual", "seleccion", "calculo", "compromisos")
MAX_CARACTERES_FRAGMENTO_EJEMPLO = 600

_VACIAS = set("""a al algo como con cual cuales de del el en entre es esta este esto ese eso hay la las lo los me mi
mas muy no o para pero por que se si sin sobre su sus te tu un una uno unos y ya yo usar uso cuando donde quien
debo deberia puedo puede tiene tienen tengo ser son fue sea""".split())


def palabras_clave(texto: str) -> set[str]:
    return {p for p in re.findall(r"[a-z0-9]+", normalizar(texto)) if len(p) > 2 and p not in _VACIAS}


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


@dataclass
class Ejemplo:
    id: str
    tipo: str
    pregunta: str
    respuesta: str
    fuentes: list[dict]
    expresion: str | None = None


def cargar_banco(dir_banco: Path) -> list[Ejemplo]:
    banco = []
    for archivo in sorted(dir_banco.glob("*.jsonl")):
        with open(archivo, encoding="utf-8") as f:
            for linea in f:
                if linea.strip():
                    d = json.loads(linea)
                    banco.append(Ejemplo(d["id"], d["tipo"], d["pregunta"], d["respuesta"],
                                         d.get("fuentes", []), d.get("expresion")))
    return banco


def mensaje_usuario(pregunta: str, contexto: str, resultado_herramienta: str | None) -> str:
    """Formato ÚNICO del mensaje de usuario. Lo usan la consulta real, los ejemplos y el dataset de fine-tuning."""
    partes = [f"FRAGMENTOS:\n{contexto or '(no se recuperaron fragmentos)'}"]
    if resultado_herramienta:
        partes.append(f"RESULTADO DE LA HERRAMIENTA:\n{resultado_herramienta}")
    partes.append(f"PREGUNTA: {pregunta}")
    return "\n\n".join(partes)


class SelectorEjemplos:
    def __init__(self, banco: list[Ejemplo], fragmentos: list, embedder=None):
        self.banco = banco
        self.por_tipo = {t: [e for e in banco if e.tipo == t] for t in TIPOS_CON_BANCO}
        self._claves = {e.id: palabras_clave(e.pregunta) for e in banco}
        # índice (doc_id, seccion) -> fragmentos, para reconstruir el contexto de cada ejemplo
        self._por_seccion: dict[tuple[str, str], list] = {}
        for f in fragmentos:
            self._por_seccion.setdefault((f.doc_id, f.seccion), []).append(f)
        self._embedder = embedder
        self._vectores = None

    # --- criterio 1: clasificación ----------------------------------------
    def por_clasificacion(self, pregunta: str, tipo: str, k: int) -> list[Ejemplo]:
        candidatos = self.por_tipo.get(tipo, [])
        claves = palabras_clave(pregunta)
        return sorted(candidatos, key=lambda e: (-jaccard(claves, self._claves[e.id]), e.id))[:k]

    # --- criterio 2: similitud vectorial ----------------------------------
    def por_similitud(self, pregunta: str, k: int) -> list[Ejemplo]:
        if self._embedder is None:
            raise RuntimeError("El criterio de similitud necesita un modelo de embeddings")
        if self._vectores is None:
            # Pregunta contra pregunta: se usa el mismo modo "consulta" en ambos lados.
            self._vectores = np.vstack([self._embedder.consulta(e.pregunta) for e in self.banco])
        q = self._embedder.consulta(pregunta)[0]
        orden = np.argsort(-(self._vectores @ q))[:k]
        return [self.banco[i] for i in orden]

    def seleccionar(self, pregunta: str, tipo: str, k: int, criterio: str = "clasificacion") -> list[Ejemplo]:
        if tipo not in TIPOS_CON_BANCO:
            return []
        if criterio == "similitud":
            return self.por_similitud(pregunta, k)
        return self.por_clasificacion(pregunta, tipo, k)

    # --- armado de mensajes -------------------------------------------------
    def contexto_de(self, ej: Ejemplo, max_caracteres: int | None = MAX_CARACTERES_FRAGMENTO_EJEMPLO) -> str:
        bloques = []
        for fuente in ej.fuentes:
            for f in self._por_seccion.get((fuente["doc"], fuente["seccion"]), [])[:2]:
                texto = f.texto if max_caracteres is None else f.texto[:max_caracteres]
                bloques.append(f"<<FRAGMENTO cita=\"{f.cita()}\" documento=\"{f.doc_titulo}\">>\n{texto}\n<<FIN>>")
        return "\n\n".join(bloques)

    def mensajes_de(self, ejemplos: list[Ejemplo]) -> list[dict]:
        mensajes = []
        for ej in ejemplos:
            herramienta = resumen_texto(calcular_disponibilidad(ej.expresion)) if ej.expresion else None
            mensajes.append({"role": "user", "content": mensaje_usuario(ej.pregunta, self.contexto_de(ej), herramienta)})
            mensajes.append({"role": "assistant", "content": ej.respuesta})
        return mensajes


def instrucciones_de(tipo: str) -> str:
    return INSTRUCCIONES_POR_TIPO.get(tipo, "")
