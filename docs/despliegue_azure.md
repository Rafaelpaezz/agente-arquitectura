# Despliegue en Azure (Azure for Students)

Costo de referencia: una VM **Standard_B4als_v2** (4 vCPU, 8 GB) en Linux cuesta alrededor de **0,13 USD por hora**
en East US (~97 USD al mes si queda prendida 24/7). Del 26 de noviembre a la sustentación son ~10 días: **~35 USD**
del crédito de 100 USD. Verifique el precio en la calculadora de Azure antes de crearla.

## 1. Crear la máquina virtual

1. Entre a https://portal.azure.com con la cuenta de Azure for Students.
2. **Crear un recurso → Máquina virtual**.
   * Grupo de recursos: `rg-agente-arquitectura` (nuevo).
   * Nombre: `vm-agente`. Región: **East US** (o la que tenga cupo).
   * Imagen: **Ubuntu Server 24.04 LTS – x64 Gen2**.
   * Tamaño: **Standard_B4als_v2** (4 vCPU, 8 GiB). Si sale "no disponible por cuota", pruebe otra región o
     `Standard_B4as_v2`. Para la Ruta 2 basta `Standard_B2als_v2`.
   * Autenticación: **clave pública SSH**, usuario `azureuser`. Descargue la clave `.pem` y guárdela bien.
   * Puertos de entrada: **solo SSH (22)**. El bot usa long polling y no necesita puertos abiertos.
3. Disco: SSD estándar de **64 GB** (el modelo y las imágenes Docker ocupan ~10 GB).
4. **Revisar y crear**. Anote la IP pública.

## 2. Alerta de presupuesto (para no gastarse el crédito)

**Cost Management → Presupuestos → Agregar**: 60 USD, con alertas al 50 % y al 90 % a su correo.

## 3. Preparar la VM

```bash
chmod 400 vm-agente_key.pem
ssh -i vm-agente_key.pem azureuser@IP_PUBLICA

# Docker y Compose
sudo apt-get update && sudo apt-get install -y ca-certificates curl git
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER && newgrp docker
docker compose version
```

## 4. Clonar y configurar

```bash
git clone https://github.com/SU_USUARIO/agente-arquitectura.git
cd agente-arquitectura
cp .env.example .env
nano .env        # TELEGRAM_BOT_TOKEN, DECISION_API_KEY y, para la Ruta 2, ANSWER_*
mkdir -p trazas evidencias
```

PDF no redistribuibles (opcional, ver `corpus/externo/README.md`), desde su PC:

```bash
scp -i vm-agente_key.pem corpus/externo/*.pdf azureuser@IP_PUBLICA:~/agente-arquitectura/corpus/externo/
```

## 5a. Levantar la Ruta 2 (modelo por API + few-shot)

En `.env`: `ANSWER_BASE_URL`, `ANSWER_API_KEY` y `ANSWER_MODEL` con los mismos valores de `DECISION_*`, y `FEWSHOT_ENABLED=on`.

```bash
docker compose up -d --build agente
docker compose logs -f agente     # debe decir "Índice listo" y "Bot iniciado con long polling"
```

## 5b. Levantar la Ruta 1 (modelo ajustado en Ollama)

1. Copie el GGUF del notebook a la VM:
   `scp -i vm-agente_key.pem arqui-qwen2.5-3b-ft.Q4_K_M.gguf azureuser@IP_PUBLICA:~/agente-arquitectura/deploy/ollama/`
2. En `.env`: `ANSWER_BASE_URL=http://ollama:11434/v1`, `ANSWER_MODEL=arqui-qwen2.5-3b-ft`, `FEWSHOT_ENABLED=off`.
3. Levante y registre los modelos:

```bash
docker compose --profile ruta1 up -d --build
docker compose --profile ruta1 exec ollama ollama create arqui-qwen2.5-3b-ft -f /modelfiles/Modelfile
docker compose --profile ruta1 exec ollama ollama pull qwen2.5:3b-instruct     # modelo base, para comparar
docker compose --profile ruta1 exec ollama ollama list
docker compose restart agente
```

## 6. Evidencias desde la VM

```bash
docker compose ps > evidencias/docker_compose_ps.txt
(nproc; lscpu | grep "Model name"; free -h; uname -a) > evidencias/vps_caracteristicas.txt
docker compose exec agente python -m scripts.evaluar_recuperacion
#   -> revise "umbral sugerido" en evidencias/recuperacion_top_k.md, póngalo en RAG_MIN_SCORE del .env
#      y reinicie: docker compose restart agente
docker compose exec agente python -m scripts.generar_trazas_demo
docker compose exec agente python -m scripts.comparar --modo fewshot                       # Ruta 2
docker compose exec agente python -m scripts.comparar --modo modelo \
    --modelo-base qwen2.5:3b-instruct --modelo-ajustado arqui-qwen2.5-3b-ft                 # Ruta 1
```

Los reportes quedan en la carpeta `evidencias/` de la VM (está montada en el contenedor). Cópielos a su PC con
`scp -r -i vm-agente_key.pem azureuser@IP_PUBLICA:~/agente-arquitectura/evidencias .` y súbalos al repositorio.

## 7. Apagar sin perder nada

* **Detener (desasignar)** la VM desde el portal deja de cobrar el cómputo (sigue cobrando el disco, centavos).
  Apagarla con `sudo shutdown` desde Linux **no** basta: sigue cobrando.
* El día de la sustentación: inicie la VM con 30 minutos de anticipación; los contenedores arrancan solos.
* Al terminar el semestre: elimine el grupo de recursos completo.
