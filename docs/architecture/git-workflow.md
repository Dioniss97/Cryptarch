# Flujo Git por task (hasta la PR)

> Este documento define como pasar de trabajo local a PR de forma consistente.
> Si vienes desde [orchestrator-flow.md](orchestrator-flow.md), aqui tienes el detalle de rama/commit/push/PR.
> Si vienes desde el [README.md](../../README.md), te recomendamos leer antes [AGENTS.md](../../AGENTS.md) y [orchestrator-flow.md](orchestrator-flow.md).

## Mapa del documento

| Seccion | Para que sirve |
|---|---|
| `## Modelo de ramas` | Ver estrategia de ramas (`develop`, `main`, task). |
| `## Flujo issue -> task -> branch -> PR` | Ejecutar el flujo de entrega sin mezclar backlog y ejecucion. |
| `## Convenciones de commits` | Mantener mensajes consistentes y legibles. |
| `## GitHub CLI (gh) recomendado` | Aclarar el uso permitido de `gh` y su configuracion basica. |
| `## Enlace con el resto de documentos` | Volver al mapa global de lectura. |

Documento de referencia para agentes y humanos: ciclo de trabajo que parte del backlog en GitHub Issues, pasa a ejecucion en Engram y termina en Pull Request. Los agentes pueden consultar este doc (o la memoria Engram `docs/git-workflow` si esta digerida) para seguir el flujo sin ambiguedad.

## Modelo de ramas

| Rama | Uso |
|------|-----|
| **main** | Estable; listo para produccion. Solo se actualiza por merge desde `develop` al hacer release. |
| **develop** | Integracion. Las ramas de trabajo se crean desde `develop` y el PR apunta a `develop`. |
| **task/<id>-slug** | Rama normal de trabajo por task. Se crea desde `develop`, se usa para implementar una `tasks/<id>` y se integra por PR a `develop`. |
| **docs/<slug>** | Excepcion opcional para cambios puramente documentales cuando no merece una task de ejecucion completa. |

## Flujo issue -> task -> branch -> PR

1. **Issue en GitHub**  
   El trabajo entra por un issue: captura, triage, labels, prioridad y contexto inicial. El issue sirve para backlog y seguimiento de producto.

2. **Task en Engram**  
   Cuando el item pasa a ejecucion, el orquestador crea o actualiza `tasks/<id>` en Engram y enlaza el issue. Desde ese punto, la task es la fuente de verdad operativa.

3. **Crear rama**  
   Crear `task/<id>-slug` desde `develop` y cambiar a ella. Si el cambio es solo documental y no requiere task, se permite `docs/<slug>`.
   Este paso es **obligatorio antes de implementar**: el orquestador debe pedir a `git-pr` que cree o seleccione la rama de trabajo antes de invocar a `ai-worker`.

4. **Trabajar**  
   Implementar en esa rama (codigo, docs o tests). El orquestador delega en **ai-worker** si aplica.

5. **Testear**  
   Ejecutar la suite de tests mediante **test-runner**. No ejecutar tests manualmente desde el orquestador.

6. **Si los tests fallan: debug -> volver a testear**  
   El orquestador invoca **debugger** con el reporte del fallo. Tras cada fix, se vuelve a **test-runner** hasta que todo pase.

7. **Commits legibles**  
   Hacer commit(s) con mensajes claros y acotados al scope de la task. Usar **Conventional Commits** sin prefijo de sprint. Preferir un commit por cambio logico; evitar megacommits.

8. **Push**  
   Subir la rama al remoto (`git push -u origin task/<id>-slug`). No hacer force push salvo indicacion explicita.

9. **Abrir o actualizar PR**  
   Abrir Pull Request hacia **develop** (no hacia `main`). El cuerpo del PR debe enlazar al issue y a la task. El orquestador puede invocar **git-pr** para rama, commit, push y PR.

10. **Verificar CI en GitHub**  
   Una PR abierta **no cierra** la task por si sola. El orquestador invoca **ci-triage** para revisar los checks de GitHub Actions (consulta con `gh`, logs si fallan, clasificacion y siguiente paso). Mantener `tasks/<id>` en `Status: in_progress` hasta que los checks relevantes esten **verdes** o la task pase a `Status: blocked` con motivo explicito (permisos, infra, decision humana). Cuando CI este verde, entonces si: actualizar `tasks/<id>` con What / Why / Where / Learned y `Status: done`. El humano revisa y mergea el PR en GitHub.

## Convencion de enlazado

- **Issue -> Task**: guardar en `tasks/<id>` el numero o URL del issue relacionado.
- **Task -> Branch**: usar `task/<id>-slug`.
- **PR -> Issue/Task**: incluir ambos enlaces en el cuerpo del PR.

Plantilla minima recomendada para el cuerpo del PR:

```md
## Enlaces
- Issue: #123
- Task: tasks/SC-209

## Resumen
- Cambio principal 1
- Cambio principal 2

## Testing
- [ ] Pendiente
```

## Resumen en una linea

Por cada item ejecutable: **issue en GitHub -> task en Engram -> rama `task/<id>-slug` -> trabajar -> testear -> [debug -> testear]* -> commits legibles -> push -> PR a `develop` -> ci-triage (checks CI) -> [test-runner/debugger -> git-pr -> ci-triage]* hasta verde o bloqueo -> entonces `Status: done` en Engram**.

## Donde se implementa

- **Orquestador**: no ejecuta git ni tests a mano; coordina y delega (ver [orchestrator-flow.md](orchestrator-flow.md)).
- **Subagente git-pr**: rama, commit, push y PR (detalle en [`.cursor/agents/git-pr.md`](../../.cursor/agents/git-pr.md)).
- **Subagentes test-runner y debugger**: ver [orchestrator-flow.md](orchestrator-flow.md).

## Convenciones de commits

Formato obligatorio:
- `type(scope): descripcion en imperativo`
- Ejemplo: `feat(web): add guided connector action builder`

Reglas:
- `type` debe ser uno de: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `style`, `perf`, `ci`.
- `scope` opcional pero recomendado (`api`, `web`, `worker`, `docs`).
- Tras `type(scope)` debe ir `:` y una descripcion breve en imperativo, sin punto final.
- Si el commit mezcla tipos, usar el tipo principal o separar en varios commits.

Detalle completo en [`.cursor/agents/git-pr.md`](../../.cursor/agents/git-pr.md).

## GitHub CLI (gh) recomendado

`gh` es util para consultar issues/PRs y abrir PRs sin salir del terminal, pero no sustituye el flujo anterior.

Uso recomendado:
- **Consultas**: `gh issue view`, `gh issue list`, `gh pr view`, `gh pr status`, `gh pr checks` (estado de checks de la PR; ver subagente **ci-triage** para triage de fallos).
- **PRs**: `gh pr create`, `gh pr edit`.
- **Issues**: reservar la creacion/actualizacion a sesiones de triage o cuando se pida explicitamente.

Configuracion basica para un repo dentro de una organizacion:
- Usar una cuenta con acceso real al repositorio y a la organizacion.
- Tener `gh` autenticado con los permisos que requiera el repo para leer/escribir issues y PRs. Si la organizacion usa SSO, la sesion debe estar autorizada.
- Comprobar el estado con `gh auth status` antes de depender de `gh`.
- Mantener el uso con privilegio minimo: consultas, creacion/actualizacion de issues y PRs, nunca acciones administrativas salvo instruccion explicita.

Ramas remotas:
- No borrar ramas remotas desde agentes salvo instruccion explicita.
- El borrado normal debe recaer en la opcion de GitHub **Automatically delete head branches** al fusionar el PR.

## Enlace con el resto de documentos

- Vision general y quick start: [README.md](../../README.md).
- Roles y subagentes: [AGENTS.md](../../AGENTS.md).
- Orquestacion end-to-end: [orchestrator-flow.md](orchestrator-flow.md).
- Priorizacion de trabajo por sprint: [tasks.md](../sprints/tasks.md).
