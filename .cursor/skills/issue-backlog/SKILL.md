---
name: issue-backlog
description: Gestionar captura y triage de backlog en Jira (`CRYPT`): épicas, historias, tareas, bugs, sprints y trabajo para agentes. Usar cuando haya ideas, notas, bugs, historias, épicas, prioridades o triage de producto/técnico.
---

# Jira backlog

Usa esta skill cuando el trabajo todavía no está listo para ejecución o necesita **captura, triage, refinamiento o promoción** en Jira.

## Cuando usarla

- Cuando el usuario dicta varias notas, bugs o ideas y hay que convertirlas en issues claros.
- Cuando hay un hallazgo tecnico y quieres decidir si merece backlog o ejecucion inmediata.
- Cuando hace falta proponer labels, prioridad o dividir un problema en varios issues.
- Cuando una conversación sobre producto debe terminar en épica/historia/tarea/bug en Jira.
- Cuando una historia debe pasar de `Idea` a `refinamiento` o a `Ready for Agent`.

No la uses para implementar producto. **Jira gobierna backlog/estado**; **Engram guarda memoria operativa**.

## Modelo mental

- **Confluence**: futura zona cero de verdad no técnica.
- **Jira issue (`CRYPT-*`)**: unidad de backlog/ejecución (Epic, Historia, Tarea, Error, Subtask).
- **Engram task memory**: memoria operativa `tasks/<jira_key>`.
- **Branch**: `task/<jira_key>-slug` para trabajo normal.
- **PR**: siempre hacia `develop`.

Excepcion opcional: `docs/<slug>` para cambios puramente documentales si no compensa abrir una task de ejecucion completa.

## Flujo de captura

1. **Normalizar la entrada**  
   Convertir la nota o hallazgo en una frase concreta: problema, necesidad o mejora.

2. **Separar por unidad de valor**  
   Si hay varias cosas mezcladas, crear varios issues en Jira. Regla practica: un issue por bug, mejora o decisión accionable.

3. **Separar por capa cuando mezcle backend y frontend**  
   Si una iniciativa cruza contrato, validacion, persistencia o integracion **y** tambien UX, formularios, estados o rendering, no la dejes como una unica task ambigua. Recomienda una de estas dos opciones:
   - **épica/historia paraguas + tareas hijas** cuando convenga mantener una iniciativa común con trazabilidad única;
   - **varias tasks directas** cuando la separacion por capa ya este clara desde el triage.

   Regla practica:
   - **Backend** si hay contrato, validacion, persistencia o integracion.
   - **Frontend** si hay UX, formularios, estados o rendering.
   - Si una parte puede resolverse solo en UI, marcarla como **frontend-only**.
   - Si una parte depende de API, esquema, reglas o persistencia, marcarla como **requiere backend**.

4. **Proponer triage minimo**  
   Devolver, como minimo:
   - tipo Jira recomendado: Epic | Historia | Tarea | Error | Subtask
   - titulo del issue
   - resumen breve
   - labels sugeridas
   - prioridad sugerida
   - si debe pasar a `refinamiento`, `Ready for Agent` o quedarse en `Idea`
   - si conviene dividir frontend/backend
   - cuantas tasks crear
   - dependencias entre tasks
   - que parte puede ir solo en frontend y cual requiere backend obligatorio

5. **Crear/editar Jira solo si se pide explícitamente**  
   Si el usuario u orquestador lo pide, usar el MCP de Atlassian/Jira. Si no, devolver el borrador listo.

## Flujo de promocion a task

Cuando un issue Jira pasa a ejecucion:

1. El orquestador lee la tarjeta Jira `CRYPT-*`.
2. Crea o actualiza `tasks/<jira_key>` en Engram con contexto operativo.
3. Si el triage recomendo separacion por capa, el orquestador crea **tasks distintas en Engram** y documenta ahi la division, dependencias y alcance de cada una.
4. El orquestador marca `Status: in_progress`.
5. La implementacion va por `ai-worker`.
6. El cierre va por rama `task/<jira_key>-slug` y PR a `develop`.

Desde este punto, **Jira mantiene el estado de ejecución** y Engram conserva contexto/outcome para agentes.

## Convencion de enlazado

Mantener siempre el hilo completo:

- **Jira**: `CRYPT-*` referencia el problema o iniciativa.
- **Engram**: `tasks/CRYPT-*` enlaza contexto operativo.
- **Branch**: `task/CRYPT-*-slug`.
- **PR**: incluir `Jira: CRYPT-123` y `Engram: tasks/CRYPT-123` en el cuerpo.

Plantilla minima recomendada para PR:

```md
## Enlaces
- Jira: CRYPT-123
- Engram: tasks/CRYPT-123
```

## Cuando invocar al subagente issue-triage

Invocalo cuando:

- haya que convertir notas largas o desordenadas en uno o varios issues Jira bien formados;
- quieras propuesta de labels/prioridad antes de tocar Engram;
- necesites crear/editar issues con Jira MCP;
- quieras devolver al orquestador un paquete minimo para crear o actualizar memoria operativa en Engram.

No lo invoques para implementar, escribir en Engram o abrir PRs.

## Uso recomendado de Jira MCP

Usar Atlassian MCP para consultar, crear, editar y transicionar issues Jira. Leer el descriptor del tool antes de llamar a `CallMcpTool`.

No usar GitHub Issues como backlog. GitHub queda para código, PRs, reviews y CI.

## Salida minima esperada

Cuando termines un triage, devuelve algo asi:

- issues Jira propuestos o creados (`CRYPT-*`, titulo, URL si existe)
- labels sugeridas
- prioridad sugerida
- recomendacion: `Idea`, `refinamiento`, `Ready for Agent`, `Bloqueado`, etc.
- recomendacion de division front/back si aplica
- numero de tasks y dependencias
- desglose de trabajo frontend-only vs backend obligatorio
- datos minimos para Engram: `topic_key` propuesto (`tasks/CRYPT-*`), Jira enlazado, resumen operativo
