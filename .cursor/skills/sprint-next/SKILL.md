---
name: sprint-next
description: Encontrar la siguiente tarea o sprint pendiente; fuente de verdad es Engram.
---

# Sprint next

Usar cuando pidan **siguiente tarea**, **siguiente sprint** o **qué hacer ahora**. Consultar **siempre Engram primero**; no usar los .md para decidir qué toca.

## Pasos

1. **Buscar en Engram** trabajo pendiente: `mem_search` con "Status: pending", "tasks pending", "sprints sprint". La siguiente tarea es la de menor ID con Status pending (el orden viene de la memoria del sprint o del id numérico task-XX).
2. **Si Engram no tiene sprints/tasks** (primera vez o memoria vacía): usar `docs/sprints/tasks.md` y el doc del sprint como **semilla**: aplicar skill sprint-start para ese sprint (crear `sprints/sprint-XX` y `tasks/task-XX` en Engram) y luego devolver el plan y la siguiente tarea.
3. **Devolver**: id de la tarea o sprint (ej. task-02, Sprint 02), resumen del objetivo en 5 puntos, dependencias. Si hace falta, indicar la ruta del doc como referencia (`docs/sprints/sprint-02-auth-admin-api.md`).

Todo el estado vive en Engram; los .md son referencia o semilla.
