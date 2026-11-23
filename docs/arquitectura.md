# Arquitectura del agente

## Vista de contexto

```mermaid
flowchart LR
    U[Estudiante en Telegram] -- mensajes --> TG[(Telegram Bot API)]
    subgraph VPS["Azure VM B4als_v2 · Docker Compose"]
        BOT[agente: bot + ciclo de decisión + RAG + herramienta]
        OL[ollama: Qwen2.5-3B ajustado GGUF]
        IDX[(índice FAISS + fragmentos)]
        TR[(trazas JSONL)]
    end
    BOT -- long polling (saliente) --> TG
    BOT -- clasificación / extracción JSON --> API[(Gemini API)]
    BOT -- redacción /v1/chat/completions --> OL
    BOT --- IDX
    BOT --- TR
```

## Vista de bloques

| Bloque | Archivo | Responsabilidad |
|---|---|---|
| Canal | `app/bot/telegram_bot.py` | Long polling, acción *typing*, comandos `/fuentes`, `/traza`, `/fewshot` |
| Ciclo de decisión | `app/agent/agente.py` | Clasificar → decidir → verificar → ejecutar → redactar → revisar citas |
| Clasificador | `app/agent/clasificador.py` | Reglas con pesos y, si dudan, modelo por API con JSON |
| Few-shot dinámico | `app/agent/fewshot.py` | Selección de ejemplos por tipo (criterio por defecto) o por similitud |
| Prompts | `app/agent/prompts.py` | Prompt de sistema fijo, instrucciones por tipo, respuestas directas |
| Trazas | `app/agent/trazas.py` | Un JSON por consulta con cada paso, puntajes y latencias |
| RAG | `app/rag/` | Fragmentación por estructura, embeddings, FAISS, citas |
| Herramienta | `app/tools/disponibilidad.py` | Disponibilidad compuesta, nueves, caída, eslabón débil, SPOF |
| Cliente LLM | `app/llm.py` | Un solo cliente para cualquier endpoint compatible con OpenAI |
| Evaluación | `app/evaluacion/rubrica.py`, `scripts/` | Top-k del RAG, separación de datos, comparación A/B |

## Vista de ejecución: una pregunta de cálculo

```mermaid
sequenceDiagram
    participant U as Usuario
    participant B as Bot
    participant A as Agente
    participant C as Clasificador
    participant H as Herramienta
    participant R as RAG
    participant M as Modelo redactor
    U->>B: "balanceador 99.99%, 3 servidores 99.5% en paralelo, BD 99.9%"
    B-->>U: escribiendo…
    B->>A: responder(pregunta)
    A->>C: clasificar → reglas: calculo (puntaje 3)
    A->>A: decidir: herramienta · verificar: hay números ✓
    A->>M: (modelo de decisión) extraer topología → serie(...)
    A->>H: calcular_disponibilidad(expresión)
    H-->>A: 99.89 %, SPOF: balanceador, bd
    A->>R: fragmentos de apoyo (fórmula serie/paralelo)
    A->>M: prompt de sistema + ejemplos de cálculo + fragmentos + resultado
    M-->>A: respuesta con formato y citas
    A->>A: revisar citas · guardar traza
    A-->>B: respuesta
    B-->>U: respuesta
```

## Atributos de calidad del propio agente

| Atributo | Táctica |
|---|---|
| Verificabilidad | Toda afirmación de contenido lleva cita `[DOC, §sección]`; se revisa que la cita exista |
| Explicabilidad | Reglas de clasificación y tabla de decisión explícitas; trazas por paso |
| Disponibilidad | `restart: unless-stopped`, healthcheck de Ollama, degradación a reglas si la API cae |
| Seguridad | Secretos en `.env`, contenedor sin root, sin puertos expuestos, `eval` prohibido en la herramienta |
| Rendimiento | Respuestas directas y "sin evidencia" sin llamar al modelo; `OLLAMA_KEEP_ALIVE` evita arranques en frío |
| Modificabilidad | Cliente LLM único: cambiar de proveedor o de modelo es cambiar el `.env` |
