---
status: aceptada
date: 2026-11-23
decision-makers: Rafael Páez Martínez
---

# ADR 0002. Estrategia de fragmentación e indexación del corpus

## Context and Problem Statement

Toda respuesta basada en el corpus debe indicar el documento y la sección o página de origen, y debe construirse
sobre los fragmentos recuperados. El corpus mezcla Markdown y AsciiDoc (con encabezados) y PDF (con páginas), en
inglés y en español, y las preguntas llegan en español. ¿Cómo se parte el corpus y cómo se indexa para recuperar
el fragmento correcto y poder citarlo con precisión?

## Decision Drivers

* Citabilidad: cada fragmento debe saber de qué documento y sección o página viene.
* Precisión de recuperación medible con el conjunto de evaluación (acierto en top-k).
* Recuperación entre idiomas: pregunta en español, documento en inglés.
* Costo cero y funcionamiento en CPU dentro del VPS.
* Simplicidad suficiente para explicarlo línea por línea.

## Considered Options

* Fragmentos de tamaño fijo (p. ej. 800 caracteres con solapamiento), sin mirar la estructura.
* Fragmentación por estructura (encabezados o páginas), con división por párrafos si la sección es larga.
* Fragmentación semántica (cortar donde cambia el tema según los embeddings).

Para el índice:

* FAISS `IndexFlatIP` (búsqueda exacta).
* FAISS HNSW o IVF (búsqueda aproximada).
* Chroma o Qdrant (bases vectoriales con servidor).

## Decision Outcome

Opción elegida: **fragmentación por estructura + FAISS `IndexFlatIP` + embeddings multilingües locales**, porque
es la única opción en la que la cita sale directamente de la estructura del documento, y porque con unos cientos
de fragmentos la búsqueda exacta es instantánea y no necesita ajustar parámetros.

Detalle (implementado en `app/rag/fragmentacion.py` y `app/rag/indice.py`):

1. **Markdown/AsciiDoc:** se corta en cada encabezado y se guarda la ruta completa de secciones
   (`Cache > When to update the cache > Write-through`). Esa ruta es la cita: `[SDP, §Cache > ... > Write-through]`.
2. **PDF:** se lee página por página; la cita es `[ATAM, p. 12]`.
3. Si una sección o página supera **1 500 caracteres**, se parte por párrafos con **un párrafo de solapamiento**
   (si es corto) para no cortar una idea.
4. Se descartan fragmentos de menos de **120 caracteres** y las secciones que solo son listas de enlaces
   ("Source(s) and further reading").
5. Al texto que se convierte en embedding se le antepone el título del documento y la ruta de secciones: así un
   fragmento corto se recupera por su tema aunque no repita las palabras clave.
6. **Embeddings:** `paraphrase-multilingual-MiniLM-L12-v2` con fastembed (ONNX, CPU, 384 dimensiones), porque
   ubica en el mismo espacio frases en español e inglés con significado parecido.
7. **Índice:** vectores normalizados en FAISS `IndexFlatIP`; producto interno = similitud coseno.
   **Ranking:** similitud semántica + un bono de 0,08 por cada término de la pregunta que aparece en el título
   de la sección (máximo 0,16). Motivo: en la primera prueba real, "¿Qué es el patrón write-through?" no
   recuperó la sección *Write-through*: el embedding multilingüe diluye el término técnico en inglés dentro de
   una frase en español, mientras que el título de la sección lo contiene literalmente.
8. **Compuerta de evidencia:** si el fragmento semánticamente más parecido no supera `RAG_MIN_SCORE`, el agente
   responde que no hay evidencia en lugar de usar el conocimiento propio del modelo; si lo supera, se entregan los
   k primeros del ranking. El valor se calibra con `scripts/evaluar_recuperacion.py`:
   punto medio entre el mayor puntaje de 5 preguntas fuera del corpus y el menor puntaje de un fragmento correcto.
9. El índice guarda una huella del corpus: al arrancar el contenedor solo se reindexa si el corpus cambió.

### Consequences

* Bueno, porque las citas son exactas y verificables: abrir el documento en la sección citada muestra el texto.
* Bueno, porque todo corre local, sin costo por consulta y sin depender de un servicio de embeddings.
* Malo, porque las secciones de tamaño muy desigual producen fragmentos desiguales; se mitiga con el corte por párrafos.
* Malo, porque `IndexFlatIP` crece linealmente; con más de ~100 000 fragmentos convendría HNSW. Este corpus tiene unos 230.
* Malo, porque los PDF escaneados sin texto no producen fragmentos; deben ser PDF con texto.

### Confirmation

`scripts/evaluar_recuperacion.py` mide, con k = 5, en cuántas de las preguntas del conjunto de evaluación el
fragmento de la sección esperada aparece entre los k primeros, además de acierto@1, acierto@3 y MRR.
El resultado queda en `evidencias/recuperacion_top_k.md`.

## Pros and Cons of the Options

### Tamaño fijo

* Bueno, porque es lo más simple de implementar.
* Malo, porque un fragmento puede mezclar dos secciones y la cita queda ambigua.

### Por estructura (elegida)

* Bueno, porque la cita es la sección del documento y el fragmento corresponde a una unidad de sentido.
* Malo, porque depende de que el documento tenga buenos encabezados.

### Semántica

* Bueno, porque los cortes siguen los cambios de tema.
* Malo, porque añade cálculo y es más difícil de explicar y de reproducir; no mejora la citabilidad.

### Chroma / Qdrant

* Bueno, porque traen filtrado por metadatos y persistencia.
* Malo, porque agregan un servicio más en un VPS con poca RAM, sin beneficio a esta escala.

## More Information

El backend `tfidf` (n-gramas de caracteres) se mantiene solo para las pruebas automáticas, que no deben descargar modelos.
