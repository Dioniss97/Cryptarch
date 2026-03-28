---
name: issue-backlog
description: Gestionar captura y triage de backlog con GitHub Issues sin desplazar a Engram como fuente de verdad de ejecucion.
---

# Issue backlog

Usa esta skill cuando el trabajo todavia no es una `tasks/<id>` lista para ejecutar y hace falta **capturar, triar o promocionar** un item.

## Cuando usarla

- Cuando el usuario dicta varias notas, bugs o ideas y hay que convertirlas en issues claros.
- Cuando hay un hallazgo tecnico y quieres decidir si merece backlog o ejecucion inmediata.
- Cuando hace falta proponer labels, prioridad o dividir un problema en varios issues.
- Cuando una conversacion sobre producto debe terminar en una task ejecutable en Engram.

No la uses para implementar producto ni para sustituir la skill de memoria: **GitHub Issues capturan y triagen; Engram ejecuta**.

## Modelo mental

- **Issue**: unidad de captura y triage en GitHub.
- **Task**: unidad operativa en Engram (`tasks/<id>`).
- **Branch**: `task/<id>-slug` para trabajo normal.
- **PR**: siempre hacia `develop`.

Excepcion opcional: `docs/<slug>` para cambios puramente documentales si no compensa abrir una task de ejecucion completa.

## Flujo de captura

1. **Normalizar la entrada**  
   Convertir la nota o hallazgo en una frase concreta: problema, necesidad o mejora.

2. **Separar por unidad de valor**  
   Si hay varias cosas mezcladas, crear varios issues. Regla practica: un issue por bug, mejora o decision accionable.

3. **Separar por capa cuando mezcle backend y frontend**  
   Si una iniciativa cruza contrato, validacion, persistencia o integracion **y** tambien UX, formularios, estados o rendering, no la dejes como una unica task ambigua. Recomienda una de estas dos opciones:
   - **issue paraguas + tasks hijas** cuando convenga mantener una iniciativa comun con trazabilidad unica;
   - **varias tasks directas** cuando la separacion por capa ya este clara desde el triage.

   Regla practica:
   - **Backend** si hay contrato, validacion, persistencia o integracion.
   - **Frontend** si hay UX, formularios, estados o rendering.
   - Si una parte puede resolverse solo en UI, marcarla como **frontend-only**.
   - Si una parte depende de API, esquema, reglas o persistencia, marcarla como **requiere backend**.

4. **Proponer triage minimo**  
   Devolver, como minimo:
   - titulo del issue
   - resumen breve
   - labels sugeridas
   - prioridad sugerida
   - si debe promocionarse ya a task o quedarse en backlog
   - si conviene dividir frontend/backend
   - cuantas tasks crear
   - dependencias entre tasks
   - que parte puede ir solo en frontend y cual requiere backend obligatorio

5. **Crear issue solo si se pide explicitamente**  
   Si el usuario u orquestador lo pide, usar `gh` para crear el issue. Si no, devolver el borrador listo.

## Flujo de promocion a task

Cuando un issue pasa a ejecucion:

1. El orquestador crea o actualiza `tasks/<id>` en Engram.
2. La task guarda referencia al issue (`#123` o URL).
3. Si el triage recomendo separacion por capa, el orquestador crea **tasks distintas en Engram** y documenta ahi la division, dependencias y alcance de cada una.
4. El orquestador marca `Status: in_progress`.
5. La implementacion va por `ai-worker`.
6. El cierre va por rama `task/<id>-slug` y PR a `develop`.

Desde este punto, **Engram es la fuente de verdad de ejecucion**. El issue sigue siendo backlog, contexto y trazabilidad.

## Convencion de enlazado

Mantener siempre el hilo completo:

- **Issue**: referencia al problema o iniciativa original.
- **Task**: enlaza el issue relacionado.
- **Branch**: `task/<id>-slug`.
- **PR**: incluir `Issue: #123` y `Task: tasks/SC-209` en el cuerpo.

Plantilla minima recomendada para PR:

```md
## Enlaces
- Issue: #123
- Task: tasks/SC-209
```

## Cuando invocar al subagente issue-triage

Invocalo cuando:

- haya que convertir notas largas o desordenadas en uno o varios issues bien formados;
- quieras propuesta de labels/prioridad antes de tocar Engram;
- necesites crear issues con `gh`;
- quieras devolver al orquestador un paquete minimo para crear o actualizar la task.

No lo invoques para implementar, escribir en Engram o abrir PRs.

## Uso recomendado de gh

`gh` encaja bien para backlog si se usa con alcance limitado:

- consultas: `gh issue view`, `gh issue list`
- creacion: `gh issue create` solo cuando se pida explicitamente
- evitar merges, cierres masivos, borrado de ramas o acciones administrativas sin instruccion explicita

Configuracion basica en repos de organizacion:

- usar una cuenta con acceso real al repo;
- validar la sesion con `gh auth status`;
- si la organizacion usa SSO, autorizar la sesion antes de depender de `gh`;
- limitar permisos a leer/escribir issues y PRs cuando sea posible.

## Salida minima esperada

Cuando termines un triage, devuelve algo asi:

- issues propuestos o creados (`#`, titulo, URL si existe)
- labels sugeridas
- prioridad sugerida
- recomendacion: backlog o promocionar a task
- recomendacion de division front/back si aplica
- numero de tasks y dependencias
- desglose de trabajo frontend-only vs backend obligatorio
- datos minimos para Engram: `task_id` propuesto, issue enlazado, resumen operativo
