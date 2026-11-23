# Documentos externos (no redistribuibles)

Estos documentos forman parte del corpus, pero su licencia **no permite subirlos al repositorio**.
Por eso esta carpeta está en `.gitignore` (salvo este README). Se publica la referencia completa
(en `corpus/fuentes.yaml`) y el procedimiento para cargarlos localmente.

## Procedimiento de carga local

1. Descargue cada documento desde su fuente oficial y guárdelo **con el nombre exacto** de esta tabla:

| id | Documento | Dónde obtenerlo | Nombre del archivo |
|----|-----------|-----------------|--------------------|
| ATAM | Kazman, Klein, Clements. *ATAM: Method for Architecture Evaluation*. CMU/SEI-2000-TR-004, 2000 | https://insights.sei.cmu.edu/library/atam-method-for-architecture-evaluation/ (descarga gratuita del PDF) | `ATAM_CMU-SEI-2000-TR-004.pdf` |
| ISO25010 | ISO/IEC 25010:2023, *Product quality model* | https://www.iso.org/standard/78176.html (compra, o la copia de la biblioteca de la universidad) | `ISO_IEC_25010_2023.pdf` |
| ISO42010 | ISO/IEC/IEEE 42010:2022, *Architecture description* | https://www.iso.org/standard/74393.html (compra, o la copia de la biblioteca de la universidad) | `ISO_IEC_IEEE_42010_2022.pdf` |
| SRE | Beyer et al. *Site Reliability Engineering*, cap. 3 y 4. O'Reilly/Google, 2016 | https://sre.google/sre-book/embracing-risk/ y https://sre.google/sre-book/service-level-objectives/ (en el navegador, *Imprimir → Guardar como PDF*, ambos capítulos en un solo PDF) | `SRE_cap3_cap4.pdf` |
| WAF | Microsoft. *Azure Well-Architected Framework*, pilares de confiabilidad y eficiencia del rendimiento | https://learn.microsoft.com/es-es/azure/well-architected/ (desde el menú de la página, *Descargar PDF*, o *Imprimir → Guardar como PDF*) | `Azure_Well_Architected.pdf` |

2. Copie los PDF en esta carpeta (`corpus/externo/`). En el VPS, súbalos con
   `scp corpus/externo/*.pdf usuario@IP:~/agente-arquitectura/corpus/externo/`.
3. Reindexe: `docker compose run --rm agente python -m scripts.ingest`
   (o `python -m scripts.ingest` en local).

El indexador lee los PDF página por página, así que las citas de estos documentos indican el
**número de página**. Si un archivo no está, el indexador lo informa y sigue con el resto:
el agente funciona igual, solo que sin esa fuente.
