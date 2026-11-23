"""Comparación de las dos versiones del agente sobre las 10 preguntas de comparación.

  --modo fewshot   (Ruta 2) mismo modelo, versión A = SIN banco de ejemplos, versión B = CON banco.
  --modo modelo    (Ruta 1) sin banco en ambas, versión A = modelo base, versión B = modelo ajustado.
                   Requiere --modelo-base y --modelo-ajustado (nombres en Ollama o en la API).

Garantías de las condiciones (enunciado): las dos versiones reciben las mismas preguntas, el mismo
prompt de sistema, la MISMA clasificación y los MISMOS fragmentos (la versión A recupera y la B
reutiliza exactamente esos fragmentos). Solo varía el elemento evaluado.

Uso:
  python -m scripts.comparar --modo fewshot
  python -m scripts.comparar --modo modelo --modelo-base qwen2.5:3b-instruct --modelo-ajustado arqui-qwen2.5-3b-ft
Salida: evidencias/comparacion_<modo>.md y evidencias/comparacion_<modo>.jsonl
"""
from __future__ import annotations

import argparse
import copy
import json
import platform
import statistics
from dataclasses import replace

from app.agent.clasificador import Clasificacion
from app.config import RAIZ, cargar_config
from app.evaluacion.rubrica import calificar
from app.fabrica import construir_agente
from app.llm import ClienteLLM
from app.tools.disponibilidad import calcular_disponibilidad


def clasificacion_de(turno) -> Clasificacion:
    p = turno.traza.datos["pasos"][0]
    return Clasificacion(p["tipo"], p["metodo"], p.get("puntajes", {}), p.get("razon", ""))


def resultado_herramienta(turno) -> dict | None:
    for p in turno.traza.datos["pasos"]:
        if p["paso"] == "herramienta" and "expresion" in p and "error" not in p:
            return calcular_disponibilidad(p["expresion"])
    return None


def info_maquina() -> str:
    try:
        cpus = open("/proc/cpuinfo").read().count("processor\t:")
        mem = int(open("/proc/meminfo").readline().split()[1]) // 1024
        modelo_cpu = next((l.split(":")[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")), "")
        return f"{platform.node()} · {cpus} vCPU ({modelo_cpu}) · {mem} MB RAM · {platform.platform()}"
    except OSError:
        return platform.platform()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--modo", choices=["fewshot", "modelo"], required=True)
    p.add_argument("--modelo-base")
    p.add_argument("--modelo-ajustado")
    args = p.parse_args()
    cfg = cargar_config()

    if args.modo == "fewshot":
        agente_a = agente_b = construir_agente(cfg)
        nombres = ("sin ejemplos", "con ejemplos")
        fewshot = (False, True)
    else:
        if not (args.modelo_base and args.modelo_ajustado):
            raise SystemExit("--modo modelo requiere --modelo-base y --modelo-ajustado")
        agente_a = construir_agente(cfg, cliente_redaccion=ClienteLLM(replace(cfg.redaccion, modelo=args.modelo_base)))
        agente_b = copy.copy(agente_a)   # mismo índice, mismo clasificador; solo cambia el modelo redactor
        agente_b.cliente_redaccion = ClienteLLM(replace(cfg.redaccion, modelo=args.modelo_ajustado))
        nombres = (f"base: {args.modelo_base}", f"ajustado: {args.modelo_ajustado}")
        fewshot = (False, False)

    preguntas = [json.loads(l) for l in (cfg.dir_banco.parent / "evaluacion" / "preguntas_comparacion.jsonl")
                 .read_text(encoding="utf-8").splitlines() if l.strip()]

    registros, filas = [], []
    for q in preguntas:
        ta = agente_a.responder(q["pregunta"], chat_id="comparacion", fewshot=fewshot[0])
        tb = agente_b.responder(q["pregunta"], chat_id="comparacion", fewshot=fewshot[1],
                                fragmentos_fijos=ta.fragmentos, clasificacion_fija=clasificacion_de(ta))
        permitidas = {r.fragmento.cita() for r in ta.fragmentos}
        herr = resultado_herramienta(ta)
        ca, cb = calificar(ta.respuesta, permitidas, herr), calificar(tb.respuesta, permitidas, herr)
        la = ta.traza.datos["latencias_s"].get("redaccion")
        lb = tb.traza.datos["latencias_s"].get("redaccion")
        registros.append({"id": q["id"], "pregunta": q["pregunta"], "tipo": ta.tipo, "accion": ta.accion,
                          "fragmentos": sorted(permitidas), "A": {"version": nombres[0], "respuesta": ta.respuesta,
                          "rubrica": ca, "latencia_s": la, "traza": ta.traza.datos["id"]},
                          "B": {"version": nombres[1], "respuesta": tb.respuesta, "rubrica": cb, "latencia_s": lb,
                                "traza": tb.traza.datos["id"]}})
        fmt = lambda c: " / ".join("–" if c[k] is None else str(c[k]) for k in ("formato", "estructura", "herramienta", "citacion"))
        filas.append(f"| {q['id']} | {ta.tipo} | {fmt(ca)} | {ca['puntaje']:.2f} | {fmt(cb)} | {cb['puntaje']:.2f} | "
                     f"{la or 0:.1f} | {lb or 0:.1f} |")
        print(q["id"], ca["puntaje"], cb["puntaje"])

    def promedio(v, clave):
        valores = [r[v][clave] for r in registros if r[v][clave] is not None]
        return statistics.mean(valores) if valores else 0.0

    def prom_crit(v, k):
        valores = [r[v]["rubrica"][k] for r in registros if r[v]["rubrica"][k] is not None]
        return f"{sum(valores)}/{len(valores)}" if valores else "–"

    base = RAIZ / "evidencias" / f"comparacion_{args.modo}"
    base.parent.mkdir(parents=True, exist_ok=True)
    with open(base.with_suffix(".jsonl"), "w", encoding="utf-8") as f:
        for r in registros:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    pa = statistics.mean(r["A"]["rubrica"]["puntaje"] for r in registros)
    pb = statistics.mean(r["B"]["rubrica"]["puntaje"] for r in registros)
    base.with_suffix(".md").write_text("\n".join([
        f"# Comparación ({args.modo}): A = {nombres[0]} · B = {nombres[1]}",
        "",
        "Criterio declarado antes de medir: docs/criterio_comparacion.md. Cada celda: formato / estructura / herramienta / citación (– = no aplica).",
        f"Máquina: {info_maquina()}",
        f"Modelo de clasificación: {cfg.decision.modelo}. Prompt de sistema: idéntico en A y B. Fragmentos: idénticos en A y B.",
        "",
        "| Id | Tipo | A: criterios | A: puntaje | B: criterios | B: puntaje | A: latencia (s) | B: latencia (s) |",
        "|---|---|---|---|---|---|---|---|",
        *filas,
        "",
        "| Resumen | A | B |",
        "|---|---|---|",
        *[f"| {k.capitalize()} | {prom_crit('A', k)} | {prom_crit('B', k)} |" for k in ("formato", "estructura", "herramienta", "citacion")],
        f"| Puntaje promedio | {pa:.2f} | {pb:.2f} |",
        f"| Latencia promedio de redacción (s) | {promedio('A', 'latencia_s'):.2f} | {promedio('B', 'latencia_s'):.2f} |",
        "",
        "Las respuestas completas están en el archivo .jsonl del mismo nombre.",
    ]) + "\n", encoding="utf-8")
    print(f"\nResultados en {base.with_suffix('.md')}")


if __name__ == "__main__":
    main()
