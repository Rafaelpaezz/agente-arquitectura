"""Índice vectorial (FAISS) y recuperación de fragmentos con su cita."""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np

from app.rag.embeddings import crear_embedder
from app.rag.fragmentacion import Fragmento


@dataclass
class Resultado:
    fragmento: Fragmento
    puntaje: float       # similitud coseno semántica (embeddings) en [-1, 1]; la usa el umbral
    posicion: int        # 1 = el más relevante
    bono: float = 0.0    # bono por términos de la pregunta presentes en el título de la sección


# Bono por cada término de la pregunta que aparece en la ruta de secciones del fragmento
# (p. ej. "write-through" en "Cache > When to update the cache > Write-through").
# Los embeddings multilingües diluyen los términos técnicos en inglés dentro de una pregunta en
# español; el título de la sección es la señal más precisa de qué trata el fragmento.
BONO_POR_TERMINO = 0.08
BONO_MAXIMO = 0.16
_VACIAS = set("""para como cual cuales donde cuando entre sobre esta este esto estos estas tiene tienen
debo deberia puede pueden hace hacer usar uso sirve sirven funciona significa explica explicame dime
que qué cómo cuál porque desde hasta segun según patron patrón sistema""".split())


def _terminos(texto: str) -> set[str]:
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return {t for t in re.findall(r"[a-z0-9][a-z0-9\-]+", texto) if len(t) >= 4 and t not in _VACIAS}


def construir_indice(fragmentos: list[Fragmento], backend: str, modelo: str, dir_indice: Path,
                     cache: Path | None = None, huella: str = "") -> dict:
    dir_indice.mkdir(parents=True, exist_ok=True)
    embedder = crear_embedder(backend, modelo, dir_indice, cache)
    vectores = embedder.documentos([f.para_embedding() for f in fragmentos])
    # IndexFlatIP: búsqueda exacta por producto interno. Con unos cientos o miles de fragmentos
    # es instantánea y no requiere entrenar ni ajustar parámetros (ver ADR 0002).
    indice = faiss.IndexFlatIP(vectores.shape[1])
    indice.add(vectores)
    faiss.write_index(indice, str(dir_indice / "faiss.index"))
    with open(dir_indice / "fragmentos.jsonl", "w", encoding="utf-8") as f:
        for frag in fragmentos:
            f.write(json.dumps(frag.a_dict(), ensure_ascii=False) + "\n")
    meta = {"backend": backend, "modelo": embedder.nombre, "dimension": int(vectores.shape[1]),
            "fragmentos": len(fragmentos), "huella_corpus": huella}
    (dir_indice / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


class Recuperador:
    def __init__(self, dir_indice: Path, backend: str, modelo: str, cache: Path | None = None):
        if not (dir_indice / "faiss.index").exists():
            raise FileNotFoundError(f"No hay índice en {dir_indice}. Ejecute: python -m scripts.ingest")
        meta = json.loads((dir_indice / "meta.json").read_text(encoding="utf-8"))
        if meta["backend"] != backend:
            raise RuntimeError(f"El índice se construyó con '{meta['backend']}' y la config pide '{backend}'. Reindexe.")
        self.meta = meta
        self.indice = faiss.read_index(str(dir_indice / "faiss.index"))
        with open(dir_indice / "fragmentos.jsonl", encoding="utf-8") as f:
            self.fragmentos = [Fragmento(**json.loads(l)) for l in f]
        self.embedder = crear_embedder(backend, modelo, dir_indice, cache)
        self._titulos = [_terminos(f.seccion) for f in self.fragmentos]

    def buscar(self, consulta: str, k: int = 5) -> list[Resultado]:
        """1. Similitud semántica (coseno de embeddings) contra TODOS los fragmentos.
        2. Bono si términos de la pregunta aparecen en el título de la sección (máx. 0,16).
        3. Se ordena por semántica + bono y se devuelven los k primeros.
        El puntaje reportado sigue siendo el semántico puro (ver ADR 0002)."""
        n = len(self.fragmentos)
        sem, ids = self.indice.search(self.embedder.consulta(consulta), n)
        terminos = _terminos(consulta)
        candidatos = []
        for p, i in zip(sem[0], ids[0]):
            bono = min(BONO_MAXIMO, BONO_POR_TERMINO * len(terminos & self._titulos[i]))
            candidatos.append((float(p) + bono, float(p), bono, int(i)))
        candidatos.sort(key=lambda c: -c[0])
        return [Resultado(self.fragmentos[i], p, pos + 1, bono)
                for pos, (_, p, bono, i) in enumerate(candidatos[:k])]

    def mejor_puntaje(self, consulta: str) -> float:
        """Similitud semántica del fragmento más parecido: decide si hay evidencia en el corpus."""
        sem, _ = self.indice.search(self.embedder.consulta(consulta), 1)
        return float(sem[0][0])


def contexto_para_prompt(resultados: list[Resultado]) -> str:
    """Bloque de fragmentos numerados que se le entrega al modelo redactor."""
    bloques = []
    for r in resultados:
        f = r.fragmento
        bloques.append(f"<<FRAGMENTO cita=\"{f.cita()}\" documento=\"{f.doc_titulo}\">>\n{f.texto}\n<<FIN>>")
    return "\n\n".join(bloques)
