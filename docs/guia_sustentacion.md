# Guía para la sustentación

La sustentación es individual y el enunciado pide explicar la lógica de decisión **línea por línea**.
Esta guía ordena qué estudiar y qué mostrar.

## 1. Demostración en vivo (5 minutos)

1. `ssh` al VPS → `docker compose ps` (contenedores arriba) → `nproc && free -h`.
2. En Telegram, una pregunta de cada tipo, y después de cada una `/traza`:
   * Conceptual: "¿Qué es el patrón write-through?" → acción **rag**, citas `[SDP, §...]`.
   * Cálculo: "Tengo un balanceador de 99.99%, tres servidores de 99.5% en paralelo y una base de 99.9%…" → **herramienta**.
   * Corrección: "¿Cómo se calcula la disponibilidad en serie?" → reglas dicen *calculo*, la verificación corrige a **rag**.
   * Fuera de dominio: "¿Cuál es la capital de Francia?" → **directa**, sin llamar al modelo.
   * Sin evidencia: algo que no esté en el corpus → **sin_evidencia**.
3. Ruta 2: `/fewshot off` y la misma pregunta otra vez, para mostrar la diferencia de formato.

## 2. El ciclo de decisión (`app/agent/agente.py`, método `responder`)

| Líneas (bloque) | Qué hace | Por qué |
|---|---|---|
| `clasificar(pregunta, self.cliente_decision)` | Reglas → modelo por API → valor por defecto | ADR 0003 |
| `ACCION_POR_TIPO[tipo]` | Tabla fija tipo → acción | Determinista y explicable |
| `if accion == HERRAMIENTA and not expresion and not _HAY_NUMEROS...` | Corrige cálculo sin números a rag | Evita llamar a la herramienta sin datos |
| `elif accion != HERRAMIENTA and expresion` | Corrige a herramienta si hay `serie(...)` | La expresión explícita manda |
| `if accion == DIRECTA` | Respuesta fija, sin modelo | Ahorra costo y latencia |
| `_usar_herramienta` | Expresión explícita o extraída por el modelo; un reintento con el error | La herramienta valida, el modelo corrige |
| `_recuperar` + umbral | k = 5, descarta fragmentos bajo 0,30; si no queda ninguno → sin evidencia | No responder de memoria |
| `_armar_prompt` | Sistema fijo + [instrucciones y ejemplos del tipo] + fragmentos + resultado | Mismo prompt en las dos versiones |
| `revisar_citas` | Compara citas usadas con las permitidas | Detecta citas inventadas |

Preguntas que probablemente le hagan:

* **¿Por qué no usó function calling?** Porque la decisión quedaría dentro del modelo y no sería explicable ni determinista; el enunciado exige escribir el ciclo.
* **¿Qué pasa si se cae la API de Gemini?** Las reglas siguen clasificando; si no son concluyentes se usa el valor por defecto (conceptual o fuera de dominio). La herramienta sigue aceptando expresiones explícitas.
* **¿Cómo sabe que no responde de memoria?** El prompt lo prohíbe, el umbral corta cuando no hay evidencia y la traza muestra qué citas usó y si alguna es inválida.
* **¿Cómo eligió el umbral 2/1 de las reglas?** Puntaje mínimo 2 evita decidir por una sola palabra; margen 1 evita empates. Se ajustó con las pruebas de `tests/test_agente.py`.

## 3. Herramienta (`app/tools/disponibilidad.py`)

* Parser descendente recursivo escrito a mano: **nunca `eval`** (sería una vulnerabilidad de inyección de código).
* Fórmulas: serie = producto; paralelo = 1 − ∏(1 − Aᵢ); k-de-n = suma binomial.
* Validaciones: rango [0, 1] o porcentaje, k ≤ n, n ≤ 100, profundidad ≤ 10, ≤ 200 componentes, paréntesis balanceados.
* Casos límite: un solo componente, disponibilidad 1 (nueves = ∞, se reporta 100 %), disponibilidad 0, k = n (equivale a serie).
* Puntos únicos de falla: hojas en la cadena de serie principal sin redundancia.

## 4. RAG

Estrategia en el ADR 0002. Números a tener a mano: fragmentos indexados, k, resultado de `evidencias/recuperacion_top_k.md`.

## 5. Few-shot dinámico vs fine-tuning (pregunta segura)

| | Few-shot dinámico (Ruta 2) | Fine-tuning QLoRA (Ruta 1) |
|---|---|---|
| ¿Cambian los pesos? | No: cambia la entrada de cada petición | Sí: el comportamiento queda en el adaptador |
| Costo por petición | Más tokens de contexto en cada consulta → más costo y latencia | No hay que enviar ejemplos |
| Cambiar de modelo | El banco se reutiliza tal cual | Hay que reentrenar: el adaptador está atado al modelo base |
| Qué aporta | Forma de la respuesta | Forma de la respuesta |
| Qué NO aporta | Conocimiento confiable | Conocimiento confiable (con ~100 ejemplos) |

En este proyecto el **mismo banco de 110 ejemplos** sirve para los dos: en la Ruta 2 se inserta en el prompt y en la
Ruta 1 se convierte en el dataset de entrenamiento (`scripts/construir_dataset_finetune.py`).

## 6. Separación entre entrenamiento y evaluación

1. Se reservaron 32 secciones del corpus para evaluación antes de escribir el banco.
2. `scripts/validar_banco.py` falla si algún ejemplo usa una sección reservada.
3. `scripts/verificar_fuga.py` compara cada pregunta de evaluación y comparación con las 110 del banco (TF-IDF de palabras y de caracteres); umbral 0,60.
4. En la primera ejecución, CMP-01 dio 0,73 contra "Explica la consistencia fuerte" y se reescribió: el procedimiento detectó un caso real.
