---
status: aceptada
date: 2026-11-23
decision-makers: Rafael Páez Martínez
---

# ADR 0003. Criterio de la lógica de decisión del agente

## Context and Problem Statement

En cada consulta el agente debe decidir si recupera documentos, ejecuta la herramienta de disponibilidad o
responde directamente, y cada decisión debe quedar en trazas. El ciclo de decisión debe estar escrito por el
estudiante (no puede venir de un agente prefabricado) y debe poder explicarse línea por línea. ¿Con qué criterio
se toma la decisión?

## Decision Drivers

* Explicabilidad: cada decisión debe poder justificarse con una regla concreta.
* Determinismo: la misma pregunta debe producir la misma decisión (necesario para comparar versiones).
* Robustez: si el modelo por API falla, el agente debe seguir funcionando.
* Costo y latencia: evitar una llamada a un modelo cuando no hace falta.
* Capacidad de corregirse: detectar decisiones incoherentes antes de ejecutarlas.

## Considered Options

* Dejar que el modelo decida con *function calling* (el modelo elige la herramienta).
* Clasificación solo con un modelo por API.
* Clasificación híbrida: reglas explícitas primero, modelo por API solo si las reglas dudan, tabla de decisión fija y reglas de verificación.

## Decision Outcome

Opción elegida: **clasificación híbrida con tabla de decisión y verificación**, porque es la única que cumple a la vez
explicabilidad, determinismo y robustez. El ciclo está en `app/agent/agente.py`:

1. **Clasificar** (`app/agent/clasificador.py`). Cada tipo tiene reglas con pesos (expresiones regulares sobre el
   texto en minúsculas y sin tildes). Gana un tipo si tiene **al menos 2 puntos y supera al segundo por 1 o más**.
   Si no, se consulta al modelo por API con salida JSON restringida a las 6 categorías. Si el modelo no responde,
   se usa un valor por defecto: `fuera_de_dominio` si no hay vocabulario del dominio, si no `conceptual`.
2. **Decidir** con una tabla fija: `conceptual`, `seleccion`, `compromisos` → **rag**; `calculo` → **herramienta**;
   `saludo`, `fuera_de_dominio` → **directa**.
3. **Verificar** con dos reglas de corrección:
   * Se decidió *herramienta* pero la pregunta no trae ningún valor numérico → se corrige a *rag*
     (ej.: "¿Cómo se calcula la disponibilidad en serie?" es conceptual).
   * Se decidió otra cosa pero la pregunta trae una expresión `serie(...)`/`paralelo(...)` → se corrige a *herramienta*.
4. **Ejecutar.** *rag*: recupera k = 5 fragmentos y descarta los que no superan el umbral; si no queda ninguno,
   responde "sin evidencia" sin llamar al modelo. *herramienta*: usa la expresión escrita por el usuario o pide al
   modelo que la extraiga; si la expresión extraída es inválida, reintenta una vez pasando el error al modelo.
   *directa*: respuesta fija, sin modelo.
5. **Redactar** con el prompt de sistema fijo, los ejemplos del tipo (si el few-shot está activo), los fragmentos y el
   resultado de la herramienta.
6. **Revisar** que las citas de la respuesta existan entre los fragmentos entregados (queda en la traza).

### Consequences

* Bueno, porque en la mayoría de preguntas típicas la decisión la toman las reglas: es gratis, instantánea y explicable.
* Bueno, porque las trazas muestran qué regla se activó, con qué puntaje, y si hubo corrección.
* Bueno, porque el agente sigue funcionando sin API (solo reglas y expresiones explícitas).
* Malo, porque las reglas requieren mantenimiento: una pregunta nueva mal clasificada exige ajustar un patrón.
  Cada ajuste se documenta en las trazas de corrección.
* Malo, porque una pregunta que mezcla tipos (p. ej. compromiso con cálculo) se resuelve con una sola acción.

### Confirmation

`tests/test_agente.py` prueba las reglas, la corrección "cálculo sin números → rag", la corrección
"expresión explícita → herramienta", el error de topología y que la respuesta directa no llame al modelo.
`scripts/generar_trazas_demo.py` deja 12 trazas reales, incluida una decisión incorrecta y su corrección.

## Pros and Cons of the Options

### Function calling

* Bueno, porque el modelo maneja preguntas ambiguas con flexibilidad.
* Malo, porque la decisión queda dentro del modelo: no se puede explicar línea por línea ni es determinista, y el enunciado exige que el ciclo lo escriba el estudiante.

### Solo modelo por API

* Bueno, porque generaliza mejor que las reglas.
* Malo, porque cada pregunta paga una llamada externa y, si la API cae, el agente no decide.

### Híbrida (elegida)

* Bueno, porque combina lo explicable de las reglas con la cobertura del modelo.
* Malo, porque hay dos mecanismos que mantener.

## More Information

El few-shot dinámico reutiliza esta misma clasificación para elegir los ejemplos del banco (criterio por defecto),
lo cual es distinto de la recuperación del RAG: los ejemplos se eligen por tipo de pregunta, los fragmentos por similitud.
