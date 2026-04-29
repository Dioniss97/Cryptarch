---
name: sprint-audit
description: Auditar un sprint de Jira frente a sus criterios de aceptación antes de marcarlo como hecho.
---

# Sprint audit

Usar cuando pidan **auditar** un sprint antes de cerrarlo. Jira (`CRYPT`) es la fuente de verdad del sprint; Engram aporta contexto operativo.

## Pasos

1. **Identificar alcance**: consultar Jira (`CRYPT`) para sprint, issues incluidos, estados, prioridades y bloqueos.
2. **Criterios**: usar criterios de aceptación de las tarjetas Jira y contexto operativo en Engram (`tasks/CRYPT-*`) si existe.
3. **Inspeccionar**: código, tests y docs afectados.
4. **Reportar**: PASS/FAIL por criterio, huecos, atajos y tareas de seguimiento. No marcar el sprint como completo automáticamente; recomendar pasos concretos.

Fuente de verdad: Jira. Engram es memoria operativa. Los `.md` antiguos de sprints son históricos/experimentales salvo instrucción explícita.
