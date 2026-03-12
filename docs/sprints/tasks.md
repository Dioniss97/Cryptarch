# Tasks por prioridad (referencia / semilla)

**La fuente de verdad es Engram.** El estado de sprints y tasks, los criterios de aceptación y qué toca hacer viven en memorias `sprints/sprint-XX` y `tasks/task-XX`. Consultar siempre Engram primero (`mem_search` "Status: pending", "sprints sprint", etc.).

Este fichero sirve de **referencia** y de **semilla**: si Engram no tiene aún un sprint o sus tasks, se usa este doc (y el `sprint-XX.md` correspondiente) para crear o completar esas memorias. Una vez poblado, el agente trabaja desde Engram.

---

## Sprint 02 — Auth y Admin API (8 tareas)

Doc: `sprint-02-auth-admin-api.md`. Tasks: task-01 … task-08.

Orden de prioridad lógica (TDD: tests primero donde aplique).

| # | Task ID (ej.) | Descripción | Alcance |
|---|----------------|-------------|---------|
| 1 | task-01 | Auth local: login / logout | Endpoints, sesión o JWT, tests |
| 2 | task-02 | Comprobación de roles (admin vs user) | Middleware/guards, tests |
| 3 | task-03 | Tenant guards y scoping | Todo acceso a datos acotado por `tenant_id`, tests |
| 4 | task-04 | Admin CRUD usuarios | API CRUD users, tenant-scoped |
| 5 | task-05 | Admin CRUD tags | API CRUD tags |
| 6 | task-06 | Admin CRUD saved filters y groups | API CRUD filters + groups, bindings |
| 7 | task-07 | Admin CRUD connectors y actions | API CRUD connectors/actions (metadata) |
| 8 | task-08 | Admin CRUD documents (metadata) + tests E2E | Document metadata, tests de guards y tenant |

Criterios de aceptación: no-admin bloqueado en rutas admin; cross-tenant bloqueado; CRUD operativo para entidades core.

---

## Sprint 03 — Admin Web (5 tareas)

Doc: `sprint-03-admin-web.md`. Tasks: task-09 … task-13.

| # | Task ID (ej.) | Descripción | Alcance |
|---|----------------|-------------|---------|
| 1 | task-09 | Layout y menú admin | Rutas admin, navegación |
| 2 | task-10 | CRUD páginas: users, tags, filters, groups | Tablas, formularios, listados |
| 3 | task-11 | Tag picker y filter builder (AND de tags) | Componentes reutilizables, semántica AND |
| 4 | task-12 | Editor de bindings de grupo + formularios connector/action | Group bindings, forms conectores y acciones |
| 5 | task-13 | Badges de estado y manejo de errores en UI | Estados visibles, mensajes de error |

Criterios de aceptación: admin gestiona entidades desde UI; filter builder refleja semántica AND; errores visibles.

---

## Siguientes sprints (referencia)

- **Sprint 04 — Ingestión y vectorización**: upload, cola Redis, worker, extracción/chunking/embeddings, Qdrant, estados.
- **Sprint 05 — Chat, RAG y acciones**: chat usuario, RAG con scope de permisos, ejecución de acciones permitidas.
- **Sprint 06 — Hardening**: redacción, auditoría, métricas, revisión de rendimiento.

Las tasks concretas se desglosan (con prioridad) cuando se abra cada sprint; usar siempre `tasks/<id>` en Engram.
