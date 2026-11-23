FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
COPY scripts ./scripts
COPY corpus ./corpus
COPY data ./data
COPY docs ./docs
COPY tests ./tests

# Usuario sin privilegios (principio de mínimo privilegio)
RUN useradd --create-home agente && mkdir -p /app/indice /app/trazas /app/modelos && chown -R agente /app
USER agente

# Al arrancar: indexa el corpus solo si cambió y luego inicia el bot con long polling.
CMD ["sh", "-c", "python -m scripts.ingest --si-cambio && python -m app.bot.telegram_bot"]
