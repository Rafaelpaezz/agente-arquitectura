# Evaluación de la recuperación (RAG)

Modelo de embeddings: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (fastembed). Fragmentos indexados: 256. **k = 5**.
Ranking: similitud semántica + bono por términos de la pregunta en el título de la sección (máx. 0,16).
Acierto: alguno de los k fragmentos recuperados pertenece al documento y sección esperados (o a una subsección).

| Métrica | Valor |
|---|---|
| Preguntas | 19 |
| Fragmento correcto en la posición 1 | 12 de 19 (63%) |
| Fragmento correcto entre los 3 primeros | 17 de 19 (89%) |
| **Fragmento correcto entre los 5 primeros** | **18 de 19 (95%)** |
| MRR@5 | 0.759 |

## Calibración del umbral (RAG_MIN_SCORE)

* Puntaje máximo del 1.º fragmento en 5 preguntas fuera del corpus: **0.397**
* Mejor puntaje mínimo entre las 19 preguntas del conjunto de evaluación: **0.398**
* Umbral configurado: 0.38 · umbral sugerido (punto medio): **0.40**

| Id | Pregunta | Fuente esperada | Posición del correcto | Puntaje del 1.º | 1.º recuperado |
|---|---|---|---|---|---|
| EV-01 | ¿Qué es la consistencia eventual y en qué sistemas se ve? | SDP §Consistency patterns > Eventual consistency | 1 | 0.625 | [SDP, §Consistency patterns > Eventual consistency] |
| EV-02 | En CAP, ¿qué implica escoger disponibilidad y tolerancia a p | SDP §m > AP - availability and partition tolerance | 2 | 0.591 | [SDP, §Availability vs consistency > CAP theorem > CP - cons |
| EV-03 | ¿Cómo funciona el failover activo-pasivo? | SDP §ability patterns > Fail-over > Active-passive | 1 | 0.668 | [SDP, §Availability patterns > Fail-over > Active-passive] |
| EV-04 | ¿Qué pasos sigue el patrón cache-aside al leer un dato? | SDP §ache > When to update the cache > Cache-aside | 1 | 0.678 | [SDP, §Cache > When to update the cache > Cache-aside] |
| EV-05 | ¿Qué riesgo tiene write-behind frente a escribir de inmediat | SDP § update the cache > Write-behind (write-back) | 1 | 0.390 | [SDP, §Cache > When to update the cache > Write-behind (writ |
| EV-06 | ¿Qué es el sharding y qué ventajas da? | SDP §database management system (RDBMS) > Sharding | 1 | 0.359 | [SDP, §Database > Relational database management system (RDB |
| EV-07 | ¿Qué ofrecen Redis, RabbitMQ y Amazon SQS como colas de mens | SDP §Asynchronism > Message queues | no | 0.476 | [ADR-AGENTE, §ADR 0004. Canal de mensajería y despliegue > C |
| EV-08 | ¿Qué es back pressure y qué recibe el cliente cuando la cola | SDP §Asynchronism > Back pressure | 1 | 0.498 | [SDP, §Asynchronism > Back pressure] |
| EV-09 | Quiero enviar el tráfico de video a unos servidores y el de  | SDP §Load balancer > Layer 7 load balancing | 1 | 0.567 | [SDP, §Load balancer > Layer 7 load balancing] |
| EV-10 | ¿Qué desventajas tiene RPC respecto al acoplamiento con el s | SDP §e procedure call (RPC) > Disadvantage(s): RPC | 1 | 0.533 | [SDP, §Communication > Remote procedure call (RPC) > Disadva |
| EV-11 | ¿Dónde guarda una aplicación twelve-factor su configuración  | 12F §III. Config > Store config in the environment | 3 | 0.692 | [12F, §I. Codebase > One codebase tracked in revision contro |
| EV-12 | ¿Por qué twelve-factor prohíbe las sticky sessions? | 12F §te the app as one or more stateless processes | 3 | 0.437 | [12F, §IX. Disposability > Maximize robustness with fast sta |
| EV-13 | ¿Qué significa que los procesos sean desechables en twelve-f | 12F §tness with fast startup and graceful shutdown | 2 | 0.576 | [12F, §VIII. Concurrency > Scale out via the process model] |
| EV-14 | ¿Qué es el árbol de calidad en arc42? | ARC42 §Requerimientos de Calidad > Árbol de Calidad | 1 | 0.647 | [ARC42, §Requerimientos de Calidad > Árbol de Calidad] |
| EV-15 | ¿Qué tipos de escenarios de calidad distingue arc42? | ARC42 §erimientos de Calidad > Escenarios de calidad | 1 | 0.569 | [ARC42, §Requerimientos de Calidad > Escenarios de calidad] |
| EV-16 | ¿Qué decisiones se documentan en la sección de decisiones de | ARC42 §Decisiones de Diseño | 1 | 0.625 | [ARC42, §Decisiones de Diseño] |
| EV-17 | ¿Qué se escribe en la sección 'Decision Drivers' de un ADR c | MADR §Plantilla > Decision Drivers | 2 | 0.623 | [MADR, §Markdown Architectural Decision Records > Using MADR |
| EV-18 | Mi API tiene una operación que tarda minutos en completarse. | MSAPI § for Service Design > Long-Running Operations | 1 | 0.648 | [MSAPI, §Considerations for Service Design > Long-Running Op |
| EV-19 | ¿Cómo funciona la paginación dirigida por el servidor? | MSAPI §ce Design > Pagination > Server-driven paging | 4 | 0.543 | [SDP, §Cache > Web server caching] |
