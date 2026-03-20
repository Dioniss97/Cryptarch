# Flujo Git por sprint (hasta la PR)

> Este documento define como pasar de cambios locales a PR de forma consistente.
> Si vienes desde `orchestrator-flow.md`, aqui tienes el detalle de rama/commit/push/PR.
> Si vienes desde `README.md`, te recomendamos leer antes `AGENTS.md` y `orchestrator-flow.md`.

Documento de referencia para agentes y humanos: ciclo de trabajo por sprint que termina en Pull Request. Los agentes pueden consultar este doc (o la memoria Engram `docs/git-workflow` si está digerida) para seguir el flujo sin ambigüedad.

## Modelo de ramas

| Rama      | Uso |
|-----------|-----|
| **main**  | Estable; listo para producción. Solo se actualiza por merge desde `develop` al hacer release. |
| **develop** | Integración: aquí se fusionan los sprints. Las ramas de sprint se crean desde `develop` y el PR apunta a `develop`. |
| **SprintX o SprintX-Y** | Una rama por sprint (ej. `Sprint3`, `Sprint3-1`, `Sprint3-2`). Crear desde `develop`, trabajar, testear, hacer commit/push y abrir PR hacia `develop`. |

## Ciclo por sprint (pasos en orden)

Para cada sprint (`SprintX` o `SprintX-Y`) definido:

1. **Crear rama**  
   Crear `SprintX` o `SprintX-Y` desde `develop` y cambiar a ella. Si ya existe la rama, usarla.

2. **Trabajar**  
   Implementar en esa rama (código, tests). El orquestador delega en **ai-worker** si aplica.

3. **Testear**  
   Ejecutar la suite de tests (orquestador invoca **test-runner**). No ejecutar tests manualmente desde el orquestador.

4. **Si los tests fallan: debug → volver a testear**  
   Orquestador invoca **debugger** con el reporte del fallo; el debugger corrige y reporta. Orquestador vuelve a invocar **test-runner**. Repetir hasta que todos los tests pasen.

5. **Commits legibles**  
   Hacer commit(s) con mensajes claros y acotados al scope del sprint. Usar **Conventional Commits** con prefijo obligatorio del sprint: `SprintX` o `SprintX-Y` + `type(scope): descripción en imperativo` (ej. `Sprint3-2 feat(web): improve admin workspace shell`). Preferir un commit por cambio lógico; evitar megacommits.

6. **Push**  
   Subir la rama al remoto (`git push -u origin Sprint3-2`). No hacer force push salvo indicación explícita.

7. **Abrir (o actualizar) PR**  
   Pull Request hacia **develop** (no hacia `main`). Título y descripción útiles (incluir sprint y alcance). El orquestador puede invocar el subagente **git-pr** para rama, commit, push y apertura/actualización del PR.

8. **Cerrar tareas del sprint en Engram**  
   Cuando tests pasan, cambios commiteados y PR abierta: actualizar las `tasks/<id>` del sprint con What/Why/Where/Learned y `Status: done` cuando corresponda. El humano revisa y mergea el PR en GitHub.

## Resumen en una línea

Por cada sprint: **rama desde develop → trabajar → testear → [debug → testear]* → commits legibles (Conventional) → push → PR a develop**.

## Dónde se implementa

- **Orquestador**: no ejecuta git ni tests a mano; coordina y delega (ver `orchestrator-flow.md`).
- **Subagente git-pr**: rama, commit, push y PR (detalle en `.cursor/agents/git-pr.md`).
- **Subagentes test-runner y debugger**: ver `orchestrator-flow.md`.

## Convenciones de commits (resumen)

Formato obligatorio:
- `SprintX type(scope): descripción` o `SprintX-Y type(scope): descripción`
- Ejemplo: `Sprint3-2 feat(web): add guided connector action builder`

Reglas:
- `SprintX` o `SprintX-Y` siempre al inicio del subject del commit.
- `type` debe ser uno de: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `style`, `perf`, `ci`.
- `scope` opcional pero recomendado (`api`, `web`, `worker`, `docs`).
- Tras `type(scope)` debe ir `:` y una descripción breve en imperativo, sin punto final.

Detalle completo en `.cursor/agents/git-pr.md`.

## Enlace con el resto de documentos

- Vision general y quick start: `../../README.md`.
- Roles y subagentes: `../../AGENTS.md`.
- Orquestacion end-to-end: `orchestrator-flow.md`.
- Priorizacion de trabajo por sprint: `../sprints/tasks.md`.
