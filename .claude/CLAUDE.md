# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Uso con Cursor**: Este repo está también configurado para Cursor. Contexto y reglas en `.cursor/rules/`, skills en `.cursor/skills/`, y guía de roles en `AGENTS.md`. En Cursor los flujos de sprint se piden en lenguaje natural (ej. "siguiente sprint", "inicia el sprint 02", "audita el sprint 01").

## What this repo is

A context-first scaffold for building a multi-tenant RAG + Actions SaaS platform. It contains project memory, sprint docs, subagents, and skills — but **no application code yet**. Claude Code generates the implementation from this contract.

**Product**: Admins manage users, groups, tags, filters, connectors, actions, and documents. Normal users only see a chat UI that queries allowed documents (RAG) and executes allowed actions (connectors), all scoped by tenant and group permissions.

## Tech stack & monorepo layout

| Path | Runtime | Purpose |
|---|---|---|
| `apps/api/` | Python 3.11 / FastAPI | Backend API. Layers: presentation, application, domain, infrastructure, tests |
| `apps/web/` | Node 20 / React | Admin panel + user chat UI. Admin and user routes separated |
| `workers/vectorizer/` | Python 3.11 | Redis queue worker: extraction, chunking, embeddings, Qdrant indexing |
| `packages/shared/` | — | Future shared contracts/constants |
| `infra/` | Docker Compose | Local dev environment |
| `docs/` | Markdown | Architecture, domain model, sprints, security notes |

## Infrastructure commands

```bash
# Start all services (Postgres 16, Redis 7, Qdrant, API, web, worker)
docker compose -f infra/docker-compose.dev.yml up -d

# Stop all services
docker compose -f infra/docker-compose.dev.yml down

# Copy env template
cp infra/.env.example .env
```

Default service ports: API `8000`, Web `3000`, Postgres `5432`, Redis `6379`, Qdrant `6333`/`6334`.

Default DB: `appdb` / `postgres` / `postgres`.

## Build & test commands (once app code exists)

```bash
# API (from apps/api/)
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
pytest                        # all tests
pytest tests/test_foo.py      # single file
pytest tests/test_foo.py::test_bar -v  # single test

# Web (from apps/web/)
npm install
npm run dev                   # dev server on :3000
npm test                      # all tests
npm test -- --grep "pattern"  # single test

# Worker (from workers/vectorizer/)
pip install -r requirements.txt
python worker.py
```

## Domain model (critical — read before changing any logic)

**Core rule**: Tags are metadata only. Permissions come from saved filters and group bindings.

1. Entities carry **tags** (users, actions, documents)
2. **SavedFilters** define selection logic (tag-based AND)
3. **Groups** bind saved filters (user filters + action filters + document filters)
4. Effective permissions for a user = **union** of permissions from all groups the user belongs to

Permission resolution: find groups whose user-filters match the user → union the actions from those groups' action-filters → union the documents from those groups' document-filters.

**Every structured entity is tenant-scoped** (`tenant_id`). Tenant filters are applied before permission filters.

## Non-negotiable rules

- `tenant_id` on every structured entity; enforce server-side, never trust client
- Tags are metadata only — never store permissions on tags directly
- Admin endpoints inaccessible to normal users
- Connector credentials stored separately from action definitions
- Follow TDD for critical backend logic
- When changing domain rules, update docs in the same change

## Ingestion pipeline (phase 1)

- Text-only extraction: PDF, TXT, CSV (no OCR)
- Statuses: `queued` → `processing` → `indexed` | `error`
- Flow: admin uploads → API creates metadata + enqueues Redis job → worker extracts/chunks/embeds → indexes to Qdrant → updates status

## Sprint workflow

Sprints are tracked in `docs/sprints/sprint-checklist.md`. Use these commands:

- `/sprint-next` — pick the next unchecked sprint
- `/sprint-start <sprint-id>` — load scope and begin implementation
- `/sprint-audit <sprint-id>` — verify acceptance criteria before marking complete

Build order: foundation → domain+schema → auth+admin API → admin UI → ingestion+vectorizer → chat+RAG+actions → hardening.

## Subagents

Use these specialized agents via the Task tool when their domain applies:

- **backend-architect** — FastAPI design, domain boundaries, tenancy enforcement, API shape
- **schema-reviewer** — Postgres schema, migrations, indexes, relational modeling
- **test-enforcer** — TDD discipline, tenancy boundary tests, permission computation tests
- **vector-pipeline-worker** — Ingestion pipeline, Redis queue, text extraction, chunking, embeddings, Qdrant
- **frontend-admin-builder** — React admin UI (referenced in skills)

## Skills

- `/fastapi-tdd` — TDD workflow for backend features (test-first, contracts, then implement)
- `/react-admin-slice` — Build/refine a React admin page with reusable patterns
- `/vectorization-pipeline` — Implement/review the document ingestion worker pipeline
- `/sprint-next`, `/sprint-start`, `/sprint-audit` — Sprint lifecycle management
