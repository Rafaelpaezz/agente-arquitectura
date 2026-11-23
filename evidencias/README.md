# Evidencias

| Entregable | Archivo | Cómo se genera |
|---|---|---|
| 5. Tabla top-k del RAG | `recuperacion_top_k.md` | `python -m scripts.evaluar_recuperacion` (en el VPS, con fastembed) |
| 6. Trazas de 10+ conversaciones | `trazas/trazas_demo.md` y `.jsonl` | `python -m scripts.generar_trazas_demo` + `trazas/` del bot real |
| 6. Decisión incorrecta y su corrección | `trazas/trazas_demo.md` (DEMO-05 y DEMO-06) | Idem |
| 7. Tabla de las 10 preguntas | `comparacion_fewshot.md` / `comparacion_modelo.md` | `python -m scripts.comparar --modo ...` |
| 8. Evidencia del fine-tuning | `finetune/curva_perdida.png`, `configuracion.json`, `historial_entrenamiento.csv`, `muestras_validacion.md` | Notebook `notebooks/finetune_qlora_qwen2.5_3b.ipynb` |
| 8. Latencia y VPS | `comparacion_modelo.md` + `vps_caracteristicas.txt` | Ver `docs/despliegue_azure.md` §6 |
| Separación de datos | `separacion_datos.md` | `python -m scripts.verificar_fuga` |
| 10. Uso del RAG y la herramienta | `trazas/` + capturas | Telegram + `/traza` |
| 11. Integración con Telegram | `capturas/telegram_*.png` | Capturas de pantalla del chat (incluya la del "escribiendo…") |
| 12. Despliegue en el VPS | `docker_compose_ps.txt`, `capturas/azure_vm.png` | `docker compose ps` y captura del portal |

Las capturas van en `capturas/`. No incluya en ninguna captura el token del bot ni llaves de API.
