"""Construye el dataset de fine-tuning (Ruta 1) a partir del banco de ejemplos.

Cada ejemplo se convierte en una conversación con EXACTAMENTE el formato que verá el modelo en
producción (mismo prompt de sistema, mismo mensaje de usuario con fragmentos y resultado de la
herramienta). Para que el modelo aprenda a elegir y citar el fragmento correcto, al contexto se le
agregan 2 fragmentos distractores (de secciones NO reservadas) y se mezcla el orden.

El fine-tuning enseña la FORMA de la respuesta (estructura, citas, uso del resultado de la
herramienta), no el contenido: el contenido siempre viene de los fragmentos.

Uso: python -m scripts.construir_dataset_finetune
Salida: data/finetune/train.jsonl, data/finetune/validacion.jsonl (formato "messages" de chat)
"""
from __future__ import annotations

import json
import random

from app.agent.fewshot import cargar_banco, mensaje_usuario
from app.agent.prompts import PROMPT_SISTEMA
from app.config import cargar_config
from app.rag.fragmentacion import Fragmento
from app.tools.disponibilidad import calcular_disponibilidad, resumen_texto

DISTRACTORES = 2
PROPORCION_VALIDACION = 0.1
SEMILLA = 2026


def bloque(f: Fragmento) -> str:
    return f"<<FRAGMENTO cita=\"{f.cita()}\" documento=\"{f.doc_titulo}\">>\n{f.texto}\n<<FIN>>"


def main() -> None:
    cfg = cargar_config()
    rnd = random.Random(SEMILLA)
    with open(cfg.dir_indice / "fragmentos.jsonl", encoding="utf-8") as f:
        fragmentos = [Fragmento(**json.loads(l)) for l in f]
    reservadas = {(s["doc"], s["seccion"]) for s in json.loads(
        (cfg.dir_banco.parent / "evaluacion" / "secciones_reservadas.json").read_text(encoding="utf-8"))["secciones"]}
    por_seccion: dict[tuple[str, str], list[Fragmento]] = {}
    for fr in fragmentos:
        por_seccion.setdefault((fr.doc_id, fr.seccion), []).append(fr)
    permitidos = [fr for fr in fragmentos if (fr.doc_id, fr.seccion) not in reservadas]

    filas = []
    for ej in cargar_banco(cfg.dir_banco):
        # Todos los fragmentos (máx. 3) de cada sección fuente: una sección larga puede venir partida.
        relevantes = [fr for fu in ej.fuentes for fr in por_seccion[(fu["doc"], fu["seccion"])][:3]]
        claves = {(f.doc_id, f.seccion) for f in relevantes}
        otros = [f for f in permitidos if (f.doc_id, f.seccion) not in claves]
        contexto = relevantes + rnd.sample(otros, DISTRACTORES)
        rnd.shuffle(contexto)
        herramienta = resumen_texto(calcular_disponibilidad(ej.expresion)) if ej.expresion else None
        filas.append({"id": ej.id, "tipo": ej.tipo, "messages": [
            {"role": "system", "content": PROMPT_SISTEMA},
            {"role": "user", "content": mensaje_usuario(ej.pregunta, "\n\n".join(bloque(f) for f in contexto), herramienta)},
            {"role": "assistant", "content": ej.respuesta},
        ]})

    # División estratificada por tipo: el 10 % de cada tipo va a validación.
    rnd.shuffle(filas)
    train, val = [], []
    for tipo in sorted({f["tipo"] for f in filas}):
        del_tipo = [f for f in filas if f["tipo"] == tipo]
        n_val = max(1, round(len(del_tipo) * PROPORCION_VALIDACION))
        val += del_tipo[:n_val]
        train += del_tipo[n_val:]

    salida = cfg.dir_banco.parent / "finetune"
    salida.mkdir(parents=True, exist_ok=True)
    for nombre, datos in (("train", train), ("validacion", val)):
        with open(salida / f"{nombre}.jsonl", "w", encoding="utf-8") as f:
            for fila in datos:
                f.write(json.dumps(fila, ensure_ascii=False) + "\n")
    print(f"train: {len(train)} · validación: {len(val)} · total: {len(filas)} -> {salida}")


if __name__ == "__main__":
    main()
