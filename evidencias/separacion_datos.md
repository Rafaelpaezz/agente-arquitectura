# Verificación de separación entre entrenamiento y evaluación

Banco/dataset: 110 preguntas. Preguntas de prueba: 29. Umbral de alerta: 0.6.
Medidas: coseno TF-IDF de palabras (1-2 gramas) y de caracteres (3-5 gramas), sobre texto en minúsculas y sin tildes.

| Prueba | Conjunto | Pregunta | Pregunta del banco más parecida | Sim. palabras | Sim. caracteres | Estado |
|---|---|---|---|---|---|---|
| EV-01 | evaluación | ¿Qué es la consistencia eventual y en qué sistemas se ve? | CON-005: ¿Qué es la consistencia débil y dónde se usa? | 0.28 | 0.41 | ok |
| EV-02 | evaluación | En CAP, ¿qué implica escoger disponibilidad y tolerancia a particiones | CON-009: ¿Cómo se mide la disponibilidad de un sistema? | 0.02 | 0.15 | ok |
| EV-03 | evaluación | ¿Cómo funciona el failover activo-pasivo? | CON-007: ¿En qué consiste el failover activo-activo? | 0.45 | 0.51 | ok |
| EV-04 | evaluación | ¿Qué pasos sigue el patrón cache-aside al leer un dato? | CON-024: ¿Qué es la caché a nivel de objeto? | 0.06 | 0.15 | ok |
| EV-05 | evaluación | ¿Qué riesgo tiene write-behind frente a escribir de inmediato en la ba | COM-018: CDN: ¿rendimiento a cambio de qué riesgos? | 0.01 | 0.14 | ok |
| EV-06 | evaluación | ¿Qué es el sharding y qué ventajas da? | CON-011: ¿Qué es el DNS y cómo enruta el tráfico? | 0.20 | 0.07 | ok |
| EV-07 | evaluación | ¿Qué ofrecen Redis, RabbitMQ y Amazon SQS como colas de mensajes y qué | COM-023: Mensajes de error detallados: ¿ayuda al cliente o riesgo? | 0.05 | 0.16 | ok |
| EV-08 | evaluación | ¿Qué es back pressure y qué recibe el cliente cuando la cola se llena? | SEL-007: Mi base de datos recibe muchas más lecturas que escrituras.  | 0.06 | 0.15 | ok |
| EV-09 | evaluación | Quiero enviar el tráfico de video a unos servidores y el de facturació | SEL-005: Voy a tener varios servidores de aplicación idénticos. ¿Qué  | 0.11 | 0.32 | ok |
| EV-10 | evaluación | ¿Qué desventajas tiene RPC respecto al acoplamiento con el servicio? | COM-008: REST vs RPC: ¿acoplamiento o eficiencia? | 0.15 | 0.32 | ok |
| EV-11 | evaluación | ¿Dónde guarda una aplicación twelve-factor su configuración y por qué  | CON-029: ¿Qué propone twelve-factor sobre las dependencias? | 0.11 | 0.22 | ok |
| EV-12 | evaluación | ¿Por qué twelve-factor prohíbe las sticky sessions? | CON-029: ¿Qué propone twelve-factor sobre las dependencias? | 0.21 | 0.31 | ok |
| EV-13 | evaluación | ¿Qué significa que los procesos sean desechables en twelve-factor? | CON-018: ¿Qué significa ACID en bases de datos relacionales? | 0.17 | 0.26 | ok |
| EV-14 | evaluación | ¿Qué es el árbol de calidad en arc42? | CON-030: ¿Qué es la vista de despliegue en arc42? | 0.27 | 0.34 | ok |
| EV-15 | evaluación | ¿Qué tipos de escenarios de calidad distingue arc42? | CON-030: ¿Qué es la vista de despliegue en arc42? | 0.09 | 0.26 | ok |
| EV-16 | evaluación | ¿Qué decisiones se documentan en la sección de decisiones de diseño de | CON-023: ¿Qué es una base de datos orientada a documentos? | 0.03 | 0.21 | ok |
| EV-17 | evaluación | ¿Qué se escribe en la sección 'Decision Drivers' de un ADR con MADR? | CON-027: ¿Qué es un ADR? | 0.26 | 0.31 | ok |
| EV-18 | evaluación | Mi API tiene una operación que tarda minutos en completarse. ¿Qué patr | SEL-016: Generar un reporte tarda varios minutos y no quiero bloquear | 0.13 | 0.28 | ok |
| EV-19 | evaluación | ¿Cómo funciona la paginación dirigida por el servidor? | CON-009: ¿Cómo se mide la disponibilidad de un sistema? | 0.07 | 0.14 | ok |
| CMP-01 | comparación | En un sistema de pagos, ¿por qué podría no bastar con que las réplicas | CAL-017: Si replico 3 veces un servicio de un sistema de facturación  | 0.08 | 0.17 | ok |
| CMP-02 | comparación | Según twelve-factor, ¿qué debe pasar con un trabajo en curso cuando un | CON-028: Según twelve-factor, ¿cómo deben manejarse los logs? | 0.17 | 0.31 | ok |
| CMP-03 | comparación | En mi API, borrar un recurso tarda varios minutos. ¿Cómo debería respo | SEL-016: Generar un reporte tarda varios minutos y no quiero bloquear | 0.18 | 0.25 | ok |
| CMP-04 | comparación | Quiero repartir la tabla de usuarios en varias bases según la inicial  | SEL-009: Mis módulos de usuarios, foros y productos comparten una sol | 0.12 | 0.22 | ok |
| CMP-05 | comparación | Cache-aside o write-through: ¿cuál deja los datos más frescos y cuál p | COM-006: Write-through vs refresh-ahead: ¿qué atributos de calidad pr | 0.12 | 0.22 | ok |
| CMP-06 | comparación | Si mi sistema prefiere seguir respondiendo durante una partición de re | COM-001: ¿Qué se sacrifica al elegir consistencia fuerte en un sistem | 0.02 | 0.20 | ok |
| CMP-07 | comparación | La plataforma de matrículas de la universidad tiene un firewall de 99. | CAL-008: Para una plataforma de cursos virtuales tengo un balanceador | 0.33 | 0.35 | ok |
| CMP-08 | comparación | Un almacenamiento distribuido guarda los datos en 5 nodos de 97% y nec | SEL-013: Quiero guardar el carrito de compras temporal de los usuario | 0.06 | 0.27 | ok |
| CMP-09 | comparación | Calcula la disponibilidad de serie(cdn=99.99%, paralelo(serie(web1=99. | CAL-006: Calcula: serie(dns=99.99%, cdn=99.95%, paralelo(api1=99.5%,  | 0.44 | 0.53 | ok |
| CMP-10 | comparación | ¿Por qué cambiar el código de estado HTTP que devuelve un error de mi  | SEL-020: Quiero cambiar la base de datos local por una administrada e | 0.10 | 0.17 | ok |

Resultado: ninguna pregunta de evaluación o comparación supera el umbral de similitud con el banco.
