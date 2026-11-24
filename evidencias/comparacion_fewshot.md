# Comparación (fewshot): A = sin ejemplos · B = con ejemplos

Criterio declarado antes de medir: docs/criterio_comparacion.md. Cada celda: formato / estructura / herramienta / citación (– = no aplica).
Máquina: Windows-10-10.0.26300-SP0
Modelo de clasificación: openai/gpt-oss-20b. Prompt de sistema: idéntico en A y B. Fragmentos: idénticos en A y B.

| Id | Tipo | A: criterios | A: puntaje | B: criterios | B: puntaje | A: latencia (s) | B: latencia (s) |
|---|---|---|---|---|---|---|---|
| CMP-01 | conceptual | 1 / 1 / – / 0 | 0.67 | 1 / 1 / – / 0 | 0.67 | 0.0 | 0.0 |
| CMP-02 | conceptual | 1 / 1 / – / 1 | 1.00 | 1 / 1 / – / 1 | 1.00 | 0.6 | 1.0 |
| CMP-03 | seleccion | 1 / 0 / – / 1 | 0.67 | 1 / 1 / – / 1 | 1.00 | 0.8 | 20.5 |
| CMP-04 | conceptual | 1 / 0 / – / 1 | 0.67 | 0 / 0 / – / 1 | 0.33 | 9.2 | 19.1 |
| CMP-05 | conceptual | 1 / 1 / – / 1 | 1.00 | 1 / 1 / – / 0 | 0.67 | 7.2 | 17.1 |
| CMP-06 | compromisos | 1 / 0 / – / 0 | 0.33 | 1 / 1 / – / 0 | 0.67 | 11.9 | 21.4 |
| CMP-07 | calculo | 1 / 0 / 0 / 0 | 0.25 | 1 / 0 / 0 / 1 | 0.50 | 5.8 | 17.2 |
| CMP-08 | calculo | 1 / 1 / 1 / 0 | 0.75 | 1 / 1 / 1 / 1 | 1.00 | 6.8 | 15.9 |
| CMP-09 | calculo | 1 / 1 / 1 / 1 | 1.00 | 1 / 1 / 0 / 0 | 0.50 | 7.3 | 20.2 |
| CMP-10 | conceptual | 1 / 1 / – / 1 | 1.00 | 1 / 1 / – / 1 | 1.00 | 10.2 | 22.3 |

| Resumen | A | B |
|---|---|---|
| Formato | 10/10 | 9/10 |
| Estructura | 6/10 | 8/10 |
| Herramienta | 2/3 | 1/3 |
| Citacion | 6/10 | 6/10 |
| Puntaje promedio | 0.73 | 0.73 |
| Latencia promedio de redacción (s) | 6.63 | 17.20 |

Las respuestas completas están en el archivo .jsonl del mismo nombre.
