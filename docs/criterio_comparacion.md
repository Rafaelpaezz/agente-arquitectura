# Criterio de comparación (declarado antes de medir)

**Fecha de declaración:** 23 de noviembre de 2026, antes de ejecutar `scripts/comparar.py`.
El historial de git de este archivo es la prueba de que el criterio se fijó antes de las mediciones.

## Qué se compara

| Ruta | Versión A | Versión B | Lo único que cambia |
|---|---|---|---|
| Ruta 1 | Modelo base `qwen2.5:3b-instruct` | Modelo ajustado `arqui-qwen2.5-3b-ft` | Los pesos del redactor (adaptador QLoRA) |
| Ruta 2 | Few-shot **desactivado** | Few-shot dinámico **activado** (criterio: clasificación, k = 3) | Ejemplos e instrucciones del tipo en el prompt |

## Condiciones

* Las mismas **10 preguntas** (`data/evaluacion/preguntas_comparacion.jsonl`): 2 conceptuales, 2 de selección,
  3 de compromisos y 3 de cálculo. Ninguna aparece, ni literal ni reformulada, en el banco ni en el dataset
  (ver `evidencias/separacion_datos.md`).
* El mismo **prompt de sistema** (`app/agent/prompts.py::PROMPT_SISTEMA`).
* La misma **clasificación** y los mismos **fragmentos recuperados**: la versión A recupera y la versión B recibe
  exactamente esos fragmentos (`fragmentos_fijos`) y esa clasificación (`clasificacion_fija`).
* El mismo resultado de la herramienta en las preguntas de cálculo.
* Temperatura 0,2 en ambas versiones.

## Qué se mide (y qué no)

Se mide la **forma** de la respuesta. **No** se mide conocimiento factual: ni el fine-tuning con ~100 ejemplos ni el
few-shot dinámico aportan conocimiento confiable; esa función la cumple el corpus del RAG.

| Criterio | Vale 1 si… | Aplica a |
|---|---|---|
| C1. Formato | Aparecen `**Respuesta:**`, `**Explicación:**` y `**Fuentes:**`, una vez cada una y en ese orden. | Todas |
| C2. Estructura | La respuesta directa tiene a lo sumo 2 oraciones y 60 palabras, y la explicación tiene entre 2 y 5 viñetas. | Todas |
| C3. Uso correcto de la herramienta | La respuesta trae la disponibilidad que calculó la herramienta (en %, con al menos 2 decimales) y nombra todos los puntos únicos de falla (o dice que no hay). | Solo cálculo |
| C4. Citación | Hay al menos una cita con el formato `[DOC, §sección]` o `[DOC, p. N]` y **todas** corresponden a fragmentos entregados al modelo. | Todas |

**Puntaje por pregunta** = promedio de los criterios que aplican (0 a 1). **Puntaje de la versión** = promedio de
las 10 preguntas. Además se reporta, por criterio, cuántas preguntas lo cumplen en cada versión.

La rúbrica está implementada en `app/evaluacion/rubrica.py` (probada en `tests/test_rubrica.py`) para que la
medición sea automática y repetible. Como control, se revisan a mano las 20 respuestas y se anota en
`evidencias/comparacion_*.md` cualquier caso en que la rúbrica automática no coincida con el juicio humano.

## Latencia

Se reporta la latencia promedio de redacción sobre las 10 preguntas para cada versión y las características del VPS
(vCPU, modelo de CPU, RAM, sistema operativo). En la Ruta 2 se espera que B sea más lenta y consuma más tokens
porque cada petición lleva los ejemplos; en la Ruta 1 la latencia de A y B debería ser parecida, porque el
comportamiento aprendido está en los pesos y no se envía en cada consulta.
