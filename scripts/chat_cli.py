"""Probar el agente desde la terminal, sin Telegram.

Uso:  python -m scripts.chat_cli               (interactivo)
      python -m scripts.chat_cli "¿Qué es el patrón cache-aside?"
"""
from __future__ import annotations

import sys

from app.fabrica import construir_agente


def main() -> None:
    agente = construir_agente()
    preguntas = sys.argv[1:]
    if preguntas:
        for p in preguntas:
            t = agente.responder(p, chat_id="cli")
            print(t.respuesta, "\n\n---\n" + t.traza.resumen_legible() + "\n")
        return
    print("Escriba su pregunta (Ctrl+C para salir). '/traza' muestra la última decisión.")
    ultima = None
    while True:
        try:
            p = input("\n> ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if not p:
            continue
        if p == "/traza":
            print(ultima.traza.resumen_legible() if ultima else "sin preguntas")
            continue
        ultima = agente.responder(p, chat_id="cli")
        print("\n" + ultima.respuesta)


if __name__ == "__main__":
    main()
