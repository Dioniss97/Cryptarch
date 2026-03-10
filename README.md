# Claude Code Project Context Pack

This repository is a **context-first scaffold** for building a multi-tenant RAG + Actions platform using **FastAPI + React + Postgres + Qdrant + Redis workers**. It works with **Claude Code (CLI)** and with **Cursor**.

It intentionally focuses on:
- project memory (`.claude/CLAUDE.md`; en Cursor: `.cursor/rules/` + `AGENTS.md`)
- reusable skills (slash commands en Claude Code; skills en `.cursor/skills/` en Cursor)
- roles/agents (subagents en Claude Code; guía en `AGENTS.md` en Cursor)
- sprint docs
- architecture/domain rules

It does **not** include full application code yet. The goal is to generate code consistently from a strong project contract.

## Uso con Cursor

Abre el proyecto en Cursor. Las reglas en `.cursor/rules/` y las skills en `.cursor/skills/` se aplican automáticamente. Para sprints, pide en lenguaje natural, por ejemplo:
- *"¿Cuál es el siguiente sprint?"* / *"Siguiente sprint"*
- *"Inicia el sprint 02"* / *"Sprint start sprint-02-auth-admin-api"*
- *"Audita el sprint 01"*

Consulta `AGENTS.md` para saber qué skill aplicar en cada tipo de tarea (backend, admin UI, ingestión, etc.).

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

## Primer uso con Claude Code (CLI)

1. Abre el repo en terminal.
2. Inicia Claude Code.
3. Ejecuta `/memory` y comprueba que `.claude/CLAUDE.md` está cargado.
4. Ejecuta `/agents` y revisa los subagentes.
5. Ejecuta `/sprint-next` para elegir el siguiente sprint.
6. Ejecuta `/sprint-start sprint-00-foundation` para empezar.
