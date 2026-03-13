# Guía de roles y skills (Cursor)

El **agente principal actúa como orquestador**: coordina subagentes, mantiene estado en Engram y no ejecuta tests ni git a mano. **Engram es la piedra angular**: solo el orquestador escribe en Engram; los subagentes reciben instrucciones y referencias (observation_id, topic_key) para leer lo necesario. Flujo en `docs/architecture/orchestrator-flow.md`; protocolo Engram-agentes en `docs/architecture/engram-agent-protocol.md`.

## Rol orquestador

- Recibe tareas (p. ej. "siguiente tarea", task ID) → Engram `tasks/<id>`, contexto, skills.
- **No implementa código**: la escritura/modificación de código (features, refactors, CRUD, integraciones) se delega siempre en el subagente **ai-worker**. El orquestador asigna la misión, pasa contexto (topic_key, ficheros, criterios) y revisa el resultado; no hace el código él mismo.
- **Único escritor en Engram**: escribe/actualiza memorias antes de delegar (contexto de tarea, brief de fallo, decisiones) y pasa **referencias** (id o topic_key) al invocar subagentes, no volcados enormes en el prompt.
- **Arquitectura y patrones**: el orquestador documenta decisiones de arquitectura, patrones y estructura de carpetas (en Engram y/o docs/). Puede invocar opcionalmente un subagente **architecture-reviewer** para misiones concretas de análisis (revisar estructura, proponer mejoras); el subagente solo reporta y el orquestador escribe en Engram y delega la implementación en **ai-worker** si aplica.
- Delega: **ai-worker** (implementación de código), **test-runner** (tests), **debugger** (si fallan tests), **git-pr** (commit, push, PR). Contrasta lo que devuelven con la documentación y con Engram.
- Si los tests fallan: escribe en Engram el brief del fallo, invoca **debugger** con la referencia a esa observación → tras el fix relanza test-runner; repite hasta éxito.

## Subagentes (usar en lugar de comandos a mano)

Todos los subagentes son **solo lectura** en Engram (mem_search, mem_get_observation). El orquestador les pasa **referencias** (observation_id o topic_key) para que consulten el contexto necesario; no escriben memorias.

| Subagente | Definición | Uso |
|-----------|------------|-----|
| **test-runner** | `.cursor/agents/test-runner.md` | Ejecutar tests; no invocar `pytest` en terminal. Si fallan, reportar para que el orquestador invoque al debugger. |
| **git-pr** | `.cursor/agents/git-pr.md` | Ramas por tarea (`task/<id>`), Conventional Commits, push, apertura/actualización de PRs. Puede recibir ref. a `tasks/<id>` para título/descripción del PR. |
| **debugger** | `.cursor/agents/debugger.md` | Cuando un test falla: el orquestador escribe el brief en Engram y pasa la referencia; el debugger consulta por id/key, diagnostica, aplica fix y reporta. No lanza tests. |
| **ai-worker** | `.cursor/agents/ai-worker.md` | Implementar lo que asigne el orquestador; consultar en Engram las observaciones/topic_keys que el orquestador indique (tarea, criterios, docs). |
| **architecture-reviewer** (opcional) | `.cursor/agents/architecture-reviewer.md` | Misiones concretas de análisis: revisar estructura de carpetas, patrones, consistencia con docs; reportar al orquestador (no escribe en Engram). |

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
