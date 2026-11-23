### CAL-013

**Esperado:**

**Respuesta:** La disponibilidad total es 98.9406 % (1.97 nueves), con una caída esperada de 3.87 días al año.
**Explicación:**
- Topología usada: serie(web=0.9995, api=0.99, bd=0.9999). En serie se multiplican las disponibilidades y en paralelo se calcula 1 − (1 − A1)(1 − A2)… [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence]
- Caída esperada: 3.87 días al año y 7.74 h al mes (resultado de la herramienta).
- Eslabón más débil de la cadena principal: api=0.99. Puntos únicos de falla: web, api, bd.
- Mejora sugerida: duplicar en paralelo 'api' sube la disponibilidad a 99.9300 %, porque la redundancia en paralelo la aumenta. [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence]
**Fuentes:** [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence]

**Modelo ajustado:**

**Respuesta:** 98.9406%.
**Explicación:**
- Topología: serie (web=0.9995, api=0.99, bd=0.9999).
- Disponibilidad total: 98.9406% (1.97 nueves).
- Caída esperada: 3.87 días al año, 7.74 h al mes.
- Eslabón más débil de la cadena principal: api=0.99 (99.0000%).
- Puntos únicos de falla: web, api, bd.
**Fuentes:** [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence].

### CAL-028

**Esperado:**

**Respuesta:** La disponibilidad total es 98.9538 % (1.98 nueves), con una caída esperada de 3.82 días al año.
**Explicación:**
- Topología usada: serie(gateway=0.9999, paralelo(serie(app_r1=0.998, bd_r1=0.9), serie(app_r2=0.998, bd_r2=0.9))). En serie se multiplican las disponibilidades y en paralelo se calcula 1 − (1 − A1)(1 − A2)… [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence]
- Caída esperada: 3.82 días al año y 7.64 h al mes (resultado de la herramienta).
- Eslabón más débil de la cadena principal: paralelo(serie(app_r1=0.998, bd_r1=0.9), serie(app_r2=0.998, bd_r2=0.9)). Puntos únicos de falla: gateway.
- Mejora sugerida: duplicar en paralelo 'gateway' sube la disponibilidad a 98.9637 %, porque la redundancia en paralelo la aumenta. [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence]
**Fuentes:** [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence]

**Modelo ajustado:**

**Respuesta:** Topología: serie(gateway=0.9999, paralelo(serie(app_r1=0.998, bd_r1=0.9), serie(app_r2=0.998, bd_r2=0.9))) y disponibilidad total: 98.9538 % (1.98 nueves).
**Explicación:**
- La disponibilidad total es 98.9538 % (1.98 nueves).
- La caída esperada es 3.82 días al año, 7.64 h al mes.
- El eje más débil es paralelo(serie(app_r1=0.998, bd_r1=0.9), serie(app_r2=0.998, bd_r2=0.9)) (98.9637 %).
- Hay un único punto de falla: gateway.
**Fuentes:** [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence]; [ADR-AGENTE, §ADR 0004. Canal de mensajería y despliegue > Decision Outcome].

### CAL-027

**Esperado:**

**Respuesta:** La disponibilidad total es 94.7700 % (1.28 nueves), con una caída esperada de 19.10 días al año.
**Explicación:**
- Topología usada: kden(3, 4, nodo=0.9). En serie se multiplican las disponibilidades y en paralelo se calcula 1 − (1 − A1)(1 − A2)… [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence]
- Caída esperada: 19.10 días al año y 38.21 h al mes (resultado de la herramienta).
- Eslabón más débil de la cadena principal: kden(3, 4, nodo=0.9). Puntos únicos de falla: ninguno.
- No quedan puntos únicos de falla: para subir más hay que mejorar el componente más débil o agregar más réplicas. [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence]
**Fuentes:** [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence]

**Modelo ajustado:**

**Respuesta:** Topología: kden(3, 4, nodo=0.9). Disponibilidad total: 94.7700 %.
**Explicación:**
- El clúster tiene 4 nodos idénticos de 90%. Topología: kden(3, 4, nodo=0.9).
- Caída esperada: 19.10 días al año, 38.21 h al mes.
- Eslabón más débil de la cadena principal: kden(3, 4, nodo=0.9) (94.7700 %).
- Puntos únicos de falla: ninguno.
**Fuentes:** [SDP, §Availability patterns > Availability in numbers > Availability in parallel vs in sequence]; [SDP, §Database > Relational database management system (RDBMS) > Denormalization].

### COM-022

**Esperado:**

**Respuesta:** La guía de Azure prioriza la estabilidad del cliente: los cambios de comportamiento van en una nueva versión.
**Explicación:**
- No se debe cambiar el comportamiento de una versión ya publicada; los cambios van en una nueva versión de la API. [MSAPI, §Azure Versioning Guidelines > Guidelines]
- Evitar romper una versión GA tiene prioridad sobre cumplir las guías o resolver errores del linter. [MSAPI, §Azure Versioning Guidelines > Guidelines]
**Fuentes:** [MSAPI, §Azure Versioning Guidelines > Guidelines]

**Modelo ajustado:**

**Respuesta:** La versión de una API debe ser estable para el cliente.
**Explicación:**
- Es importante que la API sea estable para el cliente para evitar cambios que puedan causar problemas. [MSAPI, §Azure Versioning Guidelines > Guidelines]
- Se deben revisar cambios que podrían afectar a los clientes, incluso si no están en la definición de la API. [MSAPI, §Azure Versioning Guidelines > Guidelines]
- Evitar cambios que rompan la API es prioritario sobre seguir las guías de API. [MSAPI, §Azure Versioning Guidelines > Guidelines]
- No se deben mantener características en versión previa por más de un año. [MSAPI, §Azure Versioning Guidelines > Guidelines]
**Fuentes:** [MSAPI, §Azure Versioning Guidelines > Guidelines]

### COM-014

**Esperado:**

**Respuesta:** No: más réplicas reparten las lecturas, pero aumentan el retraso de replicación y la carga de reproducir escrituras.
**Explicación:**
- Las réplicas atienden lecturas y descargan al maestro. [SDP, §Database > Relational database management system (RDBMS) > Master-slave replication]
- Cuantas más réplicas, más hay que replicar y mayor es el retraso de replicación; con muchas escrituras se saturan. [SDP, §Database > Relational database management system (RDBMS) > Master-master replication > Disadvantage(s): replication]
**Fuentes:** [SDP, §Database > Relational database management system (RDBMS) > Master-slave replication]; [SDP, §Database > Relational database management system (RDBMS) > Master-master replication > Disadvantage(s): replication]

**Modelo ajustado:**

**Respuesta:** No siempre es mejor.
**Explicación:**
- Hay pérdida de datos si el maestro falla antes de replicar los nuevos datos a otros nodos. [SDP, §Database > Relational database management system (RDBMS) > Master-slave replication]
- Las lecturas de los nodos de lectura pueden estar atascadas con la replicación de escrituras. [SDP, §Database > Relational database management system (RDBMS) > Master-slave replication]
- La mayor cantidad de lectores replicados lleva a mayor retraso de replicación. [SDP, §Database > Relational database management system (RDBMS) > Master-slave replication]
- Es más complejo escribir en el maestro. [SDP, §Database > Relational database management system (RDBMS) > Master-slave replication]
**Fuentes:** [SDP, §Database > Relational database management system (RDBMS) > Master-slave replication]

### CON-010

**Esperado:**

**Respuesta:** Tres nueves permiten unas 8 h 45 min de caída al año, unos 43 min al mes.
**Explicación:**
- Con 99.9 % la caída tolerada es de 8 h 45 min 57 s por año. [SDP, §Availability patterns > Availability in numbers > 99.9% availability - three 9s]
- Equivale a 43 min 49.7 s por mes, 10 min 4.8 s por semana y 1 min 26.4 s por día. [SDP, §Availability patterns > Availability in numbers > 99.9% availability - three 9s]
**Fuentes:** [SDP, §Availability patterns > Availability in numbers > 99.9% availability - three 9s]

**Modelo ajustado:**

**Respuesta:** 8h 45min 57s.
**Explicación:**
- **Downtime per year:** 8h 45min 57s [SDP, §Availability patterns > Availability in numbers > 99.9% availability - three 9s]
- **Downtime per month:** 43m 49.7s [SDP, §Availability patterns > Availability in numbers > 99.9% availability - three 9s]
- **Downtime per week:** 10m 4.8s [SDP, §Availability patterns > Availability in numbers > 99.9% availability - three 9s]
- **Downtime per day:** 1m 26.4s [SDP, §Availability patterns > Availability in numbers > 99.9% availability - three 9s]
**Fuentes:** [SDP, §Availability patterns > Availability in numbers > 99.9% availability - three 9s]

### CON-024

**Esperado:**

**Respuesta:** Es guardar en caché los datos como objetos, igual que en el código de la aplicación.
**Explicación:**
- La aplicación arma el conjunto de datos de la base en una instancia de clase o estructura de datos. [SDP, §Cache > Caching at the object level]
- Si cambian los datos subyacentes, se elimina el objeto de la caché; además permite procesamiento asíncrono. [SDP, §Cache > Caching at the object level]
**Fuentes:** [SDP, §Cache > Caching at the object level]

**Modelo ajustado:**

**Respuesta:** Es un método de almacenamiento donde se guarda la representación de datos de un objeto completo, no solo de sus propiedades individuales.
**Explicación:**
- Se asocia con la aplicación y se construye desde la base de datos en una instancia de clase o estructuras de datos. [SDP, §Cache > Caching at the object level]
- Se actualiza si cambia la base de datos. [SDP, §Cache > Caching at the object level]
- Se usa para procesos asíncronos. [SDP, §Cache > Caching at the object level]
**Fuentes:** [SDP, §Cache > Caching at the object level]

### CON-009

**Esperado:**

**Respuesta:** Se cuantifica con el tiempo en servicio (o fuera de servicio) como porcentaje, y se expresa en número de nueves.
**Explicación:**
- La disponibilidad se mide como porcentaje del tiempo en que el servicio está disponible. [SDP, §Availability patterns > Availability in numbers]
- Se suele expresar en número de nueves: un servicio con 99.99 % tiene cuatro nueves. [SDP, §Availability patterns > Availability in numbers]
**Fuentes:** [SDP, §Availability patterns > Availability in numbers]

**Modelo ajustado:**

**Respuesta:** Se mide en número de 9s.
**Explicación:**
- La disponibilidad se mide en número de 9s. [SDP, §Availability patterns > Availability in numbers]
- Un sistema con 99.99% de disponibilidad tiene cuatro 9s. [SDP, §Availability patterns > Availability in numbers]
**Fuentes:** [SDP, §Availability patterns > Availability in numbers]

### SEL-023

**Esperado:**

**Respuesta:** Un ADR con la plantilla MADR.
**Explicación:**
- MADR pide describir el contexto y el problema, idealmente en dos o tres oraciones o como pregunta. [MADR, §Plantilla > Context and Problem Statement]
- El resultado se escribe como 'Opción elegida: ..., porque ...', con su justificación. [MADR, §Plantilla > Decision Outcome]
- Se agregan las consecuencias, buenas y malas, de la decisión. [MADR, §Plantilla > Decision Outcome > Consequences]
**Fuentes:** [MADR, §Plantilla > Context and Problem Statement]; [MADR, §Plantilla > Decision Outcome]; [MADR, §Plantilla > Decision Outcome > Consequences]

**Modelo ajustado:**

**Respuesta:** Seleccionamos PostgreSQL porque es más seguro y confiable.
**Explicación:**
- Es más seguro y confiable, ya que tiene mejor soporte de seguridad y estándares (cita).
- Mejora la integridad de datos, ya que no permite insertar valores incorrectos (cita).
- Mejora la consistencia, ya que no permite insertar valores incorrectos (cita).
**Fuentes:** [MADR, §Plantilla > Decision Outcome]

### SEL-022

**Esperado:**

**Respuesta:** La plantilla arc42, empezando por la introducción y las metas de calidad.
**Explicación:**
- La sección de metas de calidad recoge las tres (hasta cinco) metas de calidad más importantes para las partes interesadas. [ARC42, §Introducción y Metas > Metas de Calidad]
- Luego conviene delimitar el alcance y contexto del sistema frente a sus usuarios y sistemas vecinos. [ARC42, §Alcance y Contexto del Sistema]
**Fuentes:** [ARC42, §Introducción y Metas > Metas de Calidad]; [ARC42, §Alcance y Contexto del Sistema]

**Modelo ajustado:**

**Respuesta:** La Plantilla Arc42.
**Explicación:**
- Es una plantilla que ayuda a documentar la arquitectura.
- Se puede usar para documentación de arquitectura.
- Incluye el alcance y contexto del sistema.
- Incluye las interfaces externas.
- Incluye las interfaces técnicas.
- Incluye las interfaces de dominio.
- Incluye las interfaces técnicas.
- Incluye las interfaces de comunicación.
- Incluye las interfaces de negocio.
- Incluye las interfaces técnicas.
- Incluye las interfaces de comunicación.
- Incluye las interfaces de dominio.
- Incluye las interfaces técnicas.
- Incluye las interfaces de comunicación.
- Incluye las interfaces de negocio.
- Incluye las interfaces técnicas.
- Incluye las interfaces de comunicación.
- Incluye las interfaces de dominio.
- Incluye las interfaces técnicas.
- Incluye las interfaces de comunicación.
- Incluye las interfaces de negocio.
- Incluye las interfaces técnicas.
- Incluye las interfaces de comunicación.
- Incluye las interfaces de dominio.
- Incluye las interfaces técnicas.
- Incluye las interfaces de comunicación.
- Incluye las interfaces de negocio.
- Incluye las interfaces técnicas.
- Incluye las interfaces de comunicación.
- Incluye las interfaces de dominio.
- Incluye las interfaces técnicas.
- Incluye las interfaces de comunicación.
- Incluye las interfaces de negocio.
- Incluye las interfaces técnicas.
- Incluye las interfaces de comunicación.
- Incluye las interfaces de dominio.
- Incluye las interfaces técnicas.
- Incluye las interfaces de comunicación.
- Incluye las interfaces de negocio.
- Incluye las interfaces técnicas.
- Incluye las interfaces de comunicación.
- Incluye las interfaces de dominio.
- Incluye las interfaces técnicas.
- Incluye las interfaces de comunicación.
- Incluye las interfaces de negocio.
- Incluye las interfaces técnicas.
- Incluye las interfaces de comunicación.
- Incluye las interfaces de dominio.
- Incluye las interfaces técnicas.
- Incluye las interfaces de comunicación.
- Incluye las interfaces de negocio.
- In
