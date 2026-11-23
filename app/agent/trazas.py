"""Registro de trazas: cada consulta deja una línea JSON con todas las decisiones del agente."""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


class Traza:
    def __init__(self, pregunta: str, chat_id: str | int | None = None):
        self.datos: dict = {
            "id": uuid.uuid4().hex[:12],
            "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            # El id del chat se guarda como hash: las trazas no deben identificar a la persona.
            "chat": hashlib.sha256(str(chat_id).encode()).hexdigest()[:10] if chat_id is not None else None,
            "pregunta": pregunta,
            "pasos": [],
            "latencias_s": {},
        }
        self._inicio = time.perf_counter()

    def paso(self, nombre: str, **detalle) -> None:
        """Agrega un paso de decisión, en orden."""
        self.datos["pasos"].append({"paso": nombre, **detalle})

    def latencia(self, etapa: str, segundos: float) -> None:
        self.datos["latencias_s"][etapa] = round(segundos, 3)

    def cerrar(self, respuesta: str, **resumen) -> dict:
        self.datos["latencias_s"]["total"] = round(time.perf_counter() - self._inicio, 3)
        self.datos["respuesta"] = respuesta
        self.datos.update(resumen)
        return self.datos

    def resumen_legible(self) -> str:
        d = self.datos
        lineas = [f"Traza {d['id']}"]
        for p in d["pasos"]:
            detalle = ", ".join(f"{k}={v}" for k, v in p.items() if k != "paso" and not isinstance(v, (list, dict)))
            lineas.append(f"• {p['paso']}: {detalle}")
        lineas.append("Latencias: " + ", ".join(f"{k} {v}s" for k, v in d["latencias_s"].items()))
        return "\n".join(lineas)


class RegistroTrazas:
    def __init__(self, directorio: Path):
        self.directorio = directorio
        self.directorio.mkdir(parents=True, exist_ok=True)

    def guardar(self, traza: Traza) -> Path:
        archivo = self.directorio / f"trazas-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with open(archivo, "a", encoding="utf-8") as f:
            f.write(json.dumps(traza.datos, ensure_ascii=False) + "\n")
        return archivo
