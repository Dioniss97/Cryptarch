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

## Sprint 02.5 — Backend puente para frontend dinámico (7 tareas)

Doc: `sprint-02-5-backend-bridge.md` (crear/actualizar en Engram). Tasks sugeridas: task-08a … task-08g.

Objetivo: desbloquear el frontend admin/chat con contratos backend estables para formularios dinámicos por acción, preferencias de usuario e inicio de ejecución segura de actions desde backend.

| # | Task ID (ej.) | Descripción | Alcance |
|---|----------------|-------------|---------|
| 1 | task-08a | Modelo Integration + IntegrationAction (sin romper Connector/Action actual) | Ajuste de modelo y repositorio, tenant-scoped |
| 2 | task-08b | Input schema V1 por acción (versionado) | `input_schema_json` versionado por action |
| 3 | task-08c | Validación de schema V1 | Tipos soportados, required, options, i18n map |
| 4 | task-08d | Validación payload server-side | Regex válida + validación payload en backend |
| 5 | task-08e | Preferencias de usuario | Persistencia `language`/`theme`/`table_density` |
| 6 | task-08f | Endpoints contrato frontend | `GET/PATCH` preferencias, `GET` schema action |
| 7 | task-08g | Ejecución backend de action (stub/mock) | `POST /actions/{action_id}/execute`, síncrono, sin colas |

Criterios de aceptación: frontend puede renderizar formularios dinámicos por schema; backend valida y ejecuta en modo stub/mock; preferencias de usuario persistidas; sin regresión en guards/tenant/permisos.

---

## Sprint 03 — Admin Web (MVP base) (5 tareas)

Doc: `sprint-03-admin-web.md`. Tasks: task-09 … task-13.

| # | Task ID (ej.) | Descripción | Alcance |
|---|----------------|-------------|---------|
| 1 | task-09 | Layout y menú admin | Rutas admin, navegación |
| 2 | task-10 | CRUD páginas: users, tags, filters, groups, connectors, actions, documents | Tablas, formularios, listados (API Sprint 02 + 02.5) |
| 3 | task-11 | Tag picker y filter builder (AND de tags) | Componentes reutilizables, semántica AND |
| 4 | task-12 | Editor de bindings de grupo + formularios connector/action | Group bindings, forms conectores y acciones |
| 5 | task-13 | Badges de estado y manejo de errores en UI | Estados visibles, mensajes de error |

Criterios de aceptación: admin gestiona entidades desde UI; filter builder refleja semántica AND; errores visibles; formularios de actions pueden apoyarse en el schema dinámico de Sprint 02.5.

---

## Sprint 03.1 — UX Admin + Chat Workspace (8 tareas)

Doc: `sprint-03-1-admin-ux-chat-workspace.md`. Tasks: task-13a … task-13h.

Objetivo: rehacer UX/UI del frontend para que refleje mejor el flujo real del producto, reduzca fricción para usuarios no técnicos y elimine exposición de detalles técnicos (IDs/JSON crudo) en los flujos principales.

| # | Task ID (ej.) | Descripción | Alcance |
|---|----------------|-------------|---------|
| 1 | task-13a | Reorganizar shell del admin/workspace | Topbar limpia, perfil en esquina superior derecha, navegación más compacta |
| 2 | task-13b | Unificar experiencia Connectors + Actions | Conector como contenedor expandible de actions; crear/editar actions en contexto |
| 3 | task-13c | Constructor guiado de integraciones HTTP | Auth por modos, content type visual, headers/query/body editables sin JSON crudo |
| 4 | task-13d | UX adaptativa por método HTTP/content type | Reglas UI: GET sin body principal, POST/PUT con body params, ayudas contextuales |
| 5 | task-13e | Tagging in-flow (create/reuse) | Selector con autocompletado + crear tag sin salir de users/actions/documents |
| 6 | task-13f | Users integrado: CRUD + tabla + filtros + guardar filtro | Experiencia unificada sobre la misma vista, con feedback inmediato |
| 7 | task-13g | Chat como workspace real de IA | Sin `action_id` manual ni "cargar schema"; formulario dinámico dentro del flujo |
| 8 | task-13h | Pulido UX, microcopy y smoke tests | Labels/ayudas claras, errores comprensibles, navegación coherente |

Criterios de aceptación: navegación y flujos más compactos; actions gestionadas dentro de connector sin pedir IDs técnicos; configuración HTTP guiada y entendible; tagging reutilizable desde formularios; users con flujo integrado de filtrado y saved filters; chat con experiencia real de asistente (sin controles técnicos visibles).

---

## Sprint 04 — Ingestión y vectorización (preliminar)

Doc: `sprint-04-ingestion-vectorization.md`. Tasks: task-14 … task-18 (desglose en Engram).

| # | Task ID (ej.) | Descripción | Alcance |
|---|----------------|-------------|---------|
| 1 | task-14 | Upload endpoint (single file) | API POST /admin/documents/upload |
| 2 | task-15 | Redis enqueue | Cola de jobs |
| 3 | task-16 | Worker + extraction | PDF/TXT/CSV (no OCR) |
| 4 | task-17 | Chunking + embeddings + Qdrant | Pipeline de indexación |
| 5 | task-18 | Status transitions | queued → processing → indexed \| error |

## Sprint 05 — Chat, RAG y acciones (preliminar)

Doc: `sprint-05-chat-rag-actions.md`. Tasks: task-19 … task-22 (desglose en Engram).

| # | Task ID (ej.) | Descripción | Alcance |
|---|----------------|-------------|---------|
| 1 | task-19 | Orquestación de chat + API | Conversación y backend chat (la UX base viene de Sprint 03.1) |
| 2 | task-20 | Resolución permisos efectivos | En request time |
| 3 | task-21 | RAG scope | Docs permitidos |
| 4 | task-22 | Action execution real | Evolucionar de stub/mock (Sprint 02.5) a ejecución real contra integraciones permitidas |

## Sprint 06 — Hardening (referencia)

Redacción, auditoría, métricas, revisión de rendimiento. Tasks se desglosan al abrir.

Las tasks concretas viven en Engram (`tasks/<id>`); este doc es semilla para bootstrap.
