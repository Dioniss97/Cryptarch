# Protocolo Engram y agentes (orquestador + subagentes)

Engram es la **piedra angular** de la organización de los agentes: concentra decisiones, estado de tareas, hallazgos y contexto reutilizable. Así se evita saturar la ventana de contexto y se preserva lo importante más allá de la compactación de conversaciones.

## Principios

1. **Solo el orquestador escribe en Engram**  
   El agente principal (orquestador) es el único con “permisos de escritura” conceptuales: `mem_save`, `mem_update`, `mem_delete`. Los subagentes **no** crean ni modifican memorias.

2. **Subagentes leen por referencias**  
   Si un subagente tiene acceso a Engram (MCP), solo usa **lectura**: `mem_search` y `mem_get_observation`. El orquestador le indica **qué consultar** (topic_key, observation_id o búsqueda concreta) para que el subagente no dependa de un prompt gigante ni del historial de chat.

3. **Subagentes efímeros**  
   Cada subagente cumple una misión concreta y termina; no mantiene estado entre invocaciones. Al iniciar una nueva tarea se crea un nuevo hilo/agente. La **continuidad** está en Engram y en el orquestador.

4. **Handoff por referencias, no por volcado**  
   En lugar de pegar en el prompt todo el contexto (logs, decisiones, criterios), el orquestador:
   - Escribe en Engram el contexto necesario (resumen de tarea, decisión, resumen de fallo, etc.).
   - Invoca al subagente pasando **referencias** (IDs de observación, topic_keys) e instrucciones concretas.
   - El subagente consulta Engram con esas referencias y ejecuta la misión.

## Flujo típico

```
Orquestador
  → mem_save / mem_update (contexto para la delegación)
  → Invoca subagente con: misión + referencias Engram (observation_id o topic_key / búsqueda)
Subagente
  → mem_get_observation(id=…) o mem_search(…) según lo indicado
  → Ejecuta la tarea
  → Devuelve resumen al orquestador (sin escribir en Engram)
Orquestador
  → Contrasta resultado con docs/Engram, actualiza memorias si procede
```

## Qué escribe el orquestador antes de delegar

Según el tipo de subagente:

| Subagente   | Qué escribir en Engram antes de invocar | Referencia a pasar |
|------------|------------------------------------------|--------------------|
| **ai-worker** | Contexto de la tarea: objetivo, criterios, ficheros, decisiones ya tomadas. Actualizar `tasks/<id>` con lo que el worker debe saber. | `tasks/<task_id>` o observation_id de la tarea; opcionalmente `docs/*` o `knowledge/*` relevantes. |
| **debugger**  | Resumen del fallo: fichero, test que falla, mensaje de error, traza relevante. Puede ser una nueva observación en `knowledge/` o una actualización en `tasks/<id>`. | observation_id del “brief del fallo” o topic_key (ej. `tasks/SC-209`) para que lea estado + criterios. |
| **test-runner** | Normalmente no hace falta memoria nueva; el orquestador indica scope (suite, fichero, test). Si el scope depende de una tarea, puede referenciar `tasks/<id>`. | Opcional: topic_key de la tarea para contexto. |
| **git-pr**     | Tras tests OK, la tarea ya está en Engram. Referencia a `tasks/<id>` para título/descripción del PR. | `tasks/<task_id>` o observation_id. |

## Formato de referencias al invocar un subagente

Incluir en el prompt de invocación algo como:

- **Por observation_id**: “Consulta en Engram la observación con id `<id>`; ahí está el contexto del fallo / de la tarea.”
- **Por topic_key**: “Lee en Engram el contenido de `tasks/SC-209` (mem_search por topic_key o por task id); ahí están el objetivo y los criterios.”
- **Por búsqueda**: “Haz mem_search con query `knowledge tenant_id admin guard` y usa lo que encuentres para aplicar el fix.”

Así el subagente limita sus lecturas a lo necesario y no arrastra todo el historial.

## Beneficios

- **Menos tokens**: el contexto pesado vive en Engram; el prompt al subagente son instrucciones + referencias.
- **Sin pérdida por compactación**: decisiones y hallazgos quedan en memoria persistente.
- **Trazabilidad**: cada decisión o brief de fallo tiene una observación; se puede citar en futuras tareas.
- **Reparto de carga**: el orquestador sintetiza y escribe; los subagentes ejecutan con el mínimo contexto necesario.

## Arquitectura, patrones y estructura

**El orquestador es el responsable** de documentar arquitectura, patrones de diseño, estructura de carpetas y decisiones de diseño. Es quien escribe en Engram (`docs/*`, `knowledge/*`, decisiones) y quien contrasta el código con la documentación; por tanto debe:

- Registrar nuevas decisiones o patrones cuando surjan (o cuando un subagente los proponga).
- Aplicar las skills que ya codifican estructura (fastapi-tdd, react-admin-slice, etc.) y documentar excepciones o convenciones nuevas.
- Tras refactors o cambios estructurales, actualizar docs (o delegar la redacción a ai-worker con instrucciones y luego revisar y guardar en Engram).

**Subagente opcional (architecture-reviewer)**: para misiones concretas de análisis o propuesta, el orquestador puede invocar un subagente que:

- Recibe una misión acotada (ej. “Revisa la estructura de `apps/api`, contrasta con docs/ y con las referencias Engram que te paso, y devuelve un informe: capas, posibles violaciones, sugerencias”).
- Solo lee en Engram (por referencias) y explora el repo; no escribe memorias.
- Devuelve un informe al orquestador; el orquestador decide qué guardar en Engram y qué delegar (ej. refactor a ai-worker, doc a docs-sync).

Así se mantiene un único escritor y la arquitectura no se fragmenta entre agentes.

## Resumen de responsabilidades

| Agente       | Engram (escritura) | Engram (lectura) | Rol |
|-------------|--------------------|-------------------|-----|
| Orquestador | ✅ mem_save, mem_update, mem_delete | ✅ mem_search, mem_get_observation, mem_timeline, mem_context | Coordina, contrasta con docs/Engram, escribe contexto y estado. **Documenta arquitectura y patrones.** |
| ai-worker   | ❌ | ✅ Solo con referencias dadas por orquestador | Implementa; lee tarea y criterios por ID/key. |
| debugger    | ❌ | ✅ Solo con referencias dadas por orquestador | Corrige fallos; lee brief del fallo por ID/key. |
| test-runner | ❌ | ✅ Opcional (scope o task ref) | Ejecuta tests; reporta. |
| git-pr      | ❌ | ✅ Opcional (task ref para PR) | Rama, commit, push, PR. |
| architecture-reviewer (opcional) | ❌ | ✅ Solo con referencias dadas por orquestador | Analiza estructura/patrones y reporta; el orquestador documenta y decide. |

Este protocolo se complementa con `orchestrator-flow.md` (flujo operativo), `git-workflow.md` (ciclo por tarea: rama → trabajo → test → debug → commits → push → PR) y con las reglas/skills de Engram en `.cursor/`.
