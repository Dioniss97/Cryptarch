# Flujo Git por tarea (hasta la PR)

Documento de referencia para agentes y humanos: ciclo de trabajo por tarea que termina en Pull Request. Los agentes pueden consultar este doc (o la memoria Engram `docs/git-workflow` si está digerida) para seguir el flujo sin ambigüedad.

## Modelo de ramas

| Rama      | Uso |
|-----------|-----|
| **main**  | Estable; listo para producción. Solo se actualiza por merge desde `develop` al hacer release. |
| **develop** | Integración: aquí se fusionan las tareas. Las ramas de tarea se crean desde `develop` y el PR apunta a `develop`. |
| **task/\<id>** | Una rama por tarea (ej. `task/task-02`, `task/SC-209`). Crear desde `develop`, trabajar, testear, hacer commit/push y abrir PR hacia `develop`. |

## Ciclo por tarea (pasos en orden)

Para cada tarea (task ID conocido):

1. **Crear rama**  
   Crear `task/<id>` desde `develop` y cambiar a ella. Si ya existe la rama, usarla.

2. **Trabajar**  
   Implementar en esa rama (código, tests). El orquestador delega en **ai-worker** si aplica.

3. **Testear**  
   Ejecutar la suite de tests (orquestador invoca **test-runner**). No ejecutar tests manualmente desde el orquestador.

4. **Si los tests fallan: debug → volver a testear**  
   Orquestador invoca **debugger** con el reporte del fallo; el debugger corrige y reporta. Orquestador vuelve a invocar **test-runner**. Repetir hasta que todos los tests pasen.

5. **Commits legibles**  
   Hacer commit(s) con mensajes claros y acotados al scope de la tarea. Usar **Conventional Commits**: `type(scope): descripción en imperativo` (ej. `feat(api): add admin guard and GET /admin/me`). Preferir un commit por cambio lógico; evitar megacommits.

6. **Push**  
   Subir la rama al remoto (`git push -u origin task/<id>`). No hacer force push salvo indicación explícita.

7. **Abrir (o actualizar) PR**  
   Pull Request hacia **develop** (no hacia `main`). Título y descripción útiles (incluir task ID). El orquestador puede invocar el subagente **git-pr** para rama, commit, push y apertura/actualización del PR.

8. **Cerrar la tarea en Engram**  
   Cuando tests pasan, cambios commiteados y PR abierta: actualizar `tasks/<id>` con What/Why/Where/Learned y `Status: done`. El humano revisa y mergea el PR en GitHub.

## Resumen en una línea

Por cada tarea: **rama desde develop → trabajar → testear → [debug → testear]* → commits legibles (Conventional) → push → PR a develop → marcar tarea done**.

## Dónde se implementa

- **Orquestador**: no ejecuta git ni tests a mano; coordina y delega (ver `orchestrator-flow.md`).
- **Subagente git-pr**: rama, commit, push y PR (detalle en `.cursor/agents/git-pr.md`).
- **Subagentes test-runner y debugger**: ver `orchestrator-flow.md`.

## Convenciones de commits (resumen)

Tipos: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `style`, `perf`, `ci`. Scope opcional pero recomendado (`api`, `web`, `worker`, `docs`). Descripción en imperativo, sin punto final. Detalle completo en `.cursor/agents/git-pr.md`.
