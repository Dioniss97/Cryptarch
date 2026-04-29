---
name: sprint-next
description: Encontrar la siguiente tarea o sprint pendiente en Jira (`CRYPT`). Usar cuando pidan siguiente tarea, siguiente sprint, qué hacer ahora o priorización para agentes.
---

# Sprint next

Usar cuando pidan **siguiente tarea**, **siguiente sprint** o **qué hacer ahora**. Consultar **Jira (`CRYPT`) primero**; no usar los `.md` antiguos para decidir qué toca.

## Pasos

1. **Buscar en Jira** issues `Ready for Agent`, o si no existe ese estado, en `refinamiento` priorizados por el usuario/orquestador. Usar JQL del proyecto `CRYPT`.
2. **Consultar Engram** solo para recuperar contexto operativo de la tarjeta elegida (`tasks/CRYPT-*`) y decisiones/gotchas relacionadas.
3. **Devolver**: Jira key (`CRYPT-*`), resumen del objetivo, dependencias, por qué es la siguiente, y si ya está lista para agente o requiere refinamiento.

Jira es la fuente de verdad de backlog/sprints/estado. Engram es memoria operativa.
