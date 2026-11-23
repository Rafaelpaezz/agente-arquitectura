---
status: aceptada
date: 2026-11-23
decision-makers: Mateo Acosta López
---

# ADR 0001. Selección del modelo base y reparto de funciones entre modelos

## Context and Problem Statement

El agente necesita (a) clasificar cada pregunta y extraer los parámetros de la herramienta, y (b) redactar la
respuesta final a partir de los fragmentos recuperados. En la Ruta 1 la respuesta final debe salir de un
modelo de pesos abiertos de 1B a 4B parámetros, ajustado con LoRA/QLoRA y servido en un VPS sin GPU
(4 vCPU, 8 GB de RAM). ¿Qué modelo base se ajusta y qué modelo cumple cada función?

## Decision Drivers

* Calidad en español: las preguntas y respuestas son en español y el corpus está en inglés y español.
* Seguir instrucciones de formato y citar: es justamente lo que enseña el fine-tuning.
* Caber en el VPS junto con el agente y el índice: el modelo cuantizado debe ocupar menos de ~3 GB de RAM.
* Entrenable gratis: QLoRA en una GPU T4 de Colab/Kaggle (16 GB) en menos de una hora.
* Soporte de herramientas: Unsloth (entrenamiento), exportación a GGUF y Ollama (inferencia en CPU).
* Licencia compatible con un uso académico.

## Considered Options

* Qwen2.5-3B-Instruct
* Llama-3.2-3B-Instruct
* Phi-3.5-mini-instruct (3.8B)
* Qwen2.5-1.5B-Instruct

## Decision Outcome

Opción elegida: **Qwen2.5-3B-Instruct**, porque está en el tope del rango permitido (más capacidad para seguir
el formato en español), tiene plantilla ChatML estándar, versión pre-cuantizada en Unsloth y un GGUF Q4_K_M de ~1,9 GB
que corre en CPU con margen dentro de 8 GB.

Reparto de funciones:

| Función | Modelo | Justificación |
|---|---|---|
| Clasificación (solo cuando las reglas no son concluyentes) y extracción de la topología | Gemini 2.5 Flash por API (nivel gratuito) | Tarea corta con salida JSON; un modelo grande es más confiable y responde en ~1 s. No genera la respuesta final. |
| Redacción de la respuesta final | Qwen2.5-3B-Instruct + adaptador QLoRA, GGUF Q4_K_M en Ollama | Exigido por la Ruta 1. El adaptador aporta la forma; el contenido viene de los fragmentos. |
| Embeddings del RAG | paraphrase-multilingual-MiniLM-L12-v2 (fastembed, local) | Ver ADR 0002. |

### Consequences

* Bueno, porque el modelo cuantizado (~1,9 GB) más el agente y el índice (~1 GB) caben en 8 GB de RAM.
* Bueno, porque la misma interfaz compatible con OpenAI sirve para Ollama y para la API: cambiar de modelo es cambiar el `.env`.
* Malo, porque en CPU cada respuesta tarda decenas de segundos; se mitiga con la acción *typing* de Telegram y `OLLAMA_KEEP_ALIVE` para evitar arranques en frío.
* Malo, porque la licencia de Qwen2.5-3B (Qwen Research License) restringe el uso comercial; para este trabajo académico no es un problema, y Llama-3.2-3B sería el reemplazo si se necesitara.
* Malo, porque la clasificación depende de un servicio externo cuando las reglas dudan; si la API falla, el agente usa un valor por defecto seguro (ADR 0003).

### Confirmation

Se confirma con la comparación de `scripts/comparar.py --modo modelo` (modelo base contra modelo ajustado, mismas
preguntas, mismo prompt y mismos fragmentos) y con el reporte de latencia sobre las 10 preguntas en el VPS.

## Pros and Cons of the Options

### Qwen2.5-3B-Instruct

* Bueno, porque sigue bien instrucciones de formato y maneja español con soltura.
* Bueno, porque Unsloth publica la versión `bnb-4bit`, lista para QLoRA en una T4.
* Malo, porque su licencia no es Apache 2.0 (a diferencia de los Qwen2.5 de 1.5B y 7B).

### Llama-3.2-3B-Instruct

* Bueno, porque el español es uno de sus idiomas oficialmente soportados.
* Malo, porque hay que aceptar la licencia en Hugging Face antes de descargarlo en Colab, lo que añade un paso con token.

### Phi-3.5-mini-instruct

* Bueno, porque tiene licencia MIT.
* Malo, porque con 3,8B y contexto largo deja menos margen de RAM en el VPS y es más lento en CPU.

### Qwen2.5-1.5B-Instruct

* Bueno, porque es el doble de rápido en CPU y tiene licencia Apache 2.0.
* Malo, porque comete más errores al copiar citas exactas; queda como plan B si la latencia del 3B no es aceptable.

## More Information

El enunciado permite usar un modelo por API para la clasificación y la lógica de decisión siempre que el modelo
ajustado redacte la respuesta final y la documentación indique la función de cada uno: esta tabla cumple ese requisito.
