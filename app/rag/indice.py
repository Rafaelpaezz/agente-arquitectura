"""Índice vectorial (FAISS) y recuperación de fragmentos con su cita."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np

from app.rag.embeddings import crear_embedder
from app.rag.fragmentacion import Fragmento


@dataclass
class Resultado:
    fragmento: Fragmento
    puntaje: float     # similitud coseno en [-1, 1]
    posicion: int      # 1 = el más parecido


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

    def buscar(self, consulta: str, k: int = 5) -> list[Resultado]:
        vector = self.embedder.consulta(consulta)
        puntajes, ids = self.indice.search(vector, k)
        return [Resultado(self.fragmentos[i], float(p), pos + 1)
                for pos, (p, i) in enumerate(zip(puntajes[0], ids[0])) if i >= 0]


def contexto_para_prompt(resultados: list[Resultado]) -> str:
    """Bloque de fragmentos numerados que se le entrega al modelo redactor."""
    bloques = []
    for r in resultados:
        f = r.fragmento
        bloques.append(f"<<FRAGMENTO cita=\"{f.cita()}\" documento=\"{f.doc_titulo}\">>\n{f.texto}\n<<FIN>>")
    return "\n\n".join(bloques)
