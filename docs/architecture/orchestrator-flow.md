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

El **agente principal** en Cursor actua como **orquestador**: no ejecuta tests ni git directamente; delega en subagentes y coordina el flujo completo **Jira -> Engram -> branch -> PR -> CI**.

Regla base del proyecto:

- **Confluence**: futura zona cero de verdad no técnica: visión, producto, dominio, MVP, flujos y decisiones de negocio.
- **Jira (`CRYPT`)**: backlog y ejecución: épicas, historias, tareas, bugs, sprints, estados, prioridades y trabajo para agentes.
- **Engram `tasks/CRYPT-*`**: memoria operativa para agentes (decisiones, IDs, sesiones, gotchas, contexto de ejecución).
- **Rama `CRYPT-123-slug`**: trabajo normal (Conventional Commits + prefijo Jira en commits y titulo de PR; sin prefijo `task/`).
- **PR a `develop`**: integracion.
- **GitHub**: código, ramas, PRs, reviews y CI. No usar GitHub Issues como backlog de producto.

Para cambios puramente documentales, `docs/<slug>` sigue siendo una excepcion opcional. El borrado remoto normal de ramas se delega al ajuste de GitHub **Automatically delete head branches**; no debe automatizarse desde los agentes salvo instruccion explicita.

(Shell por defecto: ver regla **project-context** — Git Bash / sintaxis bash.)

## Subagentes disponibles

| Subagente | Definicion | Responsabilidad |
|-----------|------------|-----------------|
| **issue-triage** | [`.cursor/agents/issue-triage.md`](../../.cursor/agents/issue-triage.md) | Convertir notas, hallazgos o bugs en issues Jira (`CRYPT-*`); proponer tipo/estado/prioridad; crear/editar Jira con MCP solo cuando se pida explicitamente. |
| **test-runner** | [`.cursor/agents/test-runner.md`](../../.cursor/agents/test-runner.md) | Ejecutar la suite de tests (pytest, etc.) y reportar resultado (pass/fail, resumen de fallos). |
| **git-pr** | [`.cursor/agents/git-pr.md`](../../.cursor/agents/git-pr.md) | Rama `CRYPT-*-slug`, commits y titulo de PR (`CRYPT-* type(scope): …`), push y PRs hacia `develop`. |
| **debugger** | [`.cursor/agents/debugger.md`](../../.cursor/agents/debugger.md) | Cuando un test falla: recibir contexto del orquestador, diagnosticar, aplicar fix y reportar. No lanza tests. |
| **ai-worker** | [`.cursor/agents/ai-worker.md`](../../.cursor/agents/ai-worker.md) | Ejecutar la task de implementacion que asigne el orquestador (codigo, tests iniciales, refactors). |
| **ci-triage** | [`.cursor/agents/ci-triage.md`](../../.cursor/agents/ci-triage.md) | Tras la PR: consultar checks de Actions con `gh`, leer logs de jobs fallidos, clasificar el fallo, indicar reproducibilidad local y proponer siguiente accion al orquestador. Solo lectura; no escribe Engram ni aplica fixes. |

## Flujo backlog -> ejecucion

1. **Entrada**: llega un hallazgo, idea, bug o nota dictada en Cursor.
2. **Captura/triage**: el orquestador localiza un issue Jira existente o invoca **issue-triage** si hay que dividir, redactar, etiquetar, priorizar o crear issues.
3. **Particion por capa cuando aplique**: si el hallazgo mezcla contrato, validacion, persistencia o integracion con UX, formularios, estados o rendering, el orquestador decide entre **épica/historia paraguas + tasks hijas** o **varias tasks directas por capa**.
4. **Issue listo para trabajar**: cuando el item pasa de backlog a ejecucion, el orquestador crea o actualiza en Engram `tasks/CRYPT-*` y enlaza el issue Jira correspondiente. Si hubo particion front/back, documenta la division, dependencias y que parte es frontend-only o requiere backend obligatorio.
5. **Cambio de estado**: Jira mantiene el estado del item; Engram guarda contexto operativo y outcome para agentes.

## Flujo tipico (task de desarrollo)

1. **Orquestador** recibe “siguiente tarea” o un Jira key -> lee Jira `CRYPT-*`, recupera/crea contexto en Engram `tasks/CRYPT-*` y prepara el trabajo.
2. **Antes de implementar**, el orquestador invoca **git-pr** para crear o seleccionar la rama `CRYPT-123-slug` (o `docs/<slug>` si es doc-only). Este paso es obligatorio: no se empieza a editar codigo en una task de ejecucion sin rama preparada.
3. **Orquestador** invoca **ai-worker** con la mision (ej. “implementar `CRYPT-9`”) y el contexto necesario (archivos, criterios, enlaces Jira/Engram).
4. **Ai-worker** entrega codigo y/o tests iniciales.
5. **Orquestador** invoca **test-runner** para ejecutar los tests.
6. **Si los tests fallan**: el orquestador pasa al **debugger** el reporte del test-runner (ficheros, test que falla, mensaje de error, traza) y la mision de resolverlo. Debugger aplica cambios y reporta. El orquestador vuelve al paso 5 hasta que los tests pasen.
7. **Si los tests pasan**: el orquestador invoca **git-pr** para preparar commits legibles, hacer push y abrir/actualizar PR a `develop`.
8. **Post-PR — CI**: el orquestador invoca **ci-triage** para revisar los checks de GitHub Actions de esa PR (estado, logs si fallan, clasificacion, reproducibilidad, siguiente paso recomendado).
9. **Si los checks relevantes estan verdes**: el orquestador actualiza Jira y Engram `tasks/CRYPT-*` con What / Why / Where / Learned y estado final. **Abrir PR no es suficiente** para marcar `done` sin pasar por esta comprobacion o sin un bloqueo explicito documentado.
10. **Si CI falla**: seguir la recomendacion de **ci-triage** — en muchos casos **test-runner** o **debugger** (misma distincion que en local); tras fix y push, otra ronda de **git-pr** y **volver a ci-triage**. Si el fallo es de permisos, secretos o requiere decision humana, el orquestador pone Jira/Engram en `blocked` con motivo; no marcar `done` hasta resolverlo o acordar cierre.

## Flujo test -> fallo -> debug -> test

```
test-runner (run) -> falla -> orquestador -> debugger (fix) -> orquestador -> test-runner (run) -> ...
```

El test-runner solo ejecuta y reporta; no debe intentar arreglar si existe el subagente debugger. El debugger no lanza tests; el orquestador es quien vuelve a llamar al test-runner tras cada intento de fix.

## Flujo PR -> CI -> recuperacion

```
git-pr (push/PR) -> ci-triage (checks + logs) -> [verde] -> orquestador -> Jira/Engram done
                                    |
                                    v falla
                    test-runner y/o debugger -> git-pr -> ci-triage (repite)
                                    |
                                    v no resoluble sin humano/infra
                    orquestador -> Jira/Engram blocked (motivo explicito)
```

**ci-triage** no corrige ni escribe Engram: informa para que el orquestador decida y delegue. Tras cada nuevo push que afecte a la PR, conviene **volver a invocar ci-triage** hasta obtener checks verdes o un bloqueo acordado.

## Engram y subagentes

- **Orquestador**: lee Jira para backlog/estado y escribe en Engram (`mem_search`, `mem_save`, `mem_get_observation`, etc.) solo contexto operativo (`tasks/CRYPT-*`, `knowledge/*`, resúmenes).
- **Jira issues**: viven en Jira y gobiernan backlog/sprints/estado.
- **Subagentes**: si el entorno les da acceso a las mismas herramientas MCP (Engram/Jira), pueden consultar por referencias; en caso contrario, el orquestador **incluye en el prompt** el contexto relevante.

Regla practica: el orquestador siempre puede pasar contexto desde Jira/Engram al invocar un subagente; si el subagente puede consultar MCP, puede refinar la busqueda por su cuenta. El **issue-triage** devuelve al orquestador los datos minimos para crear o actualizar Jira y `tasks/CRYPT-*`; no escribe en Engram.

## Resumen de responsabilidades

- **Orquestador**: coordina, invoca subagentes, mantiene Jira/Engram alineados y decide cuando promover un issue a task ejecutable.
- **issue-triage**: captura y triage de backlog en Jira.
- **test-runner**: ejecuta tests, reporta resultado.
- **git-pr**: git (rama, commit, push, PR) siguiendo el flujo por task.
- **debugger**: diagnostica y corrige cuando los tests fallan.
- **ai-worker**: implementa lo que pida el orquestador (feature, tests iniciales, refactor).
- **ci-triage**: consulta checks y logs de CI de la PR con `gh`, clasifica el fallo y recomienda siguiente delegacion; el orquestador mantiene `in_progress` hasta checks verdes o `blocked` con causa.

## Enlace con el resto de documentos

- Vision general y arranque local: [README.md](../../README.md).
- Roles y skills por tipo de trabajo: [AGENTS.md](../../AGENTS.md).
- Reglas de ramas, commits y PR: [git-workflow.md](git-workflow.md).
- Prioridad, sprints y estado: Jira (`CRYPT`). Los antiguos `docs/sprints/*.md` son históricos/experimentales salvo instrucción explícita.
