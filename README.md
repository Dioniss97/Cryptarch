<h1 align="center">Cryptarch</h1>

<p align="center">
  <img src="docs/assets/cryptarch-banner.png" alt="Cryptarch banner" width="1024" />
</p>

<p align="center">
  <strong>Proyecto en desarrollo: SaaS multi-tenant RAG + Actions</strong><br>
  <em>Agent-first. Orquestador + subagentes. Desarrollo guiado por documentacion.</em>
</p>

<p align="center">
  <a href="#quick-start-docker-desktop">Quick Start</a> &bull;
  <a href="#como-se-trabaja-con-agentes">Agentes</a> &bull;
  <a href="#estructura-del-repositorio">Estructura</a> &bull;
  <a href="#documentacion-recomendada">Documentacion</a> &bull;
  <a href="#troubleshooting-rapido">Troubleshooting</a>
</p>

---

Cryptarch es un **proyecto en desarrollo** de plataforma SaaS multi-tenant con **RAG + Actions** (API, admin web, worker y stack con Docker).
La idea de producto es sencilla:
- admins gestionan usuarios, grupos, filtros, conectores y documentos;
- usuarios finales usan chat;
- el chat solo puede consultar documentos y ejecutar acciones permitidas por tenant y grupos.

El proyecto sigue un enfoque **agent-first**: se trabaja con un orquestador que coordina subagentes para implementar, testear y publicar cambios de forma consistente.

Si acabas de llegar, empieza por el Quick Start.

## Indice

- [Quick Start (Docker Desktop)](#quick-start-docker-desktop)
- [Que hace Cryptarch](#que-hace-cryptarch)
- [Como se trabaja con agentes](#como-se-trabaja-con-agentes)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Stack tecnico](#stack-tecnico)
- [Documentacion recomendada](#documentacion-recomendada)
- [Troubleshooting rapido](#troubleshooting-rapido)

## Quick Start (Docker Desktop)

La forma recomendada y mas simple de arrancar el proyecto es Docker Desktop.
Con un solo comando levantas API, web, worker y dependencias.

### Requisitos

- Docker Desktop instalado y en ejecucion.
- Git instalado.

### Arranque en 4 pasos

1. Clona el repositorio y entra en la carpeta:
   - `git clone <url-del-repo>`
   - `cd Cryptarch`
2. Copia variables de entorno:
   - `cp infra/.env.example .env`
3. Levanta todo el stack:
   - `docker compose -f infra/docker-compose.dev.yml up -d`
4. Verifica que los servicios estan en marcha:
   - `docker compose -f infra/docker-compose.dev.yml ps`

### Servicios principales

| Servicio | URL / Puerto | Uso |
|---|---|---|
| API | `http://localhost:8000` | Backend principal (FastAPI). |
| Web | `http://localhost:3000` | Frontend admin + chat. |
| Postgres | `localhost:5432` | Base de datos relacional. |
| Redis | `localhost:6379` | Cola/cache para procesos async. |
| Qdrant | `http://localhost:6333` | Base de datos vectorial (RAG). |

### Parar el entorno

- `docker compose -f infra/docker-compose.dev.yml down`

### Reinicio limpio (opcional)

Si quieres borrar volumenes locales y empezar desde cero:
- `docker compose -f infra/docker-compose.dev.yml down -v`

## Que hace Cryptarch

### Objetivo funcional

- Admins gestionan usuarios, grupos, tags, filtros guardados, conectores, acciones y documentos.
- Usuarios finales solo ven chat.
- El chat consulta solo documentos permitidos y ejecuta solo acciones permitidas por permisos efectivos de grupo.

### Modelo de autorizacion (resumen)

- Los tags son metadatos; no guardan permisos por si solos.
- Los permisos salen de `SavedFilters` + `Groups`.
- Permisos efectivos de un usuario = union de permisos de todos sus grupos.
- Todo es tenant-scoped (`tenant_id`).

## Como se trabaja con agentes

Cryptarch esta pensado para trabajar con jerarquia de agentes:

| Rol | Agente | Responsabilidad |
|---|---|---|
| Coordinacion | **Orquestador** | Coordina el flujo y decide el siguiente paso. |
| Implementacion | `ai-worker` | Implementacion de codigo y cambios funcionales. |
| Validacion | `test-runner` | Ejecucion de tests y reporte de resultados. |
| Correccion | `debugger` | Diagnostico/correccion cuando fallan tests. |
| Entrega | `git-pr` | Rama, commits, push y apertura/actualizacion de PR. |
| Analisis | `architecture-reviewer` | Revisiones de arquitectura/documentacion. |

### Activar modo orquestador en Cursor

En el chat de Cursor, escribe:
- `/orchestrator`

No hace falta escribir la ruta del fichero. Con `/` veras los comandos disponibles.

## Estructura del repositorio

| Ruta | Que contiene | Notas |
|---|---|---|
| [apps/api/](apps/api/README.md) | API FastAPI | Capas `presentation/application/domain/infrastructure/tests`. |
| [apps/web/](apps/web/README.md) | Frontend React | Admin + chat. |
| [workers/vectorizer/](workers/vectorizer/README.md) | Worker de ingestion/vectorizacion | Pipeline hacia Qdrant. |
| [packages/shared/](packages/shared/README.md) | Contratos y constantes compartidas | Reutilizable entre componentes. |
| [infra/](infra/README.md) | Infra local | Docker Compose y entorno de desarrollo. |
| [docs/](docs/) | Documentacion de arquitectura/dominio/sprints | Guia de contexto y alcance. |
| [.cursor/](.cursor/) | Config de trabajo con IA | Reglas, skills, agentes y comandos. |

## Stack tecnico

- Backend: Python 3.11 + FastAPI
- Frontend: React + Vite
- DB: Postgres 16
- Cola/cache: Redis 7
- Vector DB: Qdrant
- Infra local: Docker Compose

## Documentacion recomendada

Orden sugerido para entender el proyecto de menos a mas:

| Orden | Documento | Para que sirve |
|---|---|---|
| 1 | [README.md](README.md) | Punto de entrada: vision general y quick start. |
| 2 | [AGENTS.md](AGENTS.md) | Mapa de roles, skills y subagentes; cuando delegar y como. |
| 3 | [docs/architecture/orchestrator-flow.md](docs/architecture/orchestrator-flow.md) | Flujo operativo completo del orquestador con subagentes. |
| 4 | [docs/architecture/git-workflow.md](docs/architecture/git-workflow.md) | Convenciones de ramas/commits/PR y cierre de trabajo. |
| 5 | [docs/sprints/tasks.md](docs/sprints/tasks.md) | Backlog de referencia para priorizar y poblar Engram. |

## Troubleshooting rapido

### Un servicio no arranca

- Ver estado: `docker compose -f infra/docker-compose.dev.yml ps`
- Ver logs: `docker compose -f infra/docker-compose.dev.yml logs -f <service>`

Servicios comunes: `api`, `web`, `worker`, `postgres`, `redis`, `qdrant`.

### Puerto ocupado

Si `3000`, `8000`, `5432`, `6379` o `6333` estan ocupados:
- cierra el proceso local que use ese puerto, o
- cambia los puertos en `infra/docker-compose.dev.yml`.

### Primer arranque lento

Es normal: se instalan dependencias de Python y Node dentro de contenedores.
Los siguientes arranques suelen ser mas rapidos.
