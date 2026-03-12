---
name: sprint-start
description: Iniciar un sprint: guardar su especificación y tasks en Engram (fuente de verdad) y producir plan de ejecución.
---

# Sprint start

Usar cuando pidan **iniciar un sprint** por id (ej. sprint-02). Todo lo relevante del sprint queda en Engram; los .md son solo lectura para poblar.

## Pasos

1. **Leer la especificación** desde `docs/sprints/sprint-XX.md` y, si hace falta, la sección del sprint en `docs/sprints/tasks.md` (task IDs y descripciones).
2. **Crear o actualizar en Engram la memoria del sprint** `sprints/sprint-XX` con: objetivo, alcance, criterios de aceptación, lista de task IDs (ej. task-01 … task-08), **Status: pending**. Así la spec del sprint vive en Engram.
3. **Crear en Engram las tasks** del sprint si no existen: para cada `task-XX`, `mem_search` por `tasks/task-XX`; si no hay memoria, `mem_save` con `topic_key`: `tasks/task-XX`, descripción (una línea) y **Status: pending**. No sobrescribir si ya existe (respeta in_progress/done).
4. **Producir plan de ejecución**: objetivo, dentro/fuera de alcance, orden TDD, orden de implementación, definition of done, docs a actualizar.

A partir de aquí, "qué toca" y "estado del sprint" se consultan en Engram, no en los .md.
