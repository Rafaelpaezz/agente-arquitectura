"""Ejecuta un guion de 12 conversaciones contra el agente real y guarda sus trazas como evidencia.

Incluye a propósito casos que obligan al agente a corregir su decisión:
  - DEMO-05: "¿Cómo se calcula la disponibilidad en serie?" -> las reglas la clasifican como
    'calculo' (palabras "calcula" y "en serie"), pero no trae números: la verificación la corrige a 'rag'.
  - DEMO-06: una pregunta conceptual que contiene una expresión explícita -> se corrige a 'herramienta'.
  - DEMO-07: una topología mal escrita -> la herramienta valida la entrada y responde el error.

Uso (en el VPS, con el .env configurado):  python -m scripts.generar_trazas_demo
Salida: evidencias/trazas/trazas_demo.jsonl y evidencias/trazas/trazas_demo.md
"""
from __future__ import annotations

import json

from app.config import RAIZ
from app.fabrica import construir_agente

GUION = [
    ("DEMO-01", "Hola, ¿qué puedes hacer?"),
    ("DEMO-02", "¿Qué es el patrón write-through?"),
    ("DEMO-03", "Necesito servir archivos estáticos a usuarios de varios continentes, ¿qué me recomiendas?"),
    ("DEMO-04", "¿Qué se gana y qué se pierde al desnormalizar una base de datos?"),
    ("DEMO-05", "¿Cómo se calcula la disponibilidad en serie?"),
    ("DEMO-06", "Explícame qué significa serie(api=99.9%, bd=99.95%)"),
    ("DEMO-07", "serie(api=99.9%, paralelo(bd1=99.5%, bd2=99.5%)"),
    ("DEMO-08", "Tengo un balanceador de 99.99%, tres servidores de 99.5% en paralelo y una base de datos de 99.9%. ¿Qué disponibilidad tengo?"),
    ("DEMO-09", "¿Por qué el agente usa FAISS con búsqueda exacta?"),
    ("DEMO-10", "¿Cuál es la capital de Francia?"),
    ("DEMO-11", "¿Qué es la computación cuántica topológica de Majorana?"),
    ("DEMO-12", "¿Qué debe ir en la sección de riesgos y deuda técnica de arc42?"),
]


def main() -> None:
    agente = construir_agente()
    destino = RAIZ / "evidencias" / "trazas"
    destino.mkdir(parents=True, exist_ok=True)
    md = ["# Trazas de demostración", ""]
    with open(destino / "trazas_demo.jsonl", "w", encoding="utf-8") as f:
        for id_, pregunta in GUION:
            turno = agente.responder(pregunta, chat_id="demo")
            datos = {"demo": id_, **turno.traza.datos}
            f.write(json.dumps(datos, ensure_ascii=False) + "\n")
            correcciones = [p for p in datos["pasos"] if p["paso"] == "corregir"]
            md += [f"## {id_}: {pregunta}", "",
                   f"- Clasificación: **{datos['pasos'][0]['tipo']}** (método: {datos['pasos'][0]['metodo']})",
                   f"- Acción final: **{datos['accion_final']}**",
                   *(f"- Corrección: {c['de']} → {c['a']} ({c['motivo']})" for c in correcciones),
                   "", "```", turno.traza.resumen_legible(), "```", "",
                   "<details><summary>Respuesta</summary>", "", turno.respuesta, "", "</details>", ""]
            print(f"{id_}: {datos['accion_final']}")
    (destino / "trazas_demo.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Listo: {destino}")


if __name__ == "__main__":
    main()
