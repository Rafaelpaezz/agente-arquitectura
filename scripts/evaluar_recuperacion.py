"""Evalúa la recuperación del RAG con el conjunto de evaluación.

Para cada pregunta se recuperan los k primeros fragmentos y se mira si alguno pertenece al documento
y a la sección esperados (o a una subsección de ella). Reporta acierto@1, @3, @k y MRR.

Uso: python -m scripts.evaluar_recuperacion [--k 5]  ->  evidencias/recuperacion_top_k.md
"""
from __future__ import annotations

import argparse
import json

from app.config import RAIZ, cargar_config
from app.rag.indice import Recuperador


# Preguntas que NO están cubiertas por el corpus: sirven para calibrar RAG_MIN_SCORE.
FUERA_DEL_CORPUS = [
    "¿Cuál es la receta tradicional del ajiaco santafereño?",
    "¿Quién ganó el mundial de fútbol de 2014?",
    "¿Cómo se calcula la derivada de un logaritmo natural?",
    "¿Qué es la computación cuántica topológica de Majorana?",
    "¿Cuál es la capital de Australia?",
]


def coincide(fragmento, fuente: dict) -> bool:
    return fragmento.doc_id == fuente["doc"] and (
        fragmento.seccion == fuente["seccion"] or fragmento.seccion.startswith(fuente["seccion"] + " > "))


def main() -> None:
    cfg = cargar_config()
    p = argparse.ArgumentParser()
    p.add_argument("--k", type=int, default=cfg.rag_k)
    args = p.parse_args()

    rec = Recuperador(cfg.dir_indice, cfg.embeddings_backend, cfg.embeddings_modelo, cfg.dir_cache_modelos)
    preguntas = [json.loads(l) for l in (cfg.dir_banco.parent / "evaluacion" / "conjunto_evaluacion.jsonl")
                 .read_text(encoding="utf-8").splitlines() if l.strip()]

    filas, a1, a3, ak, rr = [], 0, 0, 0, 0.0
    for d in preguntas:
        res = rec.buscar(d["pregunta"], args.k)
        pos = next((r.posicion for r in res if coincide(r.fragmento, d["fuente"])), None)
        a1 += pos == 1
        a3 += pos is not None and pos <= 3
        ak += pos is not None
        rr += 1 / pos if pos else 0
        primero = res[0].fragmento.cita() if res else "-"
        filas.append(f"| {d['id']} | {d['pregunta'][:60]} | {d['fuente']['doc']} §{d['fuente']['seccion'][-45:]} | "
                     f"{pos or 'no'} | {res[0].puntaje:.3f} | {primero[:60]} |")

    n = len(preguntas)
    # Calibración del umbral: puntaje del 1.º fragmento en preguntas fuera del corpus vs. aciertos
    # La compuerta de evidencia usa el mejor puntaje semántico de la consulta.
    fuera = [rec.mejor_puntaje(q) for q in FUERA_DEL_CORPUS]
    dentro = [rec.mejor_puntaje(d["pregunta"]) for d in preguntas]
    min_acierto = min(dentro)
    sugerido = (max(fuera) + min_acierto) / 2
    salida = RAIZ / "evidencias" / "recuperacion_top_k.md"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text("\n".join([
        "# Evaluación de la recuperación (RAG)",
        "",
        f"Modelo de embeddings: {rec.meta['modelo']} ({rec.meta['backend']}). Fragmentos indexados: {rec.meta['fragmentos']}. "
        f"**k = {args.k}**.",
        "Ranking: similitud semántica + bono por términos de la pregunta en el título de la sección (máx. 0,16).",
        "Acierto: alguno de los k fragmentos recuperados pertenece al documento y sección esperados (o a una subsección).",
        "",
        "| Métrica | Valor |",
        "|---|---|",
        f"| Preguntas | {n} |",
        f"| Fragmento correcto en la posición 1 | {a1} de {n} ({a1 / n:.0%}) |",
        f"| Fragmento correcto entre los 3 primeros | {a3} de {n} ({a3 / n:.0%}) |",
        f"| **Fragmento correcto entre los {args.k} primeros** | **{ak} de {n} ({ak / n:.0%})** |",
        f"| MRR@{args.k} | {rr / n:.3f} |",
        "",
        "## Calibración del umbral (RAG_MIN_SCORE)",
        "",
        f"* Puntaje máximo del 1.º fragmento en {len(FUERA_DEL_CORPUS)} preguntas fuera del corpus: **{max(fuera):.3f}**",
        f"* Mejor puntaje mínimo entre las {n} preguntas del conjunto de evaluación: **{min_acierto:.3f}**",
        f"* Umbral configurado: {cfg.rag_umbral:.2f} · umbral sugerido (punto medio): **{sugerido:.2f}**",
        "",
        "| Id | Pregunta | Fuente esperada | Posición del correcto | Puntaje del 1.º | 1.º recuperado |",
        "|---|---|---|---|---|---|",
        *filas,
    ]) + "\n", encoding="utf-8")
    print(salida.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
