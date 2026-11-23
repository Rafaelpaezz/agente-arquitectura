"""Cliente mínimo para cualquier endpoint compatible con la API de OpenAI (Gemini, Groq, Azure, Ollama)."""
from __future__ import annotations

import time

import logging

from openai import APIConnectionError, APIStatusError, OpenAI

from app.config import ModeloLLM


log = logging.getLogger(__name__)

# Errores por los que vale la pena probar con otro modelo: saturación (503), cuota (429),
# modelo retirado o inexistente (404) y caídas de conexión.
_ERRORES_REINTENTABLES = {404, 429, 500, 502, 503, 504}


class ClienteLLM:
    def __init__(self, cfg: ModeloLLM, timeout: float = 180.0):
        self.cfg = cfg
        self._cliente = OpenAI(base_url=cfg.base_url, api_key=cfg.api_key or "sin-llave", timeout=timeout, max_retries=2)

        self.ultimo_modelo = cfg.modelo

    @property
    def nombre(self) -> str:
        return self.cfg.modelo

    def chat(self, mensajes: list[dict], temperatura: float | None = None, max_tokens: int | None = None,
             json: bool = False) -> tuple[str, float]:
        """Devuelve (texto, segundos)."""
        extra = {"response_format": {"type": "json_object"}} if json else {}
        if self.cfg.reasoning_effort:
            extra["reasoning_effort"] = self.cfg.reasoning_effort
        inicio = time.perf_counter()
        modelos = (self.cfg.modelo, *self.cfg.alternativos)
        for i, modelo in enumerate(modelos):
            try:
                r = self._cliente.chat.completions.create(
                    model=modelo,
                    messages=mensajes,
                    temperature=self.cfg.temperatura if temperatura is None else temperatura,
                    max_tokens=max_tokens or self.cfg.max_tokens,
                    **extra,
                )
                self.ultimo_modelo = modelo
                return (r.choices[0].message.content or "").strip(), time.perf_counter() - inicio
            except (APIStatusError, APIConnectionError) as e:
                codigo = getattr(e, "status_code", None)
                ultimo = i == len(modelos) - 1
                if ultimo or (codigo is not None and codigo not in _ERRORES_REINTENTABLES):
                    raise
                log.warning("Modelo %s no disponible (%s); se prueba con %s", modelo, codigo or "conexión", modelos[i + 1])
