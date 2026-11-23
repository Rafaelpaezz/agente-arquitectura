"""Valida el banco de ejemplos.

Comprueba:
  1. Hay al menos 100 entradas y al menos 20 por cada tipo.
  2. Los ids son únicos y cada entrada tiene los campos obligatorios.
  3. Cada fuente citada existe en el índice (documento + sección).
  4. Ninguna fuente es una sección reservada para evaluación (data/evaluacion/secciones_reservadas.json).
  5. Las respuestas siguen el formato (Respuesta / Explicación / Fuentes) y los ejemplos de cálculo
     coinciden con lo que devuelve hoy la herramienta.

Uso: python -m scripts.validar_banco
"""
from __future__ import annotations

import json
import sys
from collections import Counter

from app.agent.fewshot import TIPOS_CON_BANCO, cargar_banco
from app.config import cargar_config
from app.tools.disponibilidad import calcular_disponibilidad


def main() -> int:
    cfg = cargar_config()
    banco = cargar_banco(cfg.dir_banco)
    errores = []

    conteo = Counter(e.tipo for e in banco)
    if len(banco) < 100:
        errores.append(f"el banco tiene {len(banco)} entradas (mínimo 100)")
    for t in TIPOS_CON_BANCO:
        if conteo[t] < 20:
            errores.append(f"el tipo '{t}' tiene {conteo[t]} ejemplos (mínimo 20)")

    ids = Counter(e.id for e in banco)
    errores += [f"id repetido: {i}" for i, n in ids.items() if n > 1]

    secciones = set()
    with open(cfg.dir_indice / "fragmentos.jsonl", encoding="utf-8") as f:
        for linea in f:
            d = json.loads(linea)
            secciones.add((d["doc_id"], d["seccion"]))
    reservadas = {(s["doc"], s["seccion"]) for s in json.loads(
        (cfg.dir_banco.parent / "evaluacion" / "secciones_reservadas.json").read_text(encoding="utf-8"))["secciones"]}

    for e in banco:
        if not e.fuentes:
            errores.append(f"{e.id}: no tiene fuentes")
        for fu in e.fuentes:
            clave = (fu["doc"], fu["seccion"])
            if clave not in secciones:
                errores.append(f"{e.id}: la fuente {clave} no existe en el índice")
            if clave in reservadas:
                errores.append(f"{e.id}: usa la sección reservada {clave} (fuga de datos)")
        for etiqueta in ("**Respuesta:**", "**Explicación:**", "**Fuentes:**"):
            if etiqueta not in e.respuesta:
                errores.append(f"{e.id}: falta '{etiqueta}' en la respuesta")
        if e.tipo == "calculo":
            r = calcular_disponibilidad(e.expresion)
            if f"{r['disponibilidad_pct']:.4f} %" not in e.respuesta:
                errores.append(f"{e.id}: el número de la respuesta no coincide con la herramienta")

    print(f"Banco: {len(banco)} ejemplos -> " + ", ".join(f"{t}: {conteo[t]}" for t in TIPOS_CON_BANCO))
    if errores:
        print("\n".join("ERROR: " + e for e in errores))
        return 1
    print("OK: el banco cumple todas las validaciones.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
