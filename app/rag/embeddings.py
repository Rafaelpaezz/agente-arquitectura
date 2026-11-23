"""Modelos de embeddings intercambiables.

- fastembed (por defecto): modelo multilingüe local en CPU (ONNX), gratis y sin límite de
  peticiones. Permite preguntar en español sobre documentos en inglés.
- tfidf: n-gramas de caracteres. No descarga nada. Solo para pruebas automáticas y como
  línea base de recuperación léxica.

Todos los vectores salen normalizados (norma 1), así el producto interno es la similitud coseno.
"""
from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np


def _normalizar(m: np.ndarray) -> np.ndarray:
    m = np.asarray(m, dtype="float32")
    normas = np.linalg.norm(m, axis=1, keepdims=True)
    normas[normas == 0] = 1.0
    return m / normas


class EmbedderFastembed:
    def __init__(self, modelo: str, cache: Path | None = None):
        from fastembed import TextEmbedding

        self.nombre = modelo
        # El modelo (~120 MB) se descarga una vez y queda en el volumen de caché.
        self._modelo = TextEmbedding(model_name=modelo, cache_dir=str(cache) if cache else None)
        # Los modelos E5 esperan prefijos "query:" y "passage:"
        self._e5 = "e5" in modelo.lower()

    def documentos(self, textos: list[str]) -> np.ndarray:
        if self._e5:
            textos = [f"passage: {t}" for t in textos]
        return _normalizar(np.array(list(self._modelo.embed(textos, batch_size=32))))

    def consulta(self, texto: str) -> np.ndarray:
        if self._e5:
            texto = f"query: {texto}"
        return _normalizar(np.array(list(self._modelo.embed([texto]))))


class EmbedderTfidf:
    def __init__(self, ruta_modelo: Path | None = None):
        self.nombre = "tfidf-char-3-5"
        self._ruta = ruta_modelo
        self._vect = None
        if ruta_modelo and ruta_modelo.exists():
            with open(ruta_modelo, "rb") as f:
                self._vect = pickle.load(f)

    def documentos(self, textos: list[str]) -> np.ndarray:
        from sklearn.feature_extraction.text import TfidfVectorizer

        self._vect = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, max_features=60000)
        m = self._vect.fit_transform(textos).toarray()
        if self._ruta:
            self._ruta.parent.mkdir(parents=True, exist_ok=True)
            with open(self._ruta, "wb") as f:
                pickle.dump(self._vect, f)
        return _normalizar(m)

    def consulta(self, texto: str) -> np.ndarray:
        if self._vect is None:
            raise RuntimeError("El modelo TF-IDF no está entrenado: ejecute scripts.ingest")
        return _normalizar(self._vect.transform([texto]).toarray())


def crear_embedder(backend: str, modelo: str, dir_indice: Path, cache: Path | None = None):
    if backend == "fastembed":
        return EmbedderFastembed(modelo, cache)
    if backend == "tfidf":
        return EmbedderTfidf(dir_indice / "tfidf.pkl")
    raise ValueError(f"EMBEDDINGS_BACKEND desconocido: {backend}")
