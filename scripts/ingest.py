"""Construye el índice del RAG a partir de corpus/fuentes.yaml.

Uso:  python -m scripts.ingest                  (reindexa siempre)
      python -m scripts.ingest --si-cambio      (solo si el corpus o el backend cambiaron; lo usa Docker al arrancar)
      python -m scripts.ingest --backend tfidf
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter

from app.config import cargar_config
from app.rag.fragmentacion import fragmentar_corpus
from app.rag.indice import construir_indice


def huella(fragmentos) -> str:
    h = hashlib.sha256()
    for f in fragmentos:
        h.update(f.id.encode())
        h.update(f.texto.encode())
    return h.hexdigest()[:16]


def main() -> None:
    cfg = cargar_config()
    p = argparse.ArgumentParser()
    p.add_argument("--backend", default=cfg.embeddings_backend)
    p.add_argument("--si-cambio", action="store_true")
    args = p.parse_args()

    fragmentos, avisos = fragmentar_corpus(cfg.dir_corpus)
    for a in avisos:
        print("AVISO:", a)
    if not fragmentos:
        raise SystemExit("El corpus no produjo fragmentos.")
    hu = huella(fragmentos)

    meta_path = cfg.dir_indice / "meta.json"
    if args.si_cambio and meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("huella_corpus") == hu and meta.get("backend") == args.backend:
            print(f"Índice al día ({meta['fragmentos']} fragmentos); no se reindexa.")
            return

    meta = construir_indice(fragmentos, args.backend, cfg.embeddings_modelo, cfg.dir_indice,
                            cfg.dir_cache_modelos, hu)
    print(f"Índice listo en {cfg.dir_indice}: {meta}")
    for doc, n in sorted(Counter(f.doc_id for f in fragmentos).items()):
        print(f"  {doc:<12} {n:>4} fragmentos")


if __name__ == "__main__":
    main()
