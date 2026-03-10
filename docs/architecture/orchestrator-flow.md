# Flujo del orquestador y subagentes

El **agente principal** en Cursor actúa como **orquestador**: no ejecuta tests ni git directamente; delega en subagentes y coordina el flujo hasta el éxito.

## Subagentes disponibles

| Subagente | Definición | Responsabilidad |
|-----------|------------|-----------------|
| **test-runner** | `.cursor/agents/test-runner.md` | Ejecutar la suite de tests (pytest, etc.) y reportar resultado (pass/fail, resumen de fallos). |
| **git-pr** | `.cursor/agents/git-pr.md` | Ramas por tarea (`task/<id>`), commits (Conventional Commits), push y apertura/actualización de PRs. |
| **debugger** | `.cursor/agents/debugger.md` | Cuando un test falla: recibir contexto del orquestador, diagnosticar, aplicar fix y reportar. No lanza tests. |
| **ai-worker** | `.cursor/agents/ai-worker.md` | Ejecutar la tarea de implementación que asigne el orquestador (código, tests iniciales, refactors). |

## Flujo típico (tarea de desarrollo)

1. **Orquestador** recibe “siguiente tarea” o un task ID → busca en Engram `tasks/<id>`, pone `Status: in_progress`, recupera contexto (docs, knowledge).
2. **Orquestador** invoca **ai-worker** con la misión (ej. “implementar task-02: guards admin, dependencias y ruta GET /admin/me”) y el contexto necesario (archivos, criterios). Si el ai-worker tiene acceso a Engram, puede consultar; si no, el orquestador pasa el contexto en el prompt.
3. **Ai-worker** entrega código y/o tests.
4. **Orquestador** invoca **test-runner** para ejecutar los tests.
5. **Si los tests pasan**: orquestador invoca **git-pr** (rama, commit, push, PR) y actualiza Engram `tasks/<id>` a `Status: done`.
6. **Si los tests fallan**: orquestador pasa al **debugger** el reporte del test-runner (ficheros, test que falla, mensaje de error, traza) y la misión de resolverlo. Debugger aplica cambios y reporta. Orquestador vuelve al paso 4 (test-runner). Se repite hasta que los tests pasen.

## Flujo test → fallo → debug → test

```
test-runner (run) → falla → orquestador → debugger (fix) → orquestador → test-runner (run) → …
```

El test-runner solo ejecuta y reporta; no debe intentar arreglar si existe el subagente debugger. El debugger no lanza tests; el orquestador es quien vuelve a llamar al test-runner tras cada intento de fix.

## Engram y subagentes

- **Orquestador**: tiene acceso a Engram (mem_search, mem_save, mem_get_observation, etc.). Es quien actualiza `tasks/<id>` y `sprints/*`, guarda knowledge y recupera contexto para las misiones.
- **Subagentes**: si el entorno les da acceso a las mismas herramientas MCP (Engram), pueden consultar memoria; en caso contrario, el orquestador **incluye en el prompt** el contexto relevante (resumen de la tarea, criterios, ficheros, hallazgos previos) cuando invoca a ai-worker o debugger.

Regla práctica: el orquestador siempre puede pasar contexto desde Engram al invocar un subagente; si el subagente puede consultar Engram, puede refinar la búsqueda por su cuenta.

## Resumen de responsabilidades

- **Orquestador**: coordina, invoca subagentes, mantiene estado en Engram, decide cuándo re-ejecutar tests o pasar al debugger.
- **test-runner**: ejecuta tests, reporta resultado.
- **git-pr**: git (rama, commit, push, PR) siguiendo Conventional Commits.
- **debugger**: diagnostica y corrige cuando los tests fallan.
- **ai-worker**: implementa lo que pida el orquestador (feature, tests iniciales, refactor).
