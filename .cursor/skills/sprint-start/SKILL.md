---
name: sprint-start
description: Iniciar o preparar un sprint real en Jira (`CRYPT`) y crear memoria operativa en Engram solo como apoyo para agentes.
---

# Sprint start

Usar cuando pidan **iniciar un sprint** o preparar un sprint en Jira. Jira es fuente de verdad del sprint; Engram guarda contexto operativo.

## Pasos

1. **Leer Jira**: sprint actual/candidato, issues `CRYPT-*`, estados, prioridades y dependencias.
2. **Definir objetivo del sprint** en una frase y confirmar dentro/fuera de alcance.
3. **Seleccionar pocas tareas**: preferir 3-5 issues `Ready for Agent` o refinables rápidamente.
4. **Crear/actualizar Engram** solo como memoria operativa del sprint (`sprints/<jira-sprint>`) con links a `CRYPT-*`, riesgos y contexto útil. No usar los `.md` antiguos como fuente de planificación.
5. **Producir plan de ejecución**: orden, dependencias, definition of done (tests locales, PR, checks CI verdes en GitHub o `blocked` explícito), docs/Confluence a actualizar.

A partir de aquí, "qué toca" y "estado del sprint" se consultan en Jira; Engram ayuda a los agentes a no perder contexto.
