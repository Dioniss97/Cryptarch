# Encuadre: Hexagonal, Clean Architecture, DDD y Clean Code

**Objetivo**: Aclarar la relación entre el refactor de la API (opciones A/B/C) y las escuelas de arquitectura conocidas, y fijar una recomendación explícita para Cryptarch.

---

## 1. Relación con cada enfoque

### Hexagonal (Ports & Adapters)

**Qué es en una frase**: La lógica de negocio vive en el centro; todo acceso externo (HTTP, BD, colas) entra o sale mediante **puertos** (interfaces) y **adaptadores** (implementaciones concretas).

**Cómo se traduce en nuestra API**: Los **puertos** son las interfaces que define el dominio o la aplicación para persistencia y servicios (por ejemplo: `UserRepository`, `TagRepository`; si hubiera interfaces para “obtener usuario por id”, “listar tags por tenant”). Los **adaptadores de entrada** son los routers FastAPI (reciben HTTP y llaman a servicios); los **adaptadores de salida** son las implementaciones concretas que hablan con SQL/SQLAlchemy (repositorios que usan `Session` y modelos ORM). ¿Lo que hacemos (routers → services → repositories, domain en el centro) es hexagonal? **Sí**, en la medida en que: (1) los routers no conocen la BD y solo orquestan; (2) los servicios/casos de uso no dependen de FastAPI ni de SQL; (3) la persistencia se abstrae detrás de repositorios (aunque hoy no siempre como interfaces formales). Si los repos se definen como interfaces en dominio/aplicación y las implementaciones viven en infraestructura, el encaje es completo.

### Clean Architecture

**Qué es en una frase**: Círculos concéntricos donde las dependencias apuntan hacia dentro: entidades en el centro, luego casos de uso, luego adaptadores de interfaz e infraestructura; el dominio no depende de frameworks ni de la BD.

**Cómo mapean nuestras capas**: **Domain** = entidades (modelos de dominio o, en nuestra implementación actual, modelos ORM que representan el dominio) + servicios de dominio como `permission_service`. **Application** = casos de uso / servicios de aplicación (CreateUser, ListTags, etc.) que orquestan y usan repositorios. **Infrastructure** = implementaciones de repositorios (SQL/SQLAlchemy), ORM, conexión a BD. **Presentation** = routers FastAPI, schemas Pydantic, dependencias (auth, tenant). ¿Es Clean Architecture o un subconjunto? Es un **subconjunto práctico**: tenemos la separación de responsabilidades (dominio, aplicación, infraestructura, presentación) y la regla de dependencias (nada del centro depende de FastAPI ni de SQL); no exigimos todas las capas formales de Uncle Bob (p. ej. objetos de entidad puros separados del ORM en todos los módulos) ni boundaries físicos estrictos por carpeta en cada feature. Es “Clean Architecture simplificada” con layout por dominio/features.

### DDD (Domain-Driven Design)

**Qué es en una frase**: Modelado del negocio con bounded contexts, agregados, entidades, value objects, servicios de dominio y repositorios como interfaces en el dominio; el lenguaje ubicuo y los límites de contexto guían la estructura.

**Cómo encaja con nuestra opción B**: Nuestra **opción B (por feature)** puede verse como **bounded contexts ligeros**: cada feature (users, tags, saved_filters, groups, connectors, actions, documents) agrupa un área de dominio; no son contextos con fronteras de equipo ni lenguajes distintos, pero sí unidades de cohesión. **permission_service** es un **domain service** en sentido DDD: orquesta reglas que involucran a varias entidades (User, Group, SavedFilter, Action, Document) y no pertenecen a un solo agregado. Los repositorios, en un DDD estricto, se definen como interfaces en el dominio y se implementan en infraestructura; en nuestro refactor podemos acercarnos a eso (interfaces en domain/application, implementaciones en infrastructure). **Recomendación**: **DDD táctico** — usar agregados y servicios de dominio donde aporten claridad (p. ej. “User + UserTags” como agregado; permission_service como domain service), sin adoptar DDD estratégico completo (context maps, múltiples bounded contexts formales) a menos que el producto crezca en equipos o dominios.

### Clean Code

**Qué es en una frase**: Prácticas de código legible y mantenible: nombres expresivos, funciones pequeñas y con un solo propósito, DRY, bajo acoplamiento, tests, comentarios solo cuando aporten.

**Relación**: Es **complementario** y **transversal** a la arquitectura. La decisión de capas (Hexagonal, Clean, DDD) dice *dónde* va cada responsabilidad; Clean Code dice *cómo* se escribe el código dentro de cada capa. No compiten; se aplican a la vez. En Cryptarch, aplicar Clean Code dentro de routers, servicios y repositorios refuerza el beneficio del refactor.

---

## 2. Croquis del flujo y encaje de conceptos

```
  [HTTP Request]
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │  PRESENTATION (adaptador de entrada / interface adapter)         │
  │  Router FastAPI, schemas Pydantic, Depends(get_db, require_admin)│
  └─────────────────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │  APPLICATION (use cases / Clean Architecture circle)             │
  │  Service: CreateUser, ListTags, UpdateGroup, ...                 │
  │  → Llama a repos (puertos) y a domain services                   │
  └─────────────────────────────────────────────────────────────────┘
        │
        ├──────────────────────────────────┐
        ▼                                  ▼
  ┌─────────────────────┐    ┌─────────────────────────────────────┐
  │  DOMAIN             │    │  INFRASTRUCTURE (adaptador de salida)│
  │  • Entidades/ORM    │    │  Repository impl.: UserRepository,   │
  │  • permission_      │    │  TagRepository, ... → Session, SQL   │
  │    service (domain   │    │  (implementan los “puertos”         │
  │    service DDD)     │    │  definidos en domain/application)    │
  │  • Interfaces repo  │    └─────────────────────────────────────┘
  │    (puertos Hex.)   │                      │
  └─────────────────────┘                      ▼
                                        ┌─────────────┐
                                        │  DB (Postgres)│
                                        └─────────────┘
```

- **Hexagonal**: Puertos = interfaces de repos (y opcionalmente de servicios externos); adaptadores de entrada = routers; adaptadores de salida = implementaciones de repos + ORM.
- **Clean Architecture**: Círculo “entities” = modelos de dominio (y/o ORM que los representa); “use cases” = servicios de aplicación; “interface adapters” = routers + schemas; “frameworks & drivers” = FastAPI, SQLAlchemy, Postgres.
- **DDD**: Agregados = entidades raíz + entidades hijas por feature (ej. User + UserTags); domain service = permission_service; repositorios = interfaces en dominio, implementaciones en infraestructura.

---

## 3. Recomendación explícita para Cryptarch

**Etiqueta recomendada** (una frase para documentación y conversaciones):

> La API sigue una **arquitectura en capas inspirada en Hexagonal y Clean Architecture**, con **organización por features (dominio)** y un **shared** para cross-cutting (auth, tenant, permission_service). Opcionalmente se puede describir como **DDD táctico** cuando se usen agregados y domain services de forma explícita.

**Variante más corta**:  
“Hexagonal + estructura por features (B), con shared para auth, tenant y permisos.”

---

## 4. Dónde documentar en el proyecto

| Dónde | Qué poner |
|-------|-----------|
| **docs/architecture/** | Este documento (`hexagonal-clean-ddd-framing.md`) como referencia. En `architecture-option-c-review.md` (o en un `README.md` de arquitectura) se puede enlazar aquí y repetir la frase de recomendación. |
| **README de la API** (`apps/api/README.md`) | Una frase tipo: *“La API sigue una arquitectura en capas inspirada en Hexagonal y Clean Architecture, con organización por features (dominio) y shared para cross-cutting (auth, tenant, permission_service).”* |

**Frase sugerida para README y docs**:

> La API sigue una arquitectura en capas inspirada en Hexagonal y Clean Architecture, con organización por features (dominio) y shared para cross-cutting (auth, tenant, permission_service).
