# Trazas de demostración

## DEMO-01: Hola, ¿qué puedes hacer?

- Clasificación: **saludo** (método: reglas)
- Acción final: **directa**

```
Traza 75b76e1e1a13
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
Traza 04782e22e968
• clasificar: tipo=conceptual, metodo=reglas, razon=regla 'conceptual' con 4 puntos (siguiente 0)
• decidir: tipo=conceptual, accion=rag
• recuperar: consulta=¿Qué es el patrón write-through?, k=5, umbral=0.4, mejor_puntaje=0.5, hay_evidencia=True
• armar_prompt: fewshot=True, criterio=clasificacion, fragmentos=5, herramienta=False, modelo=openai/gpt-oss-120b
• revisar_citas: sin_citas=False
Latencias: clasificacion 0.0s, recuperacion 0.012s, redaccion 1.494s, total 1.506s
```

<details><summary>Respuesta</summary>

**Respuesta:** Write‑through es un patrón de caché en el que la aplicación escribe y actualiza los datos directamente en la caché y la caché, de forma síncrona, escribe la misma información en el almacén permanente (base de datos) antes de devolver la respuesta.  
**Explicación:**
- La aplicación realiza la operación de inserción/actualización en la caché y la caché se encarga de escribir de forma síncrona en la base de datos, devolviendo el control al llamador solo después de que la escritura persista. [SDP, §Cache > When to update the cache > Write-through]
- Este patrón garantiza que los datos en la caché nunca estén obsoletos, ya que siempre se reflejan en el almacén subyacente. [SDP, §Cache > When to update the cache > Write-through]
- La operación de escritura es más lenta porque incluye la escritura en la base de datos, pero las lecturas posteriores de los datos recién escritos son rápidas. [SDP, §Cache > When to update the cache > Write-through]
- Una desventaja es el mayor costo de latencia en escrituras y que nodos nuevos no tendrán datos en caché hasta que se actualicen en la base de datos; puede mitigarse combinando con cache‑aside. [SDP, §Cache > When to update the cache > Write-through > Disadvantage(s): write through]  
**Fuentes:**  
- [SDP, §Cache > When to update the cache > Write-through]  
- [SDP, §Cache > When to update the cache > Write-through > Disadvantage(s): write through]

</details>

## DEMO-03: Necesito servir archivos estáticos a usuarios de varios continentes, ¿qué me recomiendas?

- Clasificación: **seleccion** (método: reglas)
- Acción final: **rag**

```
Traza 532fff342ab0
• clasificar: tipo=seleccion, metodo=reglas, razon=regla 'seleccion' con 3 puntos (siguiente 0)
• decidir: tipo=seleccion, accion=rag
• recuperar: consulta=Necesito servir archivos estáticos a usuarios de varios continentes, ¿qué me recomiendas?, k=5, umbral=0.4, mejor_puntaje=0.448, hay_evidencia=True
• armar_prompt: fewshot=True, criterio=clasificacion, fragmentos=5, herramienta=False, modelo=openai/gpt-oss-120b
• revisar_citas: sin_citas=False
Latencias: clasificacion 0.0s, recuperacion 0.035s, redaccion 0.747s, total 0.783s
```

<details><summary>Respuesta</summary>

**Respuesta:** Utiliza una CDN (Content Delivery Network).  

**Explicación:**  
- Una CDN distribuye los archivos estáticos (imágenes, videos, etc.) en servidores ubicados cerca de los usuarios, reduciendo significativamente la latencia para clientes en diferentes continentes.  
- Al servir el contenido desde la CDN, tus servidores de origen no tienen que atender esas peticiones, lo que también disminuye la carga y mejora la disponibilidad.  
- Aunque implica costos y la necesidad de cambiar las URLs de los recursos estáticos, estos inconvenientes se compensan con la mejora de rendimiento y la experiencia de usuario global.  

**Fuentes:**  
- [SDP, §Content delivery network]  
- [SDP, §Content delivery network > Disadvantage(s): CDN]

</details>

## DEMO-04: ¿Qué se gana y qué se pierde al desnormalizar una base de datos?

- Clasificación: **conceptual** (método: llm)
- Acción final: **rag**

```
Traza 93e28b2c4e19
• clasificar: tipo=conceptual, metodo=llm, razon=Pregunta sobre definición y efectos de desnormalizar bases de datos
• decidir: tipo=conceptual, accion=rag
• recuperar: consulta=¿Qué se gana y qué se pierde al desnormalizar una base de datos?, k=5, umbral=0.4, mejor_puntaje=0.679, hay_evidencia=True
• armar_prompt: fewshot=True, criterio=clasificacion, fragmentos=5, herramienta=False, modelo=openai/gpt-oss-120b
• revisar_citas: sin_citas=False
Latencias: clasificacion 0.404s, recuperacion 0.031s, redaccion 1.545s, total 1.98s
```

<details><summary>Respuesta</summary>

**Respuesta:** Al desnormalizar se obtienen lecturas más rápidas y menos necesidad de joins, pero se paga con duplicación de datos, mayor complejidad para mantener la consistencia y peor rendimiento en escrituras intensas.  

**Explicación:**  
- La desnormalización duplica la información, lo que aumenta el espacio ocupado. [SDP, §Database > Relational database management system (RDBMS) > Denormalization > Disadvantage(s): denormalization]  
- Mantener sincronizadas las copias redundantes requiere restricciones y lógica adicional, incrementando la complejidad del diseño. [SDP, §Database > Relational database management system (RDBMS) > Denormalization > Disadvantage(s): denormalization]  
- Bajo alta carga de escrituras, una base desnormalizada puede rendir peor que una normalizada. [SDP, §Database > Relational database management system (RDBMS) > Denormalization > Disadvantage(s): denormalization]  
- Al eliminar la necesidad de joins (implícito en la denormalización y en la práctica de NoSQL), las consultas de lectura suelen ser más rápidas y simples.  

**Fuentes:**  
- [SDP, §Database > Relational database management system (RDBMS) > Denormalization > Disadvantage(s): denormalization]

</details>

## DEMO-05: ¿Cómo se calcula la disponibilidad en serie?

- Clasificación: **calculo** (método: reglas)
- Acción final: **rag**
- Corrección: herramienta → rag (se clasificó como cálculo pero la pregunta no trae valores numéricos)

```
Traza 8fda8a257548
• clasificar: tipo=calculo, metodo=reglas, razon=regla 'calculo' con 2 puntos (siguiente 0)
• decidir: tipo=calculo, accion=herramienta
• corregir: de=herramienta, a=rag, motivo=se clasificó como cálculo pero la pregunta no trae valores numéricos
• recuperar: consulta=¿Cómo se calcula la disponibilidad en serie?, k=5, umbral=0.4, mejor_puntaje=0.702, hay_evidencia=True
• armar_prompt: fewshot=True, criterio=clasificacion, fragmentos=5, herramienta=False, modelo=openai/gpt-oss-120b
• revisar_citas: sin_citas=False
Latencias: clasificacion 0.0s, recuperacion 0.026s, redaccion 4.98s, total 5.007s
```

<details><summary>Respuesta</summary>

**Respuesta:** La disponibilidad en serie se calcula multiplicando las disponibilidades de cada componente.  

**Explicación:**
- Cuando los componentes están en secuencia, la disponibilidad total disminuye porque todos deben estar operativos simultáneamente.  
- La fórmula es: **Disponibilidad (Total) = Disponibilidad (Foo) × Disponibilidad (Bar)**. [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence > In sequence]  
- Por ejemplo, si Foo y Bar tienen 99.9 % cada uno, la disponibilidad en serie es 0.999 × 0.999 = 0.998, es decir, 99.8 %. [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence > In sequence]  

**Fuentes:**  
- [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence > In sequence]

</details>

## DEMO-06: Explícame qué significa serie(api=99.9%, bd=99.95%)

- Clasificación: **calculo** (método: reglas)
- Acción final: **herramienta**

```
Traza 43e7e239e514
• clasificar: tipo=calculo, metodo=reglas, razon=regla 'calculo' con 5 puntos (siguiente 3)
• decidir: tipo=calculo, accion=herramienta
• herramienta: intento=1, metodo=explicita, expresion=serie(api=99.9%, bd=99.95%), disponibilidad=0.9985005000000001
• recuperar: consulta=disponibilidad en serie y en paralelo, availability in sequence vs in parallel, k=2, umbral=0.4, mejor_puntaje=0.772, hay_evidencia=True
• armar_prompt: fewshot=True, criterio=clasificacion, fragmentos=2, herramienta=True, modelo=openai/gpt-oss-120b
• revisar_citas: sin_citas=False
Latencias: clasificacion 0.0s, herramienta 0.0s, recuperacion 0.027s, redaccion 20.387s, total 20.414s
```

<details><summary>Respuesta</summary>

**Respuesta:** En una topología en serie, la disponibilidad total del servicio se obtiene multiplicando las disponibilidades de cada componente; por eso la disponibilidad del sistema con `api=99.9 %` y `bd=99.95 %` es 99.85 % (≈2.82 nueves), y cualquier falla en cualquiera de los dos componentes provoca la caída del servicio.

**Explicación:**
- En serie, el cálculo es **Availability Total = Availability (api) × Availability (bd)**, tal como indica el fragmento “In sequence” [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence > In sequence].
- Con `api=0.999` y `bd=0.9995`, la multiplicación da `0.999 × 0.9995 = 0.9985` → 99.8500 % de disponibilidad (2.82 nueves) (resultado de la herramienta).
- Cada componente es un **punto único de falla**: si la API o la base de datos falla, el servicio completo se interrumpe (puntos únicos de falla: api, bd).
- El **eslabón más débil** es la API (99.9 %), porque su disponibilidad es ligeramente menor que la de la base de datos.
- La **caída esperada** se traduce en 13.14 h al año (≈ 0.55 días) o 65.7 min al mes, derivada de la disponibilidad total calculada.

**Fuentes:**  
- [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence > In sequence]  
- Resultado de la herramienta (topología, disponibilidad total y caída esperada).

</details>

## DEMO-07: serie(api=99.9%, paralelo(bd1=99.5%, bd2=99.5%)

- Clasificación: **calculo** (método: reglas)
- Acción final: **herramienta_error**

```
Traza 2deeac752649
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
Traza 4ffb0a019f3b
• clasificar: tipo=calculo, metodo=reglas, razon=regla 'calculo' con 3 puntos (siguiente 1)
• decidir: tipo=calculo, accion=herramienta
• herramienta: intento=1, metodo=llm, expresion=serie(balanceador=99.99%, paralelo(servidor1=99.5%, servidor2=99.5%, servidor3=99.5%), base_datos=99.9%), disponibilidad=0.9988999751374875
• recuperar: consulta=disponibilidad en serie y en paralelo, availability in sequence vs in parallel, k=2, umbral=0.4, mejor_puntaje=0.772, hay_evidencia=True
• armar_prompt: fewshot=True, criterio=clasificacion, fragmentos=2, herramienta=True, modelo=openai/gpt-oss-120b
• revisar_citas: sin_citas=True
Latencias: clasificacion 0.0s, herramienta 0.0s, recuperacion 0.016s, redaccion 16.779s, total 17.273s
```

<details><summary>Respuesta</summary>

**Respuesta:** La disponibilidad total es 99.8900 % (2.96 nueves), con una caída esperada de 9.64 h al año.  
Los puntos únicos de falla son el balanceador y la base de datos.

</details>

## DEMO-09: ¿Por qué el agente usa FAISS con búsqueda exacta?

- Clasificación: **conceptual** (método: llm)
- Acción final: **rag**

```
Traza aedd07e39878
• clasificar: tipo=conceptual, metodo=llm, razon=Pregunta sobre explicación de uso de FAISS con búsqueda exacta
• decidir: tipo=conceptual, accion=rag
• recuperar: consulta=¿Por qué el agente usa FAISS con búsqueda exacta?, k=5, umbral=0.4, mejor_puntaje=0.522, hay_evidencia=True
• armar_prompt: fewshot=True, criterio=clasificacion, fragmentos=5, herramienta=False, modelo=openai/gpt-oss-120b
• revisar_citas: sin_citas=True
Latencias: clasificacion 0.671s, recuperacion 0.034s, redaccion 17.164s, total 17.869s
```

<details><summary>Respuesta</summary>

**Respuesta:** No se dispone de información en los fragmentos proporcionados que explique por qué el agente utiliza FAISS con búsqueda exacta.

</details>

## DEMO-10: ¿Cuál es la capital de Francia?

- Clasificación: **fuera_de_dominio** (método: llm)
- Acción final: **directa**

```
Traza 6ea97dcf8807
• clasificar: tipo=fuera_de_dominio, metodo=llm, razon=Pregunta geográfica, no relacionada con arquitectura de software
• decidir: tipo=fuera_de_dominio, accion=directa
• responder_directo: tipo=fuera_de_dominio
Latencias: clasificacion 0.286s, total 0.286s
```

<details><summary>Respuesta</summary>

Esa pregunta está fuera del tema de la asignatura (Arquitectura de Software), así que no la respondo. Pregúntame por estilos, patrones, atributos de calidad, decisiones de arquitectura o cálculos de disponibilidad.

</details>

## DEMO-11: ¿Qué es la computación cuántica topológica de Majorana?

- Clasificación: **conceptual** (método: reglas)
- Acción final: **sin_evidencia**

```
Traza 82e4ee7ea326
• clasificar: tipo=conceptual, metodo=reglas, razon=regla 'conceptual' con 3 puntos (siguiente 0)
• decidir: tipo=conceptual, accion=rag
• recuperar: consulta=¿Qué es la computación cuántica topológica de Majorana?, k=5, umbral=0.4, mejor_puntaje=0.347, hay_evidencia=False
• sin_evidencia: umbral=0.4
Latencias: clasificacion 0.0s, recuperacion 0.007s, total 0.007s
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
Traza e9640581ed9a
• clasificar: tipo=conceptual, metodo=llm, razon=Pregunta sobre definir contenido de sección de riesgos y deuda técnica
• decidir: tipo=conceptual, accion=rag
• recuperar: consulta=¿Qué debe ir en la sección de riesgos y deuda técnica de arc42?, k=5, umbral=0.4, mejor_puntaje=0.657, hay_evidencia=True
• armar_prompt: fewshot=True, criterio=clasificacion, fragmentos=5, herramienta=False, modelo=openai/gpt-oss-120b
• revisar_citas: sin_citas=False
Latencias: clasificacion 0.403s, recuperacion 0.013s, redaccion 13.394s, total 13.81s
```

<details><summary>Respuesta</summary>

**Respuesta:** Debe contener una lista de los riesgos técnicos y la deuda técnica identificada, ordenada por prioridad, y opcionalmente medidas sugeridas para mitigarlos o reducirlos.  
**Explicación:**
- La sección incluye “una lista de los riesgos técnicos o deuda técnica identificada, ordenada por prioridad”. [ARC42, §Riesgos y deuda técnica]
- Su motivación es permitir la detección sistemática y evaluación de riesgos y deuda técnica para la planificación y medición del proyecto. [ARC42, §Riesgos y deuda técnica]
- La forma recomendada es presentar la lista de riesgos y/o deuda técnica, pudiendo añadir medidas sugeridas para minimizar, mitigar o evitar los riesgos o reducir la deuda. [ARC42, §Riesgos y deuda técnica]  
**Fuentes:** [ARC42, §Riesgos y deuda técnica]

</details>
