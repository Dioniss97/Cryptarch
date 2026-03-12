---
name: sprint-audit
description: Auditar un sprint frente a sus criterios de aceptación antes de marcarlo como hecho.
---

# Sprint audit

Usar cuando pidan **auditar** un sprint antes de cerrarlo.

## Pasos

1. **Identificar alcance**: en Engram `sprints/sprint-XX` (objetivo, criterios, lista de tasks) y `tasks/task-XX`. Si falta algo, completar desde `docs/sprints/sprint-XX.md` o `tasks.md`.
2. **Criterios**: usar los criterios de aceptación guardados en la memoria del sprint en Engram; si no están, leer el doc del sprint.
3. **Inspeccionar**: código, tests y docs afectados.
4. **Reportar**: PASS/FAIL por criterio, huecos, atajos y tareas de seguimiento. No marcar el sprint como completo automáticamente; recomendar pasos concretos.

Fuente de verdad: Engram. El checklist del sprint son las memorias `tasks/task-XX`; los .md son referencia.
