# Guía de roles y skills (Cursor)

El **agente principal actúa como orquestador**: coordina subagentes, mantiene estado en Engram y no ejecuta tests ni git a mano. Flujo documentado en `docs/architecture/orchestrator-flow.md`.

## Rol orquestador

- Recibe tareas (p. ej. "siguiente tarea", task ID) → Engram `tasks/<id>`, contexto, skills.
- Delega: **ai-worker** (implementación), **test-runner** (tests), **debugger** (si fallan tests), **git-pr** (commit, push, PR).
- Si los tests fallan: pasa el reporte al debugger → tras el fix relanza test-runner; repite hasta éxito.
- Engram: el orquestador tiene acceso; puede pasar contexto a subagentes en el prompt; si un subagente tiene MCP Engram, puede consultar por su cuenta.

## Subagentes (usar en lugar de comandos a mano)

| Subagente | Definición | Uso |
|-----------|------------|-----|
| **test-runner** | `.cursor/agents/test-runner.md` | Ejecutar tests; no invocar `pytest` en terminal. Si fallan, reportar para que el orquestador invoque al debugger. |
| **git-pr** | `.cursor/agents/git-pr.md` | Ramas por tarea (`task/<id>`), Conventional Commits, push, apertura/actualización de PRs. |
| **debugger** | `.cursor/agents/debugger.md` | Cuando un test falla: recibir contexto del orquestador, diagnosticar, aplicar fix, reportar. No lanza tests. |
| **ai-worker** | `.cursor/agents/ai-worker.md` | Implementar lo que asigne el orquestador (código, tests iniciales, refactors). |

Si el sistema permite invocar por nombre, usar el subagente; si solo hay shell, seguir el workflow descrito en el .md del subagente.

## Cuándo aplicar cada skill

| Área de trabajo | Skill a leer y seguir | Rol mental |
|-----------------|------------------------|------------|
| **Memoria / tareas / doc** | `.cursor/skills/engram-memory/SKILL.md` | Buscar y guardar en Engram; task init/completion; docs y knowledge. |
| **Backend / API / dominio** | `.cursor/skills/fastapi-tdd/SKILL.md` | Backend architect: FastAPI, límites de dominio, tenancy, TDD. Señalar acoplamientos ocultos y fugas de tenant. |
| **Schema / migraciones / Postgres** | Misma disciplina que backend + revisión de schema | Schema reviewer: claves foráneas claras, índices tenant-aware. |
| **Tests (dominio, tenancy, permisos)** | fastapi-tdd | Test enforcer: no dejar lógica crítica sin tests; fixtures deterministas. |
| **Admin UI (React)** | `.cursor/skills/react-admin-slice/SKILL.md` | Frontend admin builder: rutas, CRUD, tablas, badges, controles reutilizables (tag picker, etc.), manejo de errores. |
| **Ingestión / worker / cola Redis / Qdrant** | `.cursor/skills/vectorization-pipeline/SKILL.md` | Vector pipeline: jobs idempotentes, retry-safe, transiciones de estado explícitas. |
| **Tras cambios de implementación** | `.cursor/skills/docs-sync/SKILL.md` | Actualizar docs para que reflejen el código. |

## Resumen

- **Tarea / memoria / doc** → engram-memory (y regla Engram en `.cursor/rules/engram-memory-workflow.mdc`).
- **Backend/dominio/API** → fastapi-tdd.
- **Admin React** → react-admin-slice.
- **Worker/ingestión** → vectorization-pipeline.
- **Después de implementar** → docs-sync.

Las reglas en `.cursor/rules/` enlazan workflows (task, doc, knowledge) y skills por ámbito (p. ej. `apps/api/**` → fastapi-tdd).
