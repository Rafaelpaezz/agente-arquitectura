# Trazas de demostración

## DEMO-01: Hola, ¿qué puedes hacer?

- Clasificación: **saludo** (método: reglas)
- Acción final: **directa**

```
Traza 1a9fa6b01277
• clasificar: tipo=saludo, metodo=reglas, razon=regla 'saludo' con 3 puntos (siguiente 0)
• decidir: tipo=saludo, accion=directa
• responder_directo: tipo=saludo
Latencias: clasificacion 0.002s, total 0.002s
```

<details><summary>Respuesta</summary>

¡Hola! Soy un agente de Arquitectura de Software. Puedo:
• explicar conceptos (con citas al corpus),
• ayudarte a elegir un estilo o patrón,
• analizar compromisos entre atributos de calidad,
• calcular disponibilidad compuesta, por ejemplo: serie(lb=99.99%, paralelo(app1=0.999, app2=0.999), db=0.9995)

Comandos: /ayuda, /fuentes, /traza.

</details>

## DEMO-02: ¿Qué es el patrón write-through?

- Clasificación: **conceptual** (método: reglas)
- Acción final: **rag**

```
Traza e3f308224516
• clasificar: tipo=conceptual, metodo=reglas, razon=regla 'conceptual' con 4 puntos (siguiente 0)
• decidir: tipo=conceptual, accion=rag
• recuperar: consulta=¿Qué es el patrón write-through?, k=5, umbral=0.4, mejor_puntaje=0.501, hay_evidencia=True
• armar_prompt: fewshot=False, criterio=None, fragmentos=5, herramienta=False, modelo=arqui-qwen2.5-3b-ft
• revisar_citas: sin_citas=False
Latencias: clasificacion 0.0s, recuperacion 0.013s, redaccion 49.004s, total 49.017s
```

<details><summary>Respuesta</summary>

**Respuesta:** Es un patrón de cache que sincroniza la escritura en la caché con la base de datos.
**Explicación:**
- Write-through es una técnica de cache que sincroniza la escritura en la caché con la base de datos, asegurando que los cambios se realicen en ambos lugares. [SDP, §Cache > When to update the cache > Write-through]
- Es una técnica de cache que garantiza que los cambios se realicen en la caché y en la base de datos. [SDP, §Cache > When to update the cache > Write-through > Disadvantage(s): write through]
**Fuentes:** [SDP, §Cache > When to update the cache > Write-through]; [SDP, §Cache > When to update the cache > When to use cache-aside and write-through]; [ARC42, §Conceptos Transversales (Cross-cutting)]; [ARC42, §Glosario]

</details>

## DEMO-03: Necesito servir archivos estáticos a usuarios de varios continentes, ¿qué me recomiendas?

- Clasificación: **seleccion** (método: reglas)
- Acción final: **rag**

```
Traza 9de66b44f0c6
• clasificar: tipo=seleccion, metodo=reglas, razon=regla 'seleccion' con 3 puntos (siguiente 0)
• decidir: tipo=seleccion, accion=rag
• recuperar: consulta=Necesito servir archivos estáticos a usuarios de varios continentes, ¿qué me recomiendas?, k=5, umbral=0.4, mejor_puntaje=0.449, hay_evidencia=True
• armar_prompt: fewshot=False, criterio=None, fragmentos=5, herramienta=False, modelo=arqui-qwen2.5-3b-ft
• revisar_citas: sin_citas=False
Latencias: clasificacion 0.0s, recuperacion 0.06s, redaccion 45.721s, total 45.781s
```

<details><summary>Respuesta</summary>

**Respuesta:** Telegram con webhook (requiere URL pública con HTTPS).
**Explicación:**
- La opción con webhook permite un enlace seguro y no requiere una URL pública externa.
- Los archivos estánticos son más rápidos que el webhook, pero el webhook es más seguro.
- El webhook se conecta a través de HTTPS, lo que garantiza la seguridad del enlace.
- Los usuarios de varios continentes pueden tener problemas con las conexiones públicas.
**Fuentes:** [ADR-AGENTE, §ADR 0004. Canal de mensajería y despliegue > Considered Options], [SRE, p. 5].
RESULTADO DE LA HERRAMIENTA: No se menciona en los fragmentos.

</details>

## DEMO-04: ¿Qué se gana y qué se pierde al desnormalizar una base de datos?

- Clasificación: **conceptual** (método: llm)
- Acción final: **rag**

```
Traza a40fef203d89
• clasificar: tipo=conceptual, metodo=llm, razon=Pregunta sobre definición y efectos de desnormalizar
• decidir: tipo=conceptual, accion=rag
• recuperar: consulta=¿Qué se gana y qué se pierde al desnormalizar una base de datos?, k=5, umbral=0.4, mejor_puntaje=0.679, hay_evidencia=True
• armar_prompt: fewshot=False, criterio=None, fragmentos=5, herramienta=False, modelo=arqui-qwen2.5-3b-ft
• revisar_citas: sin_citas=False
Latencias: clasificacion 0.227s, recuperacion 0.023s, redaccion 36.917s, total 37.167s
```

<details><summary>Respuesta</summary>

**Respuesta:** Se duplica la información y puede ser más compleja. Se puede mejorar el rendimiento con menos repeticiones.
**Explicación:**
- Data is duplicated. (SDP, §Database > Relational database management system (RDBMS) > Denormalization > Disadvantage(s): denormalization)
- Constraints can help redundant copies of information stay in sync, which increases complexity of the database design. (SDP, §Database > Relational database management system (RDBMS) > Denormalization > Disadvantage(s): denormalization)
**Fuentes:** [SDP, §Database > Relational database management system (RDBMS) > Denormalization > Disadvantage(s): denormalization]

</details>

## DEMO-05: ¿Cómo se calcula la disponibilidad en serie?

- Clasificación: **calculo** (método: reglas)
- Acción final: **rag**
- Corrección: herramienta → rag (se clasificó como cálculo pero la pregunta no trae valores numéricos)

```
Traza 1145a1b22c5c
• clasificar: tipo=calculo, metodo=reglas, razon=regla 'calculo' con 2 puntos (siguiente 0)
• decidir: tipo=calculo, accion=herramienta
• corregir: de=herramienta, a=rag, motivo=se clasificó como cálculo pero la pregunta no trae valores numéricos
• recuperar: consulta=¿Cómo se calcula la disponibilidad en serie?, k=5, umbral=0.4, mejor_puntaje=0.702, hay_evidencia=True
• armar_prompt: fewshot=False, criterio=None, fragmentos=5, herramienta=False, modelo=arqui-qwen2.5-3b-ft
• revisar_citas: sin_citas=False
Latencias: clasificacion 0.0s, recuperacion 0.026s, redaccion 51.033s, total 51.059s
```

<details><summary>Respuesta</summary>

**Respuesta:** La disponibilidad se calcula como el producto de las disponibilidades individuales.
**Explicación:**
- La disponibilidad es la probabilidad de que un sistema funcione correctamente. [SDP, §Availability patterns > Availability in numbers]
- En lugar de usar métricas de uptime/downtime, se define en términos de éxito de las solicitudes. [SRE, p. 3]
- Se calcula como el porcentaje de solicitudes exitosas en un periodo de tiempo dado. [SRE, p. 3]
- La disponibilidad acumulada es la media ponderada de las disponibilidades individuales. [SDP, §Availability patterns > Availability in numbers]
**Fuentes:** [SDP, §Availability patterns > Availability in numbers]; [SRE, p. 3]; [SDP, §Availability patterns > Availability in numbers]

</details>

## DEMO-06: Explícame qué significa serie(api=99.9%, bd=99.95%)

- Clasificación: **calculo** (método: reglas)
- Acción final: **herramienta**

```
Traza fc255215ff73
• clasificar: tipo=calculo, metodo=reglas, razon=regla 'calculo' con 5 puntos (siguiente 3)
• decidir: tipo=calculo, accion=herramienta
• herramienta: intento=1, metodo=explicita, expresion=serie(api=99.9%, bd=99.95%), disponibilidad=0.9985005000000001
• recuperar: consulta=disponibilidad en serie y en paralelo, availability in sequence vs in parallel, k=2, umbral=0.4, mejor_puntaje=0.772, hay_evidencia=True
• armar_prompt: fewshot=False, criterio=None, fragmentos=2, herramienta=True, modelo=arqui-qwen2.5-3b-ft
• revisar_citas: sin_citas=False
Latencias: clasificacion 0.0s, herramienta 0.0s, recuperacion 0.033s, redaccion 12.47s, total 12.503s
```

<details><summary>Respuesta</summary>

**Respuesta:** Topología serie con una caída esperada de 13.14 horas al año.
**Explicación:**
- En serie, la disponibilidad total es el producto de las disponibilidades individuales.
- La disponibilidad total es menor que la disponibilidad más baja de los componentes.
- El eje más débil es el componente con la menor disponibilidad.
- Hay un único punto de falla en la cadena principal.
**Fuentes:** [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence > In sequence]

</details>

## DEMO-07: serie(api=99.9%, paralelo(bd1=99.5%, bd2=99.5%)

- Clasificación: **calculo** (método: reglas)
- Acción final: **herramienta_error**

```
Traza 419c3f2aa000
• clasificar: tipo=calculo, metodo=reglas, razon=regla 'calculo' con 5 puntos (siguiente 0)
• decidir: tipo=calculo, accion=herramienta
• herramienta: intento=1, metodo=explicita, expresion=serie(api=99.9%, paralelo(bd1=99.5%, bd2=99.5%), error=la expresión terminó antes de tiempo (¿falta cerrar un paréntesis?)
Latencias: clasificacion 0.0s, total 0.0s
```

<details><summary>Respuesta</summary>

**Respuesta:** No pude calcular la disponibilidad: la expresión terminó antes de tiempo (¿falta cerrar un paréntesis?).
**Explicación:**
- Escriba la topología con este formato, por ejemplo:
  serie(lb=99.99%, paralelo(app1=0.999, app2=0.999), db=0.9995)
- serie = todos son necesarios; paralelo = basta uno; kden(k, n, a) = k de n réplicas.
**Fuentes:** ninguna.

</details>

## DEMO-08: Tengo un balanceador de 99.99%, tres servidores de 99.5% en paralelo y una base de datos de 99.9%. ¿Qué disponibilidad tengo?

- Clasificación: **calculo** (método: reglas)
- Acción final: **herramienta**

```
Traza 779ad59d5813
• clasificar: tipo=calculo, metodo=reglas, razon=regla 'calculo' con 3 puntos (siguiente 1)
• decidir: tipo=calculo, accion=herramienta
• herramienta: intento=1, metodo=llm, expresion=serie(balanceador=99.99%, paralelo(servidor1=99.5%, servidor2=99.5%, servidor3=99.5%), base_datos=99.9%), disponibilidad=0.9988999751374875
• recuperar: consulta=disponibilidad en serie y en paralelo, availability in sequence vs in parallel, k=2, umbral=0.4, mejor_puntaje=0.772, hay_evidencia=True
• armar_prompt: fewshot=False, criterio=None, fragmentos=2, herramienta=True, modelo=arqui-qwen2.5-3b-ft
• revisar_citas: sin_citas=False
Latencias: clasificacion 0.0s, herramienta 0.0s, recuperacion 0.017s, redaccion 21.157s, total 21.371s
```

<details><summary>Respuesta</summary>

**Respuesta:** 99.8900 %.
**Explicación:**
- La disponibilidad total se calcula multiplicando las disponibilidades individuales, [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence > In sequence].
- El balanceador tiene una disponibilidad de 99.99%, y cada servidor y la base de datos tienen 99.5%.
- La disponibilidad total es entonces: 0.9999 * (0.995 * 0.995 * 0.995) * 0.999 = 0.998900.
- El eslabón más débil de la cadena principal es la base de datos, con una disponibilidad de 99.9%.
**Fuentes:** [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence > In sequence], [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence > In parallel].

</details>

## DEMO-09: ¿Por qué el agente usa FAISS con búsqueda exacta?

- Clasificación: **conceptual** (método: llm)
- Acción final: **rag**

```
Traza eebb6c105bd5
• clasificar: tipo=conceptual, metodo=llm, razon=Pregunta sobre explicación de uso de FAISS con búsqueda exacta
• decidir: tipo=conceptual, accion=rag
• recuperar: consulta=¿Por qué el agente usa FAISS con búsqueda exacta?, k=5, umbral=0.4, mejor_puntaje=0.522, hay_evidencia=True
• armar_prompt: fewshot=False, criterio=None, fragmentos=5, herramienta=False, modelo=arqui-qwen2.5-3b-ft
• revisar_citas: sin_citas=False
Latencias: clasificacion 0.214s, recuperacion 0.016s, redaccion 54.155s, total 54.386s
```

<details><summary>Respuesta</summary>

**Respuesta:** Porque las reglas y expresiones son fáciles de evaluar.
**Explicación:**
- Las reglas son simples, no requieren llamadas a modelos. [ADR-AGENTE, §ADR 0003. Criterio de la lógica de decisión del agente > Decision Outcome]
- Si una pregunta trae expresiones numéricas, se usa un modelo para extraerlas. [ADR-AGENTE, §ADR 0003. Criterio de la lógica de decisión del agente > Decision Outcome]
- La búsqueda exacta es más rápida y fiable que la aproximada. [ADR-AGENTE, §ADR 0003. Criterio de la lógica de decisión del agente > More Information]
**Fuentes:** [ADR-AGENTE, §ADR 0003. Criterio de la lógica de decisión del agente > Decision Outcome], [ADR-AGENTE, §ADR 0003. Criterio de la lógica de decisión del agente > More Information]

</details>

## DEMO-10: ¿Cuál es la capital de Francia?

- Clasificación: **fuera_de_dominio** (método: llm)
- Acción final: **directa**

```
Traza 10cc52d0d402
• clasificar: tipo=fuera_de_dominio, metodo=llm, razon=Pregunta geográfica, no relacionada con arquitectura de software
• decidir: tipo=fuera_de_dominio, accion=directa
• responder_directo: tipo=fuera_de_dominio
Latencias: clasificacion 0.358s, total 0.358s
```

<details><summary>Respuesta</summary>

Esa pregunta está fuera del tema de la asignatura (Arquitectura de Software), así que no la respondo. Pregúntame por estilos, patrones, atributos de calidad, decisiones de arquitectura o cálculos de disponibilidad.

</details>

## DEMO-11: ¿Qué es la computación cuántica topológica de Majorana?

- Clasificación: **conceptual** (método: reglas)
- Acción final: **sin_evidencia**

```
Traza 897803a53310
• clasificar: tipo=conceptual, metodo=reglas, razon=regla 'conceptual' con 3 puntos (siguiente 0)
• decidir: tipo=conceptual, accion=rag
• recuperar: consulta=¿Qué es la computación cuántica topológica de Majorana?, k=5, umbral=0.4, mejor_puntaje=0.347, hay_evidencia=False
• sin_evidencia: umbral=0.4
Latencias: clasificacion 0.0s, recuperacion 0.012s, total 0.012s
```

<details><summary>Respuesta</summary>

**Respuesta:** No encontré en el corpus de la asignatura información suficiente para responder con fuentes.
**Explicación:**
- Prefiero no responder de memoria: las respuestas de contenido deben basarse en documentos verificables.
- Puede reformular la pregunta o consultar /fuentes para ver qué documentos tengo indexados.
**Fuentes:** ninguna.

</details>

## DEMO-12: ¿Qué debe ir en la sección de riesgos y deuda técnica de arc42?

- Clasificación: **conceptual** (método: llm)
- Acción final: **rag**

```
Traza 7495f83f44b5
• clasificar: tipo=conceptual, metodo=llm, razon=Pregunta sobre definir contenido de sección de riesgos y deuda técnica
• decidir: tipo=conceptual, accion=rag
• recuperar: consulta=¿Qué debe ir en la sección de riesgos y deuda técnica de arc42?, k=5, umbral=0.4, mejor_puntaje=0.657, hay_evidencia=True
• armar_prompt: fewshot=False, criterio=None, fragmentos=5, herramienta=False, modelo=arqui-qwen2.5-3b-ft
• revisar_citas: sin_citas=False
Latencias: clasificacion 0.174s, recuperacion 0.017s, redaccion 65.467s, total 65.658s
```

<details><summary>Respuesta</summary>

**Respuesta:** Una lista ordenada por prioridad de riesgos y/o deuda técnica.
**Explicación:**
- La sección de riesgos y deuda técnica requiere una identificación sistemática y evaluación de riesgos y deuda técnica (SDP, §Riesgos y deuda técnica).
- Se deben identificar y categorizar como riesgo o no riesgo, sensibilidad o trato de punto, y agruparlos en tres listas.
- Se deben asociar con las altas prioridades de atributos de utilidad (ATAM, p. 42).
- Se deben identificar componentes, conectores, configuración y restricciones involucrados en cada escenario generado (ATAM, p. 42).
- Se deben identificar sensibilidad y trato de punto para cada escenario generado (ATAM, p. 42).
**Fuentes:** [ARC42, §Riesgos y deuda técnica]; [ATAM, p. 42]; [ATAM, p. 42]

</details>
