# Comparación (fewshot): A = sin ejemplos · B = con ejemplos

Criterio declarado antes de medir: docs/criterio_comparacion.md. Cada celda: formato / estructura / herramienta / citación (– = no aplica).
Máquina: Windows-10-10.0.26300-SP0
Modelo de clasificación: openai/gpt-oss-20b. Prompt de sistema: idéntico en A y B. Fragmentos: idénticos en A y B.

| Id | Tipo | A: criterios | A: puntaje | B: criterios | B: puntaje | A: latencia (s) | B: latencia (s) |
|---|---|---|---|---|---|---|---|
| CMP-01 | conceptual | 1 / 1 / – / 0 | 0.67 | 1 / 1 / – / 0 | 0.67 | 0.0 | 0.0 |
| CMP-02 | conceptual | 1 / 1 / – / 1 | 1.00 | 1 / 1 / – / 1 | 1.00 | 1.4 | 0.9 |
| CMP-03 | seleccion | 1 / 1 / – / 1 | 1.00 | 1 / 1 / – / 1 | 1.00 | 1.6 | 11.9 |
| CMP-04 | conceptual | 1 / 1 / – / 1 | 1.00 | 1 / 1 / – / 0 | 0.67 | 6.1 | 14.8 |
| CMP-05 | conceptual | 1 / 1 / – / 1 | 1.00 | 1 / 1 / – / 1 | 1.00 | 10.8 | 11.4 |
| CMP-06 | compromisos | 1 / 1 / – / 0 | 0.67 | 1 / 1 / – / 0 | 0.67 | 12.4 | 18.4 |
| CMP-07 | calculo | 1 / 1 / 0 / 0 | 0.50 | 1 / 1 / 1 / 1 | 1.00 | 5.5 | 17.7 |
| CMP-08 | calculo | 1 / 1 / 0 / 1 | 0.75 | 1 / 1 / 0 / 1 | 0.75 | 3.0 | 12.3 |
| CMP-09 | calculo | 1 / 1 / 1 / 1 | 1.00 | 1 / 0 / 1 / 1 | 0.75 | 4.4 | 21.2 |
| CMP-10 | conceptual | 1 / 1 / – / 1 | 1.00 | 1 / 1 / – / 1 | 1.00 | 14.2 | 19.8 |

| Resumen | A | B |
|---|---|---|
| Formato | 10/10 | 10/10 |
| Estructura | 10/10 | 9/10 |
| Herramienta | 1/3 | 2/3 |
| Citacion | 7/10 | 7/10 |
| Puntaje promedio | 0.86 | 0.85 |
| Latencia promedio de redacción (s) | 6.59 | 14.26 |

Las respuestas completas están en el archivo .jsonl del mismo nombre.
