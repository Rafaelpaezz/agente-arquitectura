# Comparación (modelo): A = base: qwen2.5:3b-instruct · B = ajustado: arqui-qwen2.5-3b-ft

Criterio declarado antes de medir: docs/criterio_comparacion.md. Cada celda: formato / estructura / herramienta / citación (– = no aplica).
Máquina: a98716915f43 · 4 vCPU (AMD EPYC 7763 64-Core Processor) · 7931 MB RAM · Linux-7.0.0-1020-azure-x86_64-with-glibc2.41
Modelo de clasificación: openai/gpt-oss-20b. Prompt de sistema: idéntico en A y B. Fragmentos: idénticos en A y B.

| Id | Tipo | A: criterios | A: puntaje | B: criterios | B: puntaje | A: latencia (s) | B: latencia (s) |
|---|---|---|---|---|---|---|---|
| CMP-01 | conceptual | 1 / 1 / – / 0 | 0.67 | 1 / 1 / – / 0 | 0.67 | 0.0 | 0.0 |
| CMP-02 | conceptual | 1 / 0 / – / 1 | 0.67 | 1 / 1 / – / 1 | 1.00 | 114.0 | 85.2 |
| CMP-03 | seleccion | 1 / 0 / – / 1 | 0.67 | 1 / 0 / – / 1 | 0.67 | 86.4 | 57.4 |
| CMP-04 | conceptual | 1 / 0 / – / 1 | 0.67 | 1 / 1 / – / 1 | 1.00 | 77.0 | 39.9 |
| CMP-05 | conceptual | 1 / 1 / – / 1 | 1.00 | 1 / 1 / – / 1 | 1.00 | 49.0 | 33.5 |
| CMP-06 | compromisos | 1 / 0 / – / 1 | 0.67 | 1 / 1 / – / 1 | 1.00 | 54.0 | 35.3 |
| CMP-07 | calculo | 1 / 0 / 0 / 1 | 0.50 | 1 / 1 / 0 / 1 | 0.75 | 44.4 | 22.8 |
| CMP-08 | calculo | 1 / 0 / 0 / 1 | 0.50 | 1 / 1 / 1 / 1 | 1.00 | 25.9 | 19.4 |
| CMP-09 | calculo | 1 / 0 / 0 / 1 | 0.50 | 1 / 1 / 1 / 1 | 1.00 | 51.1 | 28.9 |
| CMP-10 | conceptual | 1 / 0 / – / 0 | 0.33 | 1 / 1 / – / 0 | 0.67 | 98.7 | 77.6 |

| Resumen | A | B |
|---|---|---|
| Formato | 10/10 | 10/10 |
| Estructura | 2/10 | 9/10 |
| Herramienta | 0/3 | 2/3 |
| Citacion | 8/10 | 8/10 |
| Puntaje promedio | 0.62 | 0.88 |
| Latencia promedio de redacción (s) | 66.72 | 44.45 |

Las respuestas completas están en el archivo .jsonl del mismo nombre.
