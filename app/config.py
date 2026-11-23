"""Configuración del agente. Todo se lee de variables de entorno (archivo .env).

Ningún secreto está escrito en el código: los tokens y llaves van en .env, que está en
.gitignore. El repositorio solo incluye .env.example.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")


def _env(nombre: str, defecto: str = "") -> str:
    return os.getenv(nombre, defecto).strip()


def _env_float(nombre: str, defecto: float) -> float:
    return float(_env(nombre, str(defecto)))


def _env_int(nombre: str, defecto: int) -> int:
    return int(_env(nombre, str(defecto)))


@dataclass(frozen=True)
class ModeloLLM:
    """Un modelo accesible por un endpoint compatible con la API de OpenAI.

    Sirve para Gemini, Groq, Azure OpenAI, OpenAI y Ollama (todos exponen /v1/chat/completions).
    """
    base_url: str
    api_key: str
    modelo: str
    temperatura: float = 0.2
    max_tokens: int = 700
    reasoning_effort: str = ""      # p. ej. "minimal" para reducir el "thinking" de Gemini 3; vacío = no se envía


@dataclass(frozen=True)
class Config:
    # Telegram
    telegram_token: str = field(default_factory=lambda: _env("TELEGRAM_BOT_TOKEN"))

    # Modelo de decisión (clasificación y extracción de parámetros). Va por API.
    decision: ModeloLLM = field(default_factory=lambda: ModeloLLM(
        base_url=_env("DECISION_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
        api_key=_env("DECISION_API_KEY"),
        modelo=_env("DECISION_MODEL", "gemini-3.8-flash"),
        temperatura=0.0,
        max_tokens=400,
        reasoning_effort=_env("DECISION_REASONING_EFFORT", ""),
    ))

    # Modelo que redacta la respuesta final.
    #  - Ruta 1: el modelo ajustado servido por Ollama (http://ollama:11434/v1).
    #  - Ruta 2: cualquier modelo por API con el banco de ejemplos.
    redaccion: ModeloLLM = field(default_factory=lambda: ModeloLLM(
        base_url=_env("ANSWER_BASE_URL", "http://ollama:11434/v1"),
        api_key=_env("ANSWER_API_KEY", "ollama"),
        modelo=_env("ANSWER_MODEL", "arqui-qwen2.5-3b-ft"),
        temperatura=_env_float("ANSWER_TEMPERATURE", 0.2),
        max_tokens=_env_int("ANSWER_MAX_TOKENS", 1200),
        reasoning_effort=_env("ANSWER_REASONING_EFFORT", ""),
    ))

    # Few-shot dinámico: on | off  y criterio: clasificacion | similitud
    fewshot_activo: bool = field(default_factory=lambda: _env("FEWSHOT_ENABLED", "on").lower() == "on")
    fewshot_criterio: str = field(default_factory=lambda: _env("FEWSHOT_SELECTOR", "clasificacion"))
    fewshot_k: int = field(default_factory=lambda: _env_int("FEWSHOT_K", 3))

    # RAG
    embeddings_backend: str = field(default_factory=lambda: _env("EMBEDDINGS_BACKEND", "fastembed"))
    embeddings_modelo: str = field(default_factory=lambda: _env(
        "EMBEDDINGS_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"))
    rag_k: int = field(default_factory=lambda: _env_int("RAG_TOP_K", 5))
    rag_umbral: float = field(default_factory=lambda: _env_float("RAG_MIN_SCORE", 0.30))

    # Rutas
    dir_corpus: Path = RAIZ / "corpus"
    dir_indice: Path = field(default_factory=lambda: Path(_env("INDEX_DIR", str(RAIZ / "indice"))))
    dir_banco: Path = RAIZ / "data" / "banco_ejemplos"
    dir_cache_modelos: Path = field(default_factory=lambda: Path(_env("MODELS_CACHE_DIR", str(RAIZ / "modelos"))))
    dir_trazas: Path = field(default_factory=lambda: Path(_env("TRACES_DIR", str(RAIZ / "trazas"))))


def cargar_config() -> Config:
    return Config()
