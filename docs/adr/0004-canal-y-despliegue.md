---
status: aceptada
date: 2026-11-23
decision-makers: Rafael Páez Martínez
---

# ADR 0004. Canal de mensajería y despliegue

## Context and Problem Statement

El agente debe atender por Telegram o Slack con sus API oficiales y estar desplegado de forma permanente en un VPS
distinto del equipo del estudiante, con Docker y Docker Compose. Se cuenta con el crédito de Azure for Students.
¿Qué canal, qué modo de conexión y qué infraestructura se usan?

## Decision Drivers

* No depender de dominio, IP pública fija ni certificado TLS.
* Costo dentro del crédito disponible y requisitos mínimos de la Ruta 1 (4 vCPU, 8 GB de RAM).
* Reproducibilidad: levantar todo con un solo comando.
* Seguridad: ningún secreto en el repositorio y ningún puerto expuesto innecesariamente.

## Considered Options

* Telegram con long polling.
* Telegram con webhook (requiere URL pública con HTTPS).
* Slack con Socket Mode.

Para la infraestructura: Azure VM Standard_B4als_v2 (4 vCPU, 8 GB), Azure VM B2als_v2 (2 vCPU, 4 GB) y Azure Container Apps.

## Decision Outcome

Opción elegida: **Telegram con long polling en una Azure VM Standard_B4als_v2 con Ubuntu 24.04, Docker Compose y
Ollama en el mismo host**, porque long polling solo hace conexiones salientes (sin dominio ni certificado) y la VM
cumple el mínimo de la Ruta 1 dentro del crédito.

### Consequences

* Bueno, porque el único puerto abierto en el grupo de seguridad de red es el 22 (SSH); el bot y Ollama no exponen puertos.
* Bueno, porque `docker compose --profile ruta1 up -d` levanta todo, y `restart: unless-stopped` lo recupera tras un reinicio.
* Bueno, porque el bot muestra "escribiendo…" mientras el modelo trabaja en CPU.
* Malo, porque una VM B-series acumula créditos de CPU: con uso sostenido puede bajar a su rendimiento base. Para la sustentación se mide la latencia real.
* Malo, porque un único VPS es un punto único de falla; aceptable para un prototipo académico.

### Confirmation

Evidencias en `evidencias/`: `docker compose ps`, características del VPS (`nproc`, `free -h`), captura de la
conversación en Telegram y trazas generadas en el VPS.
