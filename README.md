# Agente de IA para Arquitectura de Software

Agente conversacional en Telegram que responde preguntas de Arquitectura de Software **citando un corpus de
documentos verificables (RAG)**, calcula **disponibilidad compuesta** con una herramienta propia y decide en cada
consulta, con una lógica escrita a mano y registrada en trazas, si recupera documentos, usa la herramienta o
responde directamente.

* **Ruta 1:** el redactor final es `Qwen2.5-3B-Instruct` ajustado con **QLoRA**, servido con Ollama en CPU.
* **Ruta 2 (respaldo):** **few-shot dinámico** con un banco de 110 ejemplos seleccionados por tipo de pregunta.
* Desplegado con **Docker Compose** en una VM de Azure (4 vCPU, 8 GB).

Autor: Rafael Paez Martinez 67000821 · Arquitectura de Software

---

## Contenido

1. [Arquitectura](#arquitectura)
2. [Función de cada modelo](#función-de-cada-modelo)
3. [Estructura del repositorio](#estructura-del-repositorio)
4. [Cómo levantar el proyecto](#cómo-levantar-el-proyecto)
5. [Evaluación y comparación](#evaluación-y-comparación)
6. [Declaración de separación entre entrenamiento y evaluación](#declaración-de-separación-entre-entrenamiento-y-evaluación)
7. [Corpus y fuentes](#corpus-y-fuentes)
8. [Entregables](#entregables)
9. [Seguridad](#seguridad)

---

## Arquitectura

```
Telegram ──long polling──► Bot ──► Ciclo de decisión (app/agent/agente.py)
                                    1. Clasificar  (reglas → Gemini si dudan → valor por defecto)
                                    2. Decidir     (tabla: rag | herramienta | directa)
                                    3. Verificar   (corrige decisiones incoherentes)
                                    4. Ejecutar    (FAISS top-k  |  disponibilidad compuesta  |  respuesta fija)
                                    5. Redactar    (prompt fijo + [ejemplos del tipo] + fragmentos + resultado)
                                    6. Revisar     (las citas existen en los fragmentos)  ──► traza JSONL
```

Detalle de vistas y atributos de calidad en [`docs/arquitectura.md`](docs/arquitectura.md). Decisiones en
[`docs/adr/`](docs/adr):

* [ADR 0001](docs/adr/0001-seleccion-del-modelo-base.md): selección del modelo base y función de cada modelo
* [ADR 0002](docs/adr/0002-fragmentacion-e-indexacion.md): fragmentación e indexación del corpus
* [ADR 0003](docs/adr/0003-criterio-logica-de-decision.md): criterio de la lógica de decisión
* [ADR 0004](docs/adr/0004-canal-y-despliegue.md): canal de mensajería y despliegue

## Función de cada modelo

| Modelo | Dónde corre | Función | Por qué |
|---|---|---|---|
| Reglas explícitas (`app/agent/clasificador.py`) | VPS | Clasifica la mayoría de preguntas | Deterministas, explicables, sin costo |
| Gemini 2.5 Flash (API, nivel gratuito) | Google | Clasifica cuando las reglas dudan y extrae la topología de cálculo a JSON | Tarea corta y estructurada; **no** redacta la respuesta |
| `arqui-qwen2.5-3b-ft` (Qwen2.5-3B + QLoRA, GGUF Q4_K_M) | VPS, Ollama, CPU | **Redacta la respuesta final** (Ruta 1) | Exigido por la Ruta 1; aporta la forma, el contenido viene del RAG |
| `paraphrase-multilingual-MiniLM-L12-v2` (fastembed) | VPS, CPU | Embeddings del RAG | Recupera documentos en inglés con preguntas en español |

## Estructura del repositorio

```
app/
  agent/        agente.py (ciclo de decisión), clasificador.py, fewshot.py, prompts.py, trazas.py
  rag/          fragmentacion.py, embeddings.py, indice.py
  tools/        disponibilidad.py  (herramienta propia)
  bot/          telegram_bot.py
  evaluacion/   rubrica.py
corpus/         fuentes.yaml (manifiesto) · abierto/ (licencias libres) · externo/ (no redistribuible, solo README)
data/
  banco_ejemplos/   110 ejemplos por tipo: conceptual, seleccion, calculo, compromisos
  evaluacion/       conjunto_evaluacion.jsonl (19), preguntas_comparacion.jsonl (10), secciones_reservadas.json
  finetune/         train.jsonl (100), validacion.jsonl (10)
notebooks/      finetune_qlora_qwen2.5_3b.ipynb (Colab, GPU T4)
scripts/        ingest, validar_banco, verificar_fuga, evaluar_recuperacion, comparar,
                construir_dataset_finetune, generar_banco_calculo, generar_trazas_demo, chat_cli
deploy/ollama/  Modelfile del modelo ajustado
docs/           adr/, arquitectura.md, criterio_comparacion.md, despliegue_azure.md, guia_sustentacion.md
evidencias/     reportes generados (top-k, trazas, comparación, separación, fine-tuning, VPS)
tests/          pruebas de la herramienta, la rúbrica y el ciclo de decisión
```

## Cómo levantar el proyecto

### Requisitos

* Python 3.11+ (local) o Docker con Docker Compose v2.20+ (VPS).
* Un bot de Telegram creado con [@BotFather](https://t.me/BotFather) → `TELEGRAM_BOT_TOKEN`.
* Una llave de la API de Gemini en https://aistudio.google.com/apikey → `DECISION_API_KEY`.
* Ruta 1: el archivo `arqui-qwen2.5-3b-ft.Q4_K_M.gguf` generado con el notebook.

### En local (para desarrollar)

```bash
git clone https://github.com/SU_USUARIO/agente-arquitectura.git && cd agente-arquitectura
python -m venv .venv && source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                        # complete los valores
python -m scripts.ingest                                    # construye el índice
python -m pytest -q                                         # 46 pruebas
python -m scripts.chat_cli "¿Qué es el patrón write-through?"
python -m app.bot.telegram_bot                              # bot en Telegram
```

### En el VPS (producción)

Guía completa paso a paso, con costos de Azure for Students: [`docs/despliegue_azure.md`](docs/despliegue_azure.md).

```bash
cp .env.example .env && nano .env && mkdir -p trazas evidencias
docker compose up -d --build agente                         # Ruta 2
docker compose --profile ruta1 up -d --build                # Ruta 1 (agente + Ollama)
docker compose --profile ruta1 exec ollama ollama create arqui-qwen2.5-3b-ft -f /modelfiles/Modelfile
docker compose logs -f agente
```

### Fine-tuning (Ruta 1)

Abra [`notebooks/finetune_qlora_qwen2.5_3b.ipynb`](notebooks/finetune_qlora_qwen2.5_3b.ipynb) en Google Colab con
GPU T4, cambie la URL del repositorio en la primera celda y ejecute todo (~30 min). Produce el adaptador LoRA, el
GGUF cuantizado y la evidencia del entrenamiento (curva de pérdida, hiperparámetros, muestras de validación).

## Evaluación y comparación

```bash
python -m scripts.validar_banco             # 110 ejemplos, ≥ 20 por tipo, fuentes válidas, sin secciones reservadas
python -m scripts.verificar_fuga            # separación banco vs evaluación   → evidencias/separacion_datos.md
python -m scripts.evaluar_recuperacion      # top-k del RAG (k = 5)            → evidencias/recuperacion_top_k.md
python -m scripts.generar_trazas_demo       # 12 conversaciones con trazas     → evidencias/trazas/
python -m scripts.comparar --modo fewshot   # Ruta 2: sin vs con ejemplos      → evidencias/comparacion_fewshot.md
python -m scripts.comparar --modo modelo --modelo-base qwen2.5:3b-instruct --modelo-ajustado arqui-qwen2.5-3b-ft
```

El criterio de comparación se declaró por escrito antes de medir: [`docs/criterio_comparacion.md`](docs/criterio_comparacion.md).
Mide formato, estructura, uso correcto de la herramienta y citación; **no** mide conocimiento factual. Las dos
versiones reciben las mismas preguntas, el mismo prompt de sistema, la misma clasificación y los mismos fragmentos.

**Few-shot dinámico.** Criterio por defecto: **clasificación** (el tipo decide de qué archivo del banco salen los
ejemplos; dentro del tipo se ordenan por solapamiento de palabras clave). Criterio alternativo para comparar:
**similitud vectorial** contra todo el banco (`FEWSHOT_SELECTOR=similitud`). Un prompt fijo no es few-shot dinámico:
aquí los ejemplos cambian con cada pregunta (lo verifica `tests/test_agente.py::test_fewshot_cambia_segun_la_pregunta`).

## Declaración de separación entre entrenamiento y evaluación

Ninguna pregunta del conjunto de evaluación ni de las diez de comparación aparece, literal ni reformulada, en el
banco de ejemplos ni en el dataset de fine-tuning. Procedimiento:

1. **Reserva previa de secciones.** Antes de escribir el banco se reservaron 32 secciones del corpus para evaluación
   ([`data/evaluacion/secciones_reservadas.json`](data/evaluacion/secciones_reservadas.json)). Las preguntas de
   evaluación y comparación se escribieron sobre esas secciones.
2. **Prohibición verificada.** El banco (y por tanto el dataset de fine-tuning, que se genera a partir del banco)
   no puede usar como fuente ninguna sección reservada; ni siquiera como fragmento distractor.
   `scripts/validar_banco.py` falla si ocurre.
3. **Control de similitud.** `scripts/verificar_fuga.py` compara cada una de las 29 preguntas de prueba con las 110
   del banco usando similitud coseno TF-IDF de palabras y de caracteres. Umbral de alerta: 0,60. Toda pregunta que lo
   supere se reescribe. En la primera ejecución, CMP-01 obtuvo 0,73 frente a "Explica la consistencia fuerte" y se
   reescribió; la versión actual no tiene alertas ([`evidencias/separacion_datos.md`](evidencias/separacion_datos.md)).
4. **Revisión manual** de la pregunta del banco más parecida a cada pregunta de prueba (columna de la misma tabla).
5. **Generación separada.** Los ejemplos de cálculo del banco se generan con una semilla fija y plantillas propias
   (`scripts/generar_banco_calculo.py`); los casos de cálculo de la comparación usan otros dominios y topologías.

## Corpus y fuentes

Manifiesto completo con versión y licencia: [`corpus/fuentes.yaml`](corpus/fuentes.yaml).

| Id | Referencia | Licencia | En el repo |
|---|---|---|---|
| SDP | Martin, D. et al. *The System Design Primer*. GitHub, commit ae9bbd7 | CC BY 4.0 | Sí (extracto) |
| 12F | Wiggins, A. *The Twelve-Factor App*. 12factor.net, commit 1ec1d77 | MIT | Sí |
| ARC42 | Starke, G. y Hruschka, P. *Plantilla arc42* (español), commit 9057fe1 | CC BY-SA 4.0 | Sí |
| MADR | Kopp, O., Zimmermann, O. et al. *Markdown Architectural Decision Records*, commit ba75bb1 | MIT / CC0 | Sí |
| MSAPI | Microsoft. *Azure REST API Guidelines: Considerations for Service Design; Versioning*, commit 1c58ca7 | CC BY 4.0 | Sí |
| ADR-AGENTE | Acosta López, M. Registros de decisión del agente (`docs/adr/`) | Propia | Sí |
| ATAM | Kazman, R., Klein, M. y Clements, P. *ATAM: Method for Architecture Evaluation*. CMU/SEI-2000-TR-004, 2000 | © CMU | No: carga local |
| ISO25010 | ISO/IEC 25010:2023. *Product quality model* | © ISO | No: carga local |
| ISO42010 | ISO/IEC/IEEE 42010:2022. *Architecture description* | © ISO/IEEE | No: carga local |
| SRE | Beyer, B. et al. *Site Reliability Engineering*, cap. 3 y 4. O'Reilly, 2016 | CC BY-NC-ND 4.0 | No: carga local |
| WAF | Microsoft. *Azure Well-Architected Framework* | Términos de Microsoft Learn | No: carga local |

Procedimiento de carga local de los no redistribuibles: [`corpus/externo/README.md`](corpus/externo/README.md).

## Entregables

| # | Entregable | Dónde |
|---|---|---|
| 1 | Repositorio con `.env.example` y sin secretos | Este repo · `.gitignore` excluye `.env` |
| 2 | README reproducible + declaración de separación | Este archivo |
| 3 | ≥ 3 ADR del propio agente | `docs/adr/0001` a `0004` |
| 4 | Corpus y lista de fuentes | `corpus/`, tabla de arriba |
| 5 | Conjunto de evaluación (19 preguntas) + tabla top-k | `data/evaluacion/conjunto_evaluacion.jsonl`, `evidencias/recuperacion_top_k.md` |
| 6 | Trazas de ≥ 10 conversaciones con una corrección | `evidencias/trazas/` |
| 7 | Criterio de comparación + tabla de 10 preguntas | `docs/criterio_comparacion.md`, `evidencias/comparacion_*.md` |
| 8 | Ruta 1: dataset, evidencia de entrenamiento, comparación, latencia | `data/finetune/`, `evidencias/finetune/`, `evidencias/comparacion_modelo.md` |
| 9 | Ruta 2: banco (110) con criterio de clasificación + comparación | `data/banco_ejemplos/`, `evidencias/comparacion_fewshot.md` |
| 10 | Evidencia de RAG y herramienta | `evidencias/trazas/`, capturas |
| 11 | Evidencia de Telegram | `evidencias/capturas/` |
| 12 | Evidencia del despliegue en el VPS | `evidencias/docker_compose_ps.txt`, `evidencias/vps_caracteristicas.txt` |
| 13 | Sustentación técnica | `docs/guia_sustentacion.md` |

## Seguridad

* Secretos solo en `.env` (excluido de git). El repositorio incluye `.env.example` sin valores.
* El contenedor corre con un usuario sin privilegios y no expone puertos; en la VM solo está abierto el puerto 22.
* La herramienta usa un parser propio: nunca evalúa texto del usuario como código.
* Las trazas guardan un hash del id del chat, no el id ni el nombre del usuario.

## Licencia

Código: MIT. Los documentos del corpus conservan su licencia original (ver `corpus/abierto/*/LICENSE*`).
