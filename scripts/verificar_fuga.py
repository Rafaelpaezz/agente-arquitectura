"""Verifica la separación entre el banco/dataset y las preguntas de evaluación y comparación.

Procedimiento (se declara en el README):
  1. Las preguntas de evaluación y de comparación se escribieron PRIMERO, sobre secciones del
     corpus que se reservaron para evaluación (data/evaluacion/secciones_reservadas.json).
  2. El banco de ejemplos y el dataset de fine-tuning NO pueden usar esas secciones como fuente
     (lo comprueba scripts.validar_banco).
  3. Este script compara cada pregunta de evaluación/comparación contra TODAS las preguntas del banco
     con dos medidas: similitud coseno TF-IDF de palabras (1-2 gramas) y de caracteres (3-5 gramas).
     Si alguna supera el UMBRAL, la pregunta se marca para revisión manual y se reescribe.
  4. Se revisa a mano la tabla de las 3 preguntas del banco más parecidas a cada pregunta.

Uso: python -m scripts.verificar_fuga  ->  escribe evidencias/separacion_datos.md
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.agent.clasificador import normalizar
from app.agent.fewshot import cargar_banco
from app.config import RAIZ, cargar_config

UMBRAL = 0.60


def leer(ruta: Path) -> list[dict]:
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> int:
    cfg = cargar_config()
    banco = cargar_banco(cfg.dir_banco)
    dir_eval = cfg.dir_banco.parent / "evaluacion"
    pruebas = [("evaluación", d) for d in leer(dir_eval / "conjunto_evaluacion.jsonl")] + \
              [("comparación", d) for d in leer(dir_eval / "preguntas_comparacion.jsonl")]

    textos_banco = [normalizar(e.pregunta) for e in banco]
    textos_prueba = [normalizar(d["pregunta"]) for _, d in pruebas]
    sims = []
    for vect in (TfidfVectorizer(ngram_range=(1, 2)), TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))):
        vect.fit(textos_banco + textos_prueba)
        sims.append(cosine_similarity(vect.transform(textos_prueba), vect.transform(textos_banco)))

    filas, alertas = [], 0
    for i, (conjunto, d) in enumerate(pruebas):
        combinado = [max(sims[0][i][j], sims[1][i][j]) for j in range(len(banco))]
        top = sorted(range(len(banco)), key=lambda j: -combinado[j])[:3]
        maximo = combinado[top[0]]
        estado = "REVISAR" if maximo >= UMBRAL else "ok"
        alertas += estado == "REVISAR"
        mas_parecida = banco[top[0]]
        filas.append(f"| {d['id']} | {conjunto} | {d['pregunta'][:70]} | {mas_parecida.id}: {mas_parecida.pregunta[:60]} | "
                     f"{sims[0][i][top[0]]:.2f} | {sims[1][i][top[0]]:.2f} | {estado} |")

    salida = RAIZ / "evidencias" / "separacion_datos.md"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text("\n".join([
        "# Verificación de separación entre entrenamiento y evaluación",
        "",
        f"Banco/dataset: {len(banco)} preguntas. Preguntas de prueba: {len(pruebas)}. Umbral de alerta: {UMBRAL}.",
        "Medidas: coseno TF-IDF de palabras (1-2 gramas) y de caracteres (3-5 gramas), sobre texto en minúsculas y sin tildes.",
        "",
        "| Prueba | Conjunto | Pregunta | Pregunta del banco más parecida | Sim. palabras | Sim. caracteres | Estado |",
        "|---|---|---|---|---|---|---|",
        *filas,
        "",
        f"Resultado: {alertas} preguntas superan el umbral." if alertas else
        "Resultado: ninguna pregunta de evaluación o comparación supera el umbral de similitud con el banco.",
    ]) + "\n", encoding="utf-8")
    print(salida.read_text(encoding="utf-8"))
    return 1 if alertas else 0


if __name__ == "__main__":
    sys.exit(main())
