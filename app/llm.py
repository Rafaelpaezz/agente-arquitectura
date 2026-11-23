"""Cliente mínimo para cualquier endpoint compatible con la API de OpenAI (Gemini, Groq, Azure, Ollama)."""
from __future__ import annotations

import time

from openai import OpenAI

from app.config import ModeloLLM


class ClienteLLM:
    def __init__(self, cfg: ModeloLLM, timeout: float = 180.0):
        self.cfg = cfg
        self._cliente = OpenAI(base_url=cfg.base_url, api_key=cfg.api_key or "sin-llave", timeout=timeout, max_retries=2)

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
        r = self._cliente.chat.completions.create(
            model=self.cfg.modelo,
            messages=mensajes,
            temperature=self.cfg.temperatura if temperatura is None else temperatura,
            max_tokens=max_tokens or self.cfg.max_tokens,
            **extra,
        )
        return (r.choices[0].message.content or "").strip(), time.perf_counter() - inicio
