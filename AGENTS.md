# Guía de roles y skills (Cursor)

En Cursor no hay subagentes separados; el agente aplica **roles** y **skills** según el tipo de tarea. Usa esta guía para elegir disciplina y skill.

## Cuándo aplicar cada skill

| Área de trabajo | Skill a leer y seguir | Rol mental |
|-----------------|------------------------|------------|
| **Backend / API / dominio** | `.cursor/skills/fastapi-tdd/SKILL.md` | Backend architect: FastAPI, límites de dominio, tenancy, TDD. Señalar acoplamientos ocultos y fugas de tenant. |
| **Schema / migraciones / Postgres** | Misma disciplina que backend + revisión de schema | Schema reviewer: claves foráneas claras, índices tenant-aware. |
| **Tests (dominio, tenancy, permisos)** | fastapi-tdd | Test enforcer: no dejar lógica crítica sin tests; fixtures deterministas. |
| **Admin UI (React)** | `.cursor/skills/react-admin-slice/SKILL.md` | Frontend admin builder: rutas, CRUD, tablas, badges, controles reutilizables (tag picker, etc.), manejo de errores. |
| **Ingestión / worker / cola Redis / Qdrant** | `.cursor/skills/vectorization-pipeline/SKILL.md` | Vector pipeline: jobs idempotentes, retry-safe, transiciones de estado explícitas. |
| **Tras cambios de implementación** | `.cursor/skills/docs-sync/SKILL.md` | Actualizar docs para que reflejen el código. |
| **Siguiente sprint** | `docs/sprints/sprint-checklist.md` + sprint-next | Leer checklist, proponer siguiente sprint y primeras tareas. |
| **Iniciar sprint** | `.cursor/skills/sprint-start/SKILL.md` + skill del área | Cargar scope, proponer tareas, aplicar la skill del área (fastapi-tdd, react-admin-slice, etc.). |
| **Auditar sprint** | `.cursor/skills/sprint-audit/SKILL.md` | Revisar criterios de aceptación, código y tests; no marcar completo sin pedido explícito. |

## Resumen

- **Backend/dominio/API** → fastapi-tdd.
- **Admin React** → react-admin-slice.
- **Worker/ingestión** → vectorization-pipeline.
- **Después de implementar** → docs-sync.
- **Sprints** → sprint-next / sprint-start / sprint-audit según lo que pida el usuario.

Las reglas en `.cursor/rules/` ya enlazan estas skills a los paths correspondientes (p. ej. `apps/api/**` → fastapi-tdd).
