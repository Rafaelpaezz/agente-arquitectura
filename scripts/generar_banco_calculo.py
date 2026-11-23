"""Genera data/banco_ejemplos/calculo.jsonl: ejemplos resueltos de cálculo con la herramienta.

Los números de cada respuesta los calcula la propia herramienta (no se escriben a mano), así el
banco siempre es coherente con el código. Semilla fija: el archivo es reproducible.

Uso: python -m scripts.generar_banco_calculo
"""
from __future__ import annotations

import json
import random
import re
from pathlib import Path

from app.tools.disponibilidad import calcular_disponibilidad

SALIDA = Path(__file__).resolve().parent.parent / "data" / "banco_ejemplos" / "calculo.jsonl"
FUENTE = {"doc": "SDP", "seccion": "Availability patterns > Availability in numbers > Availability in parallel vs in sequence"}
CITA = f"[{FUENTE['doc']}, §{FUENTE['seccion']}]"

DOMINIOS = ["una tienda en línea", "un sistema de citas médicas", "una plataforma de streaming de música",
            "un sistema bancario de transferencias", "una app de reservas de hotel", "un portal de noticias",
            "un sistema de facturación electrónica", "una plataforma de cursos virtuales", "una app de transporte",
            "un sistema de inventario de bodega"]
VALORES = [0.99, 0.995, 0.998, 0.999, 0.9995, 0.9999, 0.98, 0.97, 0.95, 0.9]


def pct(a: float) -> str:
    return f"{a * 100:g}%"


def mejora(expr: str, r: dict) -> tuple[str, dict] | None:
    """Duplica en paralelo el punto único de falla más débil y recalcula."""
    if not r["puntos_unicos_de_falla"]:
        return None
    hojas = dict(re.findall(r"([A-Za-z_][\w\-]*)=([\d.]+%?)", expr))
    candidatos = [n for n in r["puntos_unicos_de_falla"] if n in hojas]
    if not candidatos:
        return None
    valor = lambda n: float(hojas[n].rstrip("%")) / (100 if hojas[n].endswith("%") else 1)
    peor = min(candidatos, key=valor)
    nueva = re.sub(rf"\b{re.escape(peor)}={re.escape(hojas[peor])}",
                   f"paralelo({peor}_a={hojas[peor]}, {peor}_b={hojas[peor]})", expr, count=1)
    return peor, {"expr": nueva, "r": calcular_disponibilidad(nueva)}


def respuesta(expr: str) -> str:
    r = calcular_disponibilidad(expr)
    nueves = f"{r['nueves']} nueves" if r["nueves"] is not None else "disponibilidad perfecta"
    spof = ", ".join(r["puntos_unicos_de_falla"]) or "ninguno"
    lineas = [
        f"**Respuesta:** La disponibilidad total es {r['disponibilidad_pct']:.4f} % ({nueves}), "
        f"con una caída esperada de {r['caida_anual']} al año.",
        "**Explicación:**",
        f"- Topología usada: {r['topologia']}. En serie se multiplican las disponibilidades y en paralelo "
        f"se calcula 1 − (1 − A1)(1 − A2)… {CITA}",
        f"- Caída esperada: {r['caida_anual']} al año y {r['caida_mensual']} al mes (resultado de la herramienta).",
        f"- Eslabón más débil de la cadena principal: {r['eslabon_mas_debil']}. Puntos únicos de falla: {spof}.",
    ]
    m = mejora(expr, r)
    if m:
        peor, alt = m
        lineas.append(f"- Mejora sugerida: duplicar en paralelo '{peor}' sube la disponibilidad a "
                      f"{alt['r']['disponibilidad_pct']:.4f} %, porque la redundancia en paralelo la aumenta. {CITA}")
    else:
        lineas.append("- No quedan puntos únicos de falla: para subir más hay que mejorar el componente más débil "
                      f"o agregar más réplicas. {CITA}")
    lineas.append(f"**Fuentes:** {CITA}")
    return "\n".join(lineas)


def generar(rnd: random.Random) -> list[tuple[str, str]]:
    casos = []
    v = lambda: rnd.choice(VALORES)
    for i in range(30):
        dom = DOMINIOS[i % len(DOMINIOS)]
        plantilla = i % 6
        if plantilla == 0:
            a, b, c = v(), v(), v()
            expr = f"serie(web={pct(a)}, api={pct(b)}, bd={pct(c)})"
            p = (f"En {dom}, el servidor web ({pct(a)}), la API ({pct(b)}) y la base de datos ({pct(c)}) "
                 "están en serie. ¿Qué disponibilidad tiene el sistema?")
        elif plantilla == 1:
            lb, app, bd = rnd.choice([0.9999, 0.9995]), v(), rnd.choice([0.999, 0.9995, 0.9999])
            n = rnd.choice([2, 3])
            apps = ", ".join(f"app{j + 1}={pct(app)}" for j in range(n))
            expr = f"serie(balanceador={pct(lb)}, paralelo({apps}), bd={pct(bd)})"
            p = (f"Para {dom} tengo un balanceador de {pct(lb)} delante de {n} servidores de aplicación de "
                 f"{pct(app)} cada uno y una base de datos de {pct(bd)}. ¿Cuál es la disponibilidad total y dónde están los puntos únicos de falla?")
        elif plantilla == 2:
            n = rnd.choice([3, 4, 5])
            k = rnd.randint(2, n - 1)
            a = rnd.choice([0.9, 0.95, 0.98, 0.99])
            expr = f"kden({k}, {n}, nodo={pct(a)})"
            p = (f"Un clúster de {dom} tiene {n} nodos idénticos de {pct(a)} y funciona mientras haya al menos {k} activos. "
                 "Calcula su disponibilidad.")
        elif plantilla == 3:
            g, app, bd = rnd.choice([0.9999, 0.9995]), v(), v()
            expr = f"serie(gateway={pct(g)}, paralelo(serie(app_r1={pct(app)}, bd_r1={pct(bd)}), serie(app_r2={pct(app)}, bd_r2={pct(bd)})))"
            p = (f"{dom.capitalize()} corre en dos regiones activas; en cada una hay una app de {pct(app)} y una base de "
                 f"{pct(bd)} en serie, y ambas regiones están detrás de un gateway de {pct(g)}. ¿Qué disponibilidad se obtiene?")
        elif plantilla == 4:
            a, n = v(), rnd.choice([2, 3])
            expr = f"replicas({n}, servicio={pct(a)})"
            p = f"Si replico {n} veces un servicio de {dom} que tiene {pct(a)} de disponibilidad, ¿cuántos nueves gano?"
        else:
            a, b, c, d = v(), v(), v(), v()
            expr = f"serie(dns={pct(max(a, 0.9999))}, cdn={pct(b)}, paralelo(api1={pct(c)}, api2={pct(c)}), cola={pct(d)})"
            p = f"Calcula: {expr}"
        casos.append((p, expr))
    return casos


def main() -> None:
    rnd = random.Random(2026)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        for i, (p, expr) in enumerate(generar(rnd), 1):
            f.write(json.dumps({"id": f"CAL-{i:03d}", "tipo": "calculo", "pregunta": p, "expresion": expr,
                                "fuentes": [FUENTE], "respuesta": respuesta(expr)}, ensure_ascii=False) + "\n")
    print(f"{SALIDA}: 30 ejemplos")


if __name__ == "__main__":
    main()
