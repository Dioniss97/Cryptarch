# Flujo del orquestador y subagentes

> Si vienes desde [AGENTS.md](../../AGENTS.md), aqui veras el flujo operativo completo.
> Si necesitas convenciones de git/PR, continua en [git-workflow.md](git-workflow.md).

## Mapa del documento

| Seccion | Para que sirve |
|---|---|
| `## Subagentes disponibles` | Ver responsabilidades por subagente. |
| `## Flujo backlog -> ejecucion` | Separar captura/triage de ejecucion. |
| `## Flujo tipico (task de desarrollo)` | Entender el ciclo completo de una task. |
| `## Flujo test -> fallo -> debug -> test` | Recordar la secuencia de recuperacion ante fallos locales. |
| `## Flujo PR -> CI -> recuperacion` | Cerrar el ciclo con checks de GitHub Actions tras la PR. |
| `## Engram y subagentes` | Aclarar el reparto de memoria/contexto. |
| `## Enlace con el resto de documentos` | Navegar al siguiente documento recomendado. |

El **agente principal** en Cursor actua como **orquestador**: no ejecuta tests ni git directamente; delega en subagentes y coordina el flujo completo **issue -> task -> branch -> PR**.

Regla base del proyecto:

- **GitHub Issue**: captura, triage y backlog.
- **Engram `tasks/<id>`**: fuente de verdad para la ejecucion.
- **Rama `task/<id>-slug`**: trabajo normal.
- **PR a `develop`**: integracion.

Para cambios puramente documentales, `docs/<slug>` sigue siendo una excepcion opcional. El borrado remoto normal de ramas se delega al ajuste de GitHub **Automatically delete head branches**; no debe automatizarse desde los agentes salvo instruccion explicita.

(Shell por defecto: ver regla **project-context** — Git Bash / sintaxis bash.)

## Subagentes disponibles

| Subagente | Definicion | Responsabilidad |
|-----------|------------|-----------------|
| **issue-triage** | [`.cursor/agents/issue-triage.md`](../../.cursor/agents/issue-triage.md) | Convertir notas, hallazgos o bugs en uno o varios issues; proponer labels/prioridad; crear issues con `gh` solo cuando se pida explicitamente. |
| **test-runner** | [`.cursor/agents/test-runner.md`](../../.cursor/agents/test-runner.md) | Ejecutar la suite de tests (pytest, etc.) y reportar resultado (pass/fail, resumen de fallos). |
| **git-pr** | [`.cursor/agents/git-pr.md`](../../.cursor/agents/git-pr.md) | Rama por task, commits (Conventional Commits), push y apertura/actualizacion de PRs hacia `develop`. |
| **debugger** | [`.cursor/agents/debugger.md`](../../.cursor/agents/debugger.md) | Cuando un test falla: recibir contexto del orquestador, diagnosticar, aplicar fix y reportar. No lanza tests. |
| **ai-worker** | [`.cursor/agents/ai-worker.md`](../../.cursor/agents/ai-worker.md) | Ejecutar la task de implementacion que asigne el orquestador (codigo, tests iniciales, refactors). |
| **ci-triage** | [`.cursor/agents/ci-triage.md`](../../.cursor/agents/ci-triage.md) | Tras la PR: consultar checks de Actions con `gh`, leer logs de jobs fallidos, clasificar el fallo, indicar reproducibilidad local y proponer siguiente accion al orquestador. Solo lectura; no escribe Engram ni aplica fixes. |

## Flujo backlog -> ejecucion

1. **Entrada**: llega un hallazgo, idea, bug o nota dictada en Cursor.
2. **Captura/triage**: el orquestador localiza un issue existente o invoca **issue-triage** si hay que dividir, redactar, etiquetar, priorizar o crear issues.
3. **Particion por capa cuando aplique**: si el hallazgo mezcla contrato, validacion, persistencia o integracion con UX, formularios, estados o rendering, el orquestador decide entre **issue paraguas + tasks hijas** o **varias tasks directas por capa**.
4. **Issue listo para trabajar**: cuando el item pasa de backlog a ejecucion, el orquestador crea o actualiza en Engram `tasks/<id>` y enlaza el issue correspondiente. Si hubo particion front/back, documenta en esas tasks la division, dependencias y que parte es frontend-only o requiere backend obligatorio.
5. **Cambio de estado**: la task en Engram pasa a `Status: in_progress` y desde ese momento gobierna la ejecucion. El issue sigue siendo backlog/seguimiento, no la fuente de verdad operativa.

## Flujo tipico (task de desarrollo)

1. **Orquestador** recibe “siguiente tarea” o un task ID -> busca en Engram `tasks/<id>`, pone `Status: in_progress`, recupera contexto (`docs/*`, `knowledge/*`, issue enlazado si existe).
2. **Antes de implementar**, el orquestador invoca **git-pr** para crear o seleccionar la rama de trabajo `task/<id>-slug` (o `docs/<slug>` si es doc-only). Este paso es obligatorio: no se empieza a editar codigo en una task de ejecucion sin rama preparada.
3. **Orquestador** invoca **ai-worker** con la mision (ej. “implementar `tasks/SC-209`”) y el contexto necesario (archivos, criterios, enlaces).
4. **Ai-worker** entrega codigo y/o tests iniciales.
5. **Orquestador** invoca **test-runner** para ejecutar los tests.
6. **Si los tests fallan**: el orquestador pasa al **debugger** el reporte del test-runner (ficheros, test que falla, mensaje de error, traza) y la mision de resolverlo. Debugger aplica cambios y reporta. El orquestador vuelve al paso 5 hasta que los tests pasen.
7. **Si los tests pasan**: el orquestador invoca **git-pr** para preparar commits legibles, hacer push y abrir/actualizar PR a `develop`.
8. **Post-PR — CI**: el orquestador invoca **ci-triage** para revisar los checks de GitHub Actions de esa PR (estado, logs si fallan, clasificacion, reproducibilidad, siguiente paso recomendado).
9. **Si los checks relevantes estan verdes**: el orquestador actualiza Engram `tasks/<id>` con What / Why / Where / Learned y `Status: done`. **Abrir PR no es suficiente** para marcar `done` sin pasar por esta comprobacion o sin un bloqueo explicito documentado.
10. **Si CI falla**: seguir la recomendacion de **ci-triage** — en muchos casos **test-runner** o **debugger** (misma distincion que en local); tras fix y push, otra ronda de **git-pr** y **volver a ci-triage**. Si el fallo es de permisos, secretos o requiere decision humana, el orquestador pone `Status: blocked` en Engram con motivo; no marcar `done` hasta resolverlo o acordar cierre.

## Flujo test -> fallo -> debug -> test

```
test-runner (run) -> falla -> orquestador -> debugger (fix) -> orquestador -> test-runner (run) -> ...
```

El test-runner solo ejecuta y reporta; no debe intentar arreglar si existe el subagente debugger. El debugger no lanza tests; el orquestador es quien vuelve a llamar al test-runner tras cada intento de fix.

## Flujo PR -> CI -> recuperacion

```
git-pr (push/PR) -> ci-triage (checks + logs) -> [verde] -> orquestador -> Engram Status: done
                                    |
                                    v falla
                    test-runner y/o debugger -> git-pr -> ci-triage (repite)
                                    |
                                    v no resoluble sin humano/infra
                    orquestador -> Engram Status: blocked (motivo explicito)
```

**ci-triage** no corrige ni escribe Engram: informa para que el orquestador decida y delegue. Tras cada nuevo push que afecte a la PR, conviene **volver a invocar ci-triage** hasta obtener checks verdes o un bloqueo acordado.

## Engram y subagentes

- **Orquestador**: tiene acceso a Engram (`mem_search`, `mem_save`, `mem_get_observation`, etc.). Es quien actualiza `tasks/<id>` y `sprints/*`, guarda `knowledge/*` y recupera contexto para las misiones.
- **Issues**: viven en GitHub y sirven para captura, triage y backlog. Pueden enlazarse desde la task, pero no sustituyen a `tasks/<id>`.
- **Subagentes**: si el entorno les da acceso a las mismas herramientas MCP (Engram), pueden consultar memoria; en caso contrario, el orquestador **incluye en el prompt** el contexto relevante (resumen de la task, issue relacionado, criterios, ficheros, hallazgos previos).

Regla practica: el orquestador siempre puede pasar contexto desde Engram al invocar un subagente; si el subagente puede consultar Engram, puede refinar la busqueda por su cuenta. El **issue-triage** devuelve al orquestador los datos minimos para crear o actualizar `tasks/<id>`; no escribe en Engram. Si recomienda dividir frontend/backend, esa division queda explicitada en Engram al crear las tasks.

## Resumen de responsabilidades

- **Orquestador**: coordina, invoca subagentes, mantiene estado en Engram y decide cuando promover un issue a task.
- **issue-triage**: captura y triage de backlog en GitHub Issues.
- **test-runner**: ejecuta tests, reporta resultado.
- **git-pr**: git (rama, commit, push, PR) siguiendo el flujo por task.
- **debugger**: diagnostica y corrige cuando los tests fallan.
- **ai-worker**: implementa lo que pida el orquestador (feature, tests iniciales, refactor).
- **ci-triage**: consulta checks y logs de CI de la PR con `gh`, clasifica el fallo y recomienda siguiente delegacion; el orquestador mantiene `in_progress` hasta checks verdes o `blocked` con causa.

## Enlace con el resto de documentos

- Vision general y arranque local: [README.md](../../README.md).
- Roles y skills por tipo de trabajo: [AGENTS.md](../../AGENTS.md).
- Reglas de ramas, commits y PR: [git-workflow.md](git-workflow.md).
- Prioridad y alcance de tareas: [tasks.md](../sprints/tasks.md).
