# Guía de roles y skills (Cursor)

> Si vienes desde [README.md](README.md), este documento te explica como trabajar el dia a dia con agentes.
> Si quieres el flujo operativo paso a paso, continua en [docs/architecture/orchestrator-flow.md](docs/architecture/orchestrator-flow.md).

## Lectura rapida

| Si necesitas... | Ve a... |
|---|---|
| Entender roles y responsabilidades | [Rol orquestador](#rol-orquestador) |
| Saber que subagente usar | [Subagentes](#subagentes-usar-en-lugar-de-comandos-a-mano) |
| Elegir skill por tipo de tarea | [Cuándo aplicar cada skill](#cuándo-aplicar-cada-skill) |
| Continuar con el flujo operativo | [docs/architecture/orchestrator-flow.md](docs/architecture/orchestrator-flow.md) |

El **agente principal actua como orquestador**: coordina subagentes, mantiene contexto operativo en Engram y no ejecuta tests ni git a mano. Fuentes de verdad actuales:

- **Confluence**: futura zona cero de verdad no técnica: visión, producto, dominio, MVP, flujos y decisiones de negocio.
- **Jira (`CRYPT`)**: backlog y ejecución: épicas, historias, tareas, bugs, sprints, estados, prioridades y trabajo para agentes.
- **Engram**: memoria operativa de agentes: decisiones, convenciones, IDs, sesiones, gotchas y resúmenes de ejecución. Solo el orquestador escribe.
- **GitHub**: código, ramas, PRs, reviews y CI. **No usar GitHub Issues como backlog de producto**.

El flujo recomendado separa claramente **Jira issue -> Engram context -> branch -> PR -> CI**. Flujo en [docs/architecture/orchestrator-flow.md](docs/architecture/orchestrator-flow.md); protocolo Engram-agentes en [docs/architecture/engram-agent-protocol.md](docs/architecture/engram-agent-protocol.md).

Para activar este comportamiento de forma explicita en chat, usa el comando:
- `/orchestrator`

## Rol orquestador

- Recibe backlog o tareas (p. ej. un hallazgo, "siguiente tarea", un Jira key `CRYPT-*`) -> captura/triage en Jira cuando haga falta y memoria operativa en Engram `tasks/CRYPT-*`.
- Si una iniciativa mezcla backend y frontend, decide entre **issue paraguas + tasks hijas** o **tasks separadas por capa**. Regla practica: backend para contrato, validacion, persistencia o integracion; frontend para UX, formularios, estados o rendering. Esa division debe quedar documentada en Engram al crear las tasks.
- **No implementa código**: la escritura/modificación de código (features, refactors, CRUD, integraciones) se delega siempre en el subagente **ai-worker**. El orquestador asigna la misión, pasa contexto (topic_key, ficheros, criterios) y revisa el resultado; no hace el código él mismo.
- **Único escritor en Engram**: escribe/actualiza memorias antes de delegar (contexto de tarea, brief de fallo, decisiones) y pasa **referencias** (id o topic_key) al invocar subagentes, no volcados enormes en el prompt.
- **Arquitectura y patrones**: el orquestador documenta decisiones de arquitectura, patrones y estructura de carpetas (en Engram y/o docs/). Puede invocar opcionalmente un subagente **architecture-reviewer** para misiones concretas de análisis (revisar estructura, proponer mejoras); el subagente solo reporta y el orquestador escribe en Engram y delega la implementación en **ai-worker** si aplica.
- Delega: **issue-triage** (captura/triage de backlog Jira), **ai-worker** (implementacion de codigo), **test-runner** (tests), **debugger** (si fallan tests), **git-pr** (commit, push, PR), **ci-triage** (checks de GitHub Actions tras la PR). Contrasta lo que devuelven con Confluence/Jira/Engram.
- Si los tests fallan: escribe en Engram el brief del fallo, invoca **debugger** con la referencia a esa observación → tras el fix relanza test-runner; repite hasta éxito.
- Tras **git-pr**, invoca **ci-triage** para validar checks en GitHub. Si CI falla, sigue la recomendacion del informe (test-runner, debugger, nuevo git-pr, re-ci-triage). **No marques `tasks/<id>` como `done` solo porque exista la PR**: espera checks relevantes verdes o deja `Status: blocked` con motivo explicito.

## Subagentes (usar en lugar de comandos a mano)

Todos los subagentes son **solo lectura** en Engram (mem_search, mem_get_observation). El orquestador les pasa **referencias** (observation_id o topic_key) para que consulten el contexto necesario; no escriben memorias.

| Subagente | Definición | Uso |
|-----------|------------|-----|
| **issue-triage** | [`.cursor/agents/issue-triage.md`](.cursor/agents/issue-triage.md) | Convertir notas o hallazgos en issues Jira (`CRYPT-*`), proponer tipo/estado/prioridad y crear/editar Jira con MCP solo cuando se pida explicitamente. Si el hallazgo mezcla capas, devuelve recomendacion de division front/back, numero de tasks, dependencias y alcance frontend-only vs backend obligatorio para que el orquestador lo documente en Jira/Engram. |
| **test-runner** | [`.cursor/agents/test-runner.md`](.cursor/agents/test-runner.md) | Ejecutar tests; no invocar `pytest` en terminal. Si fallan, reportar para que el orquestador invoque al debugger. |
| **git-pr** | [`.cursor/agents/git-pr.md`](.cursor/agents/git-pr.md) | Ramas `task/CRYPT-123-slug` (o `docs/<slug>` como excepcion doc-only), Conventional Commits, push y apertura/actualizacion de PRs a `develop`. Puede recibir ref. a Jira `CRYPT-*` y Engram `tasks/CRYPT-*` para titulo/descripción del PR. |
| **debugger** | [`.cursor/agents/debugger.md`](.cursor/agents/debugger.md) | Cuando un test falla: el orquestador escribe el brief en Engram y pasa la referencia; el debugger consulta por id/key, diagnostica, aplica fix y reporta. No lanza tests. |
| **ai-worker** | [`.cursor/agents/ai-worker.md`](.cursor/agents/ai-worker.md) | Implementar lo que asigne el orquestador; consultar en Engram las observaciones/topic_keys que el orquestador indique (tarea, criterios, docs). |
| **architecture-reviewer** (opcional) | [`.cursor/agents/architecture-reviewer.md`](.cursor/agents/architecture-reviewer.md) | Misiones concretas de análisis: revisar estructura de carpetas, patrones, consistencia con docs; reportar al orquestador (no escribe en Engram). |
| **ci-triage** | [`.cursor/agents/ci-triage.md`](.cursor/agents/ci-triage.md) | Tras abrir o actualizar PR: consultar checks de Actions con `gh`, leer logs de jobs fallidos, clasificar (lint/test/build/config/permisos/infra), estimar reproducibilidad local y proponer siguiente accion. No escribe Engram ni aplica fixes ni merge. |

Si el sistema permite invocar por nombre, usar el subagente; si solo hay shell, seguir el workflow descrito en el .md del subagente.

## Cuándo aplicar cada skill

| Área de trabajo | Skill a leer y seguir | Rol mental |
|-----------------|------------------------|------------|
| **Memoria / tareas / doc** | [`.cursor/skills/engram-memory/SKILL.md`](.cursor/skills/engram-memory/SKILL.md) | Buscar y guardar en Engram; task init/completion; docs y knowledge. |
| **Backlog / Jira triage** | [`.cursor/skills/issue-backlog/SKILL.md`](.cursor/skills/issue-backlog/SKILL.md) | Convertir hallazgos en Jira issues, triar, priorizar, refinar y mantener trazabilidad Jira/Engram/PR. |
| **Backend / API / dominio** | [`.cursor/skills/fastapi-tdd/SKILL.md`](.cursor/skills/fastapi-tdd/SKILL.md) | Backend architect: FastAPI, límites de dominio, tenancy, TDD. Señalar acoplamientos ocultos y fugas de tenant. |
| **Schema / migraciones / Postgres** | Misma disciplina que backend + revisión de schema | Schema reviewer: claves foráneas claras, índices tenant-aware. |
| **Tests (dominio, tenancy, permisos)** | [fastapi-tdd](.cursor/skills/fastapi-tdd/SKILL.md) | Test enforcer: no dejar lógica crítica sin tests; fixtures deterministas. |
| **Admin UI (React)** | [`.cursor/skills/react-admin-slice/SKILL.md`](.cursor/skills/react-admin-slice/SKILL.md) | Frontend admin builder: rutas, CRUD, tablas, badges, controles reutilizables (tag picker, etc.), manejo de errores. |
| **Ingestión / worker / cola Redis / Qdrant** | [`.cursor/skills/vectorization-pipeline/SKILL.md`](.cursor/skills/vectorization-pipeline/SKILL.md) | Vector pipeline: jobs idempotentes, retry-safe, transiciones de estado explícitas. |
| **Tras cambios de implementación** | [`.cursor/skills/docs-sync/SKILL.md`](.cursor/skills/docs-sync/SKILL.md) | Actualizar docs para que reflejen el código. |

## Resumen

- **Tarea / memoria / doc** → engram-memory (y regla Engram en [`.cursor/rules/engram-memory-workflow.mdc`](.cursor/rules/engram-memory-workflow.mdc)).
- **Backlog / Jira triage** -> issue-backlog.
- **Backend/dominio/API** → fastapi-tdd.
- **Admin React** → react-admin-slice.
- **Worker/ingestión** → vectorization-pipeline.
- **Después de implementar** → docs-sync.

Las reglas en [`.cursor/rules/`](.cursor/rules/) enlazan workflows (task, doc, knowledge) y skills por ámbito (p. ej. `apps/api/**` → fastapi-tdd).

## Siguiente lectura recomendada

- Para el flujo detallado de coordinacion: [docs/architecture/orchestrator-flow.md](docs/architecture/orchestrator-flow.md).
- Para como cerrar cambios con git y PR: [docs/architecture/git-workflow.md](docs/architecture/git-workflow.md).
- Para escoger trabajo por prioridad: Jira (`CRYPT`), no los antiguos `.md` de sprints.
