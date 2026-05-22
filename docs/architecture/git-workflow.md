# Flujo Git por task (hasta la PR)

> Este documento define como pasar de trabajo local a PR de forma consistente.
> Si vienes desde [orchestrator-flow.md](orchestrator-flow.md), aqui tienes el detalle de rama/commit/push/PR.
> Si vienes desde el [README.md](../../README.md), te recomendamos leer antes [AGENTS.md](../../AGENTS.md) y [orchestrator-flow.md](orchestrator-flow.md).

## Mapa del documento

| Seccion | Para que sirve |
|---|---|
| `## Modelo de ramas` | Ver estrategia de ramas (`develop`, `main`, `CRYPT-*-slug`). |
| `## Convenciones de PR` | Titulo y cuerpo alineados con Jira y Conventional Commits. |
| `## Flujo Jira -> Engram -> branch -> PR` | Ejecutar el flujo de entrega sin mezclar backlog y contexto operativo. |
| `## Convenciones de commits` | Mantener mensajes consistentes y legibles. |
| `## GitHub CLI (gh) recomendado` | Aclarar el uso permitido de `gh` para PRs y CI. |
| `## Enlace con el resto de documentos` | Volver al mapa global de lectura. |

Documento de referencia para agentes y humanos: ciclo de trabajo que parte del backlog en Jira (`CRYPT`), usa Engram como memoria operativa y termina en Pull Request. Los agentes pueden consultar este doc (o la memoria Engram `docs/git-workflow` si esta digerida) para seguir el flujo sin ambiguedad.

## Modelo de ramas

| Rama | Uso |
|------|-----|
| **main** | Estable; listo para produccion. Solo se actualiza por merge desde `develop` al hacer release. |
| **develop** | Integracion. Las ramas de trabajo se crean desde `develop` y el PR apunta a `develop`. |
| **CRYPT-123-slug** | Rama normal de trabajo por Jira task (sin prefijo `task/`). Se crea desde `develop`, implementa `CRYPT-*` y se integra por PR a `develop`. |
| **docs/<slug>** | Excepcion opcional para cambios puramente documentales cuando no merece una task de ejecucion completa. |

## Flujo Jira -> Engram -> branch -> PR

1. **Issue en Jira (`CRYPT-*`)**  
   El trabajo entra por Jira: captura, triage, tipo, estado, prioridad, sprint y contexto inicial. Jira sirve para backlog y seguimiento de ejecución.

2. **Contexto en Engram**  
   Cuando el item pasa a ejecucion, el orquestador crea o actualiza `tasks/CRYPT-*` en Engram y enlaza el issue Jira. Jira mantiene estado; Engram conserva contexto, decisiones y outcome para agentes.

3. **Crear rama**  
   Crear `CRYPT-123-slug` desde `develop` y cambiar a ella. Si el cambio es solo documental y no requiere task, se permite `docs/<slug>`.
   Este paso es **obligatorio antes de implementar**: el orquestador debe pedir a `git-pr` que cree o seleccione la rama de trabajo antes de invocar a `ai-worker`.

4. **Trabajar**  
   Implementar en esa rama (codigo, docs o tests). El orquestador delega en **ai-worker** si aplica.

5. **Testear**  
   Ejecutar la suite de tests mediante **test-runner**. No ejecutar tests manualmente desde el orquestador.

6. **Si los tests fallan: debug -> volver a testear**  
   El orquestador invoca **debugger** con el reporte del fallo. Tras cada fix, se vuelve a **test-runner** hasta que todo pase.

7. **Commits legibles**  
   Mensajes **Conventional Commits** con prefijo Jira: `CRYPT-123 type(scope): descripcion`. Un commit por cambio logico de cada tarjeta; evitar megacommits. No usar el prefijo de rama antiguo `task/` en ramas nuevas.

8. **Push**  
   Subir la rama al remoto (`git push -u origin CRYPT-123-slug`). No hacer force push salvo indicacion explicita.

9. **Abrir o actualizar PR**  
   Abrir Pull Request hacia **develop** (no hacia `main`). El **titulo** sigue la misma convencion que los commits (ver [Convenciones de PR](#convenciones-de-pr)). El cuerpo enlaza Jira `CRYPT-*` y Engram `tasks/CRYPT-*` si existe. El orquestador puede invocar **git-pr** para rama, commit, push y PR.

10. **Verificar CI en GitHub**  
   Una PR abierta **no cierra** la task por si sola. El orquestador invoca **ci-triage** para revisar los checks de GitHub Actions (consulta con `gh`, logs si fallan, clasificacion y siguiente paso). Mantener Jira/Engram en progreso hasta que los checks relevantes esten **verdes** o la task pase a `blocked` con motivo explicito (permisos, infra, decision humana). Cuando CI este verde, entonces si: actualizar Jira y `tasks/CRYPT-*` con What / Why / Where / Learned y estado final. El humano revisa y mergea el PR en GitHub.

## Convencion de enlazado

- **Jira -> Engram**: guardar en `tasks/CRYPT-*` el enlace o key de Jira.
- **Jira -> Branch**: `CRYPT-123-slug` (clave Jira + slug corto en kebab-case). **No** usar `task/CRYPT-123-slug` (convencion obsoleta; ramas historicas pueden conservarla hasta borrarse).
- **Jira -> Commit**: `CRYPT-123 type(scope): descripcion` (Conventional Commits).
- **Jira -> PR titulo**: misma forma que el commit principal o un resumen de la entrega (ver abajo).
- **PR -> Jira/Engram**: incluir ambos enlaces en el cuerpo del PR.

## Convenciones de PR

**Titulo** (obligatorio, primera linea visible en GitHub):

```
CRYPT-123 type(scope): descripcion breve de la entrega
```

- Misma gramatica que los commits: prefijo `CRYPT-*`, tipo conventional (`feat`, `fix`, `docs`, `chore`, `test`, …), scope opcional.
- **Una tarjeta**: titulo con esa clave (ej. `CRYPT-8 feat(api): add GET /actions for user`).
- **Varias tarjetas en la misma PR**: listar claves al inicio, luego tipo y resumen (ej. `CRYPT-11 CRYPT-47 CRYPT-12 feat: user preferences API, profile UI and E2E smoke`).
- **Solo documentacion** sin tarjeta Jira: rama `docs/<slug>` y titulo `docs(scope): descripcion` (sin prefijo `CRYPT-` si no hay issue).

**Cuerpo**: plantilla minima (enlaces + resumen + testing). No sustituye el titulo estructurado.

Plantilla minima recomendada para el cuerpo del PR:

```md
## Enlaces
- Jira: CRYPT-123
- Engram: tasks/CRYPT-123

## Resumen
- Cambio principal 1
- Cambio principal 2

## Testing
- [ ] Pendiente
```

## Resumen en una linea

Por cada item ejecutable: **Jira `CRYPT-*` -> contexto Engram `tasks/CRYPT-*` -> rama `CRYPT-*-slug` -> trabajar -> testear -> [debug -> testear]* -> commits atomizados por tarjeta -> push -> PR a `develop` -> ci-triage (checks CI) -> [test-runner/debugger -> git-pr -> ci-triage]* hasta verde o bloqueo -> entonces `done` en Jira/Engram**.

## Donde se implementa

- **Orquestador**: no ejecuta git ni tests a mano; coordina y delega (ver [orchestrator-flow.md](orchestrator-flow.md)).
- **Subagente git-pr**: rama, commit, push y PR (detalle en [`.cursor/agents/git-pr.md`](../../.cursor/agents/git-pr.md)).
- **Subagentes test-runner y debugger**: ver [orchestrator-flow.md](orchestrator-flow.md).

## Convenciones de commits

Formato obligatorio (un commit por cambio logico; prefijo Jira siempre):

```
CRYPT-123 type(scope): descripcion en imperativo
```

Ejemplos:
- `CRYPT-11 feat(api): add GET/PATCH /me/preferences`
- `CRYPT-12 test(web): add Playwright smoke for admin and chat`
- `CRYPT-47 fix(web): apply theme from preferences in ProfileMenu`
- `CRYPT-55 docs: document input_schema_json contract`

Reglas:
- **Prefijo**: clave Jira de la tarjeta que cubre el cambio (`CRYPT-*`).
- **type**: `feat` (feature), `fix`, `docs`, `chore`, `refactor`, `test`, `style`, `perf`, `ci`.
- **scope** opcional pero recomendado (`api`, `web`, `worker`, `docs`).
- Descripcion breve en imperativo, sin punto final.
- **Atomizar**: si una rama agrupa varias tarjetas (p. ej. CRYPT-11 + CRYPT-47 + CRYPT-12), un commit por tarjeta/cambio principal; no megacommits sin prefijo Jira.
- Si un commit mezcla tipos de la misma tarjeta, usar el tipo principal o separar en varios commits.

Detalle completo en [`.cursor/agents/git-pr.md`](../../.cursor/agents/git-pr.md).

## GitHub CLI (gh) recomendado

`gh` es util para consultar/abrir PRs y revisar CI sin salir del terminal, pero no sustituye el flujo anterior.

Uso recomendado:
- **Consultas**: `gh pr view`, `gh pr status`, `gh pr checks` (estado de checks de la PR; ver subagente **ci-triage** para triage de fallos).
- **PRs**: `gh pr create`, `gh pr edit`.
- **Issues de GitHub**: no usarlos como backlog de producto. Jira (`CRYPT`) es la fuente de backlog.

Configuracion basica para un repo dentro de una organizacion:
- Usar una cuenta con acceso real al repositorio y a la organizacion.
- Tener `gh` autenticado con los permisos que requiera el repo para leer/escribir PRs. Si la organizacion usa SSO, la sesion debe estar autorizada.
- Comprobar el estado con `gh auth status` antes de depender de `gh`.
- Mantener el uso con privilegio minimo: consultas, creacion/actualizacion de issues y PRs, nunca acciones administrativas salvo instruccion explicita.

Ramas remotas:
- No borrar ramas remotas desde agentes salvo instruccion explicita.
- El borrado normal debe recaer en la opcion de GitHub **Automatically delete head branches** al fusionar el PR.

## Enlace con el resto de documentos

- Vision general y quick start: [README.md](../../README.md).
- Roles y subagentes: [AGENTS.md](../../AGENTS.md).
- Orquestacion end-to-end: [orchestrator-flow.md](orchestrator-flow.md).
- Priorizacion de trabajo por sprint: Jira (`CRYPT`).
