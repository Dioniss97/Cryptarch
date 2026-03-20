# Cryptarch Project Context Pack

This repository is a **context-first scaffold** for building a multi-tenant RAG + Actions platform using **FastAPI + React + Postgres + Qdrant + Redis workers**. It works with **Cursor**.

It intentionally focuses on:
- project memory (Engram + `.cursor/rules/` + `AGENTS.md`)
- reusable skills (`.cursor/skills/`)
- roles/agents (subagents en Cursor; guía en `AGENTS.md` en Cursor)
- sprint docs
- architecture/domain rules

It does **not** include full application code yet. The goal is to generate code consistently from a strong project contract.

## Uso con Cursor

Abre el proyecto en Cursor. Las reglas en `.cursor/rules/` y las skills en `.cursor/skills/` se aplican automáticamente. Para sprints, pide en lenguaje natural, por ejemplo:
- *"¿Cuál es el siguiente sprint?"* / *"Siguiente sprint"*
- *"Inicia el sprint 02"* / *"Sprint start sprint-02-auth-admin-api"*
- *"Audita el sprint 01"*

Consulta `AGENTS.md` para saber qué skill aplicar en cada tipo de tarea (backend, admin UI, ingestión, etc.).

## Flujo de trabajo (orquestador + Engram)

El orquestador coordina el ciclo de desarrollo con ayuda de subagentes y Engram:
- Pides en lenguaje natural “siguiente tarea” o “inicia el sprint X”.
- El orquestador consulta `sprints/*` y `tasks/<id>` (incluyendo el campo `Status`) en Engram y delega la ejecución a subagentes.
- Si toca implementación de código, se delega en `ai-worker`; si hace falta, se ejecuta `test-runner` (y en caso de fallo, `debugger` y re-ejecución).
- Cuando los tests pasan, se delega en `git-pr` para crear rama/commit/push y abrir o actualizar el PR.

Para más detalle: `docs/architecture/orchestrator-flow.md` y `docs/architecture/git-workflow.md`.

## Project objective

Build a multi-tenant SaaS where:
- **Admins** manage users, groups, tags, filters, connectors, actions, and documents.
- **Normal users** only see a **chat UI**.
- The chat can:
  - query only the documents allowed for the user's groups (RAG scope)
  - execute only the actions allowed for the user's groups (connector/action scope)

## Core authorization model (important)

Permissions are not stored directly on tags.

Instead:
1. Entities carry **tags** (`users`, `actions`, `documents`)
2. Admins create **saved filters** using tag AND logic
3. Groups bind to those saved filters:
   - one or more user filters
   - one or more action filters
   - one or more document filters
4. Effective permissions for a user = union of the permissions from all groups the user belongs to

## Primer uso con Cursor

1. Abre el repo en Cursor.
2. Asegúrate de revisar `AGENTS.md` para saber qué skill aplicar según el tipo de tarea (backend, admin UI, ingestión, etc.).
3. Verifica que las reglas en `.cursor/rules/` y las skills en `.cursor/skills/` están disponibles (se aplican automáticamente al abrir el proyecto).
4. Para elegir el siguiente sprint/tarea, pide en lenguaje natural, por ejemplo:
   - "¿Cuál es el siguiente sprint?" / "Siguiente sprint"
   - "Inicia el sprint 02" / "Inicia el sprint sprint-00-foundation"
