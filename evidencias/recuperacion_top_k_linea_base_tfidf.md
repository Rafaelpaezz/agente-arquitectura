# Evaluación de la recuperación — LÍNEA BASE léxica (TF-IDF), no es el modelo de producción

Modelo de embeddings: tfidf-char-3-5 (tfidf). Fragmentos indexados: 256. **k = 5**.
Acierto: alguno de los k fragmentos recuperados pertenece al documento y sección esperados (o a una subsección).

| Métrica | Valor |
|---|---|
| Preguntas | 19 |
| Fragmento correcto en la posición 1 | 13 de 19 (68%) |
| Fragmento correcto entre los 3 primeros | 13 de 19 (68%) |
| **Fragmento correcto entre los 5 primeros** | **16 de 19 (84%)** |
| MRR@5 | 0.718 |

## Calibración del umbral (RAG_MIN_SCORE)

* Puntaje máximo del 1.º fragmento en 5 preguntas fuera del corpus: **0.123**
* Puntaje mínimo del fragmento correcto en las preguntas acertadas: **0.097**
* Umbral configurado: 0.30 · umbral sugerido (punto medio): **0.11**

| Id | Pregunta | Fuente esperada | Posición del correcto | Puntaje del 1.º | 1.º recuperado |
|---|---|---|---|---|---|
| EV-01 | ¿Qué es la consistencia eventual y en qué sistemas se ve? | SDP §Consistency patterns > Eventual consistency | 1 | 0.312 | [SDP, §Consistency patterns > Eventual consistency] |
| EV-02 | En CAP, ¿qué implica escoger disponibilidad y tolerancia a p | SDP §m > AP - availability and partition tolerance | 5 | 0.155 | [SDP, §Availability vs consistency > CAP theorem > CP - cons |
| EV-03 | ¿Cómo funciona el failover activo-pasivo? | SDP §ability patterns > Fail-over > Active-passive | 1 | 0.215 | [SDP, §Availability patterns > Fail-over > Active-passive] |
| EV-04 | ¿Qué pasos sigue el patrón cache-aside al leer un dato? | SDP §ache > When to update the cache > Cache-aside | 1 | 0.202 | [SDP, §Cache > When to update the cache > Cache-aside > Disa |
| EV-05 | ¿Qué riesgo tiene write-behind frente a escribir de inmediat | SDP § update the cache > Write-behind (write-back) | 1 | 0.333 | [SDP, §Cache > When to update the cache > Write-behind (writ |
| EV-06 | ¿Qué es el sharding y qué ventajas da? | SDP §database management system (RDBMS) > Sharding | 1 | 0.208 | [SDP, §Database > Relational database management system (RDB |
| EV-07 | ¿Qué ofrecen Redis, RabbitMQ y Amazon SQS como colas de mens | SDP §Asynchronism > Message queues | 4 | 0.143 | [ADR-AGENTE, §ADR 0004. Canal de mensajería y despliegue > C |
| EV-08 | ¿Qué es back pressure y qué recibe el cliente cuando la cola | SDP §Asynchronism > Back pressure | 1 | 0.193 | [SDP, §Asynchronism > Back pressure] |
| EV-09 | Quiero enviar el tráfico de video a unos servidores y el de  | SDP §Load balancer > Layer 7 load balancing | 5 | 0.164 | [ARC42, §Vista de Despliegue] |
| EV-10 | ¿Qué desventajas tiene RPC respecto al acoplamiento con el s | SDP §e procedure call (RPC) > Disadvantage(s): RPC | 1 | 0.118 | [SDP, §Communication > Remote procedure call (RPC) > Disadva |
| EV-11 | ¿Dónde guarda una aplicación twelve-factor su configuración  | 12F §III. Config > Store config in the environment | 1 | 0.147 | [12F, §III. Config > Store config in the environment] |
| EV-12 | ¿Por qué twelve-factor prohíbe las sticky sessions? | 12F §te the app as one or more stateless processes | 1 | 0.352 | [12F, §VI. Processes > Execute the app as one or more statel |
| EV-13 | ¿Qué significa que los procesos sean desechables en twelve-f | 12F §tness with fast startup and graceful shutdown | no | 0.143 | [12F, §VI. Processes > Execute the app as one or more statel |
| EV-14 | ¿Qué es el árbol de calidad en arc42? | ARC42 §Requerimientos de Calidad > Árbol de Calidad | 1 | 0.349 | [ARC42, §Requerimientos de Calidad > Árbol de Calidad] |
| EV-15 | ¿Qué tipos de escenarios de calidad distingue arc42? | ARC42 §erimientos de Calidad > Escenarios de calidad | 1 | 0.280 | [ARC42, §Requerimientos de Calidad > Escenarios de calidad] |
| EV-16 | ¿Qué decisiones se documentan en la sección de decisiones de | ARC42 §Decisiones de Diseño | 1 | 0.300 | [ARC42, §Decisiones de Diseño] |
| EV-17 | ¿Qué se escribe en la sección 'Decision Drivers' de un ADR c | MADR §Plantilla > Decision Drivers | 1 | 0.277 | [MADR, §Plantilla > Decision Drivers] |
| EV-18 | Mi API tiene una operación que tarda minutos en completarse. | MSAPI § for Service Design > Long-Running Operations | no | 0.124 | [ARC42, §Estrategia de solución] |
| EV-19 | ¿Cómo funciona la paginación dirigida por el servidor? | MSAPI §ce Design > Pagination > Server-driven paging | no | 0.149 | [ADR-AGENTE, §ADR 0002. Estrategia de fragmentación e indexa |
