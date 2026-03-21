# Infraestructura local (Docker)

Aquí vive lo mínimo para levantar el entorno de desarrollo con Docker Compose: definición del stack y un ejemplo de variables de entorno.

## Qué hay en esta carpeta

| Archivo | Para qué sirve |
|--------|----------------|
| `docker-compose.dev.yml` | Stack de desarrollo: API, web, worker, Postgres, Redis y Qdrant. |
| `.env.example` | Plantilla de variables; el proyecto la copia a la raíz del repo como `.env` (ver abajo). |

## Levantar y parar el stack

Los comandos son los mismos que en el [README de la raíz del repositorio](../README.md#quick-start-docker-desktop):

**Arrancar en segundo plano**

```bash
docker compose -f infra/docker-compose.dev.yml up -d
```

**Ver estado**

```bash
docker compose -f infra/docker-compose.dev.yml ps
```

**Parar**

```bash
docker compose -f infra/docker-compose.dev.yml down
```

Ejecuta estos comandos desde la **raíz del repositorio** (donde está la carpeta `infra/`).

## Servicios, puertos y dependencias

En `docker-compose.dev.yml` aparecen estos servicios. Los puertos listados son los que el compose **publica en el host** (mapeo `host:contenedor`).

| Servicio | Imagen (referencia en compose) | Puertos en el host | Depende de (según `depends_on`) |
|----------|--------------------------------|--------------------|----------------------------------|
| **web** | `node:20-alpine` | `3000` | `api` |
| **api** | `python:3.11-slim` | `8000` | `postgres`, `redis`, `qdrant` |
| **worker** | `python:3.11-slim` | *(ninguno expuesto en el compose)* | `postgres`, `redis`, `qdrant` |
| **postgres** | `postgres:16` | `5432` | — |
| **redis** | `redis:7` | `6379` | — |
| **qdrant** | `qdrant/qdrant:latest` | `6333`, `6334` | — |

El compose define además volúmenes nombrados: `pgdata`, `qdrant_data` y `web_node_modules`.

Para **api** y **worker**, el fichero fija en `environment` (sin usar fichero `.env` del compose en el YAML que tenemos): `DATABASE_URL`, `REDIS_URL` y `QDRANT_URL` apuntando a los servicios `postgres`, `redis` y `qdrant` por nombre de servicio en la red de Compose.

## Variables de entorno

1. Copia el ejemplo a la **raíz del repo**:
   ```bash
   cp infra/.env.example .env
   ```
2. Ajusta valores sensibles (por ejemplo `JWT_SECRET`) en tu `.env` local; no lo subas al control de versiones si contiene secretos reales.

Las claves que aparecen en `infra/.env.example` son:

| Variable | Valor de ejemplo en el fichero |
|----------|-------------------------------|
| `APP_ENV` | `development` |
| `API_PORT` | `8000` |
| `JWT_SECRET` | `change-me` |
| `POSTGRES_DB` | `appdb` |
| `POSTGRES_USER` | `postgres` |
| `POSTGRES_PASSWORD` | `postgres` |
| `POSTGRES_HOST` | `postgres` |
| `POSTGRES_PORT` | `5432` |
| `REDIS_HOST` | `redis` |
| `REDIS_PORT` | `6379` |
| `QDRANT_HOST` | `qdrant` |
| `QDRANT_PORT` | `6333` |
| `QDRANT_COLLECTION` | `documents` |
| `EMBEDDINGS_PROVIDER` | `local` |

En el servicio **postgres** del compose, el propio YAML define `POSTGRES_DB`, `POSTGRES_USER` y `POSTGRES_PASSWORD` con los mismos valores por defecto que encajan con el ejemplo anterior.

## Quick start completo

Para requisitos, pasos detallados, URLs útiles y troubleshooting, sigue el **[README en la raíz del repositorio](../README.md)** (sección Quick Start con Docker Desktop).
