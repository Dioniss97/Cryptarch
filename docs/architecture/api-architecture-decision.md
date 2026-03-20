# Decisión de arquitectura: API (FastAPI)

**Estado**: Aceptado  
**Fecha**: 2025-03-12  
**Alcance**: `apps/api`

---

## Decisión (recomendación oficial)

El backend de la API sigue **una sola** arquitectura con nombre reconocido:

> **Hexagonal Architecture** (Ports & Adapters)

No mezclamos varios estilos con nombres distintos. Cualquier búsqueda tipo *"Hexagonal Architecture FastAPI"* o *"Ports and Adapters Python"* debe corresponder a esta estructura, para poder reutilizar skills, tutoriales y convenciones existentes.

---

## Otras opciones consideradas

Se compararon al menos tres arquitecturas con nombre estándar; esta es la elegida tras el análisis.

| Criterio | Hexagonal | Clean Architecture | Layered / N-tier |
|----------|------------|--------------------|-------------------|
| **Encaje con Cryptarch** | Core sin frameworks; puertos claros; FastAPI = driving, persistencia = driven. Multi-tenant encaja en boundaries. | Mismo encaje conceptual (círculos = core + adapters). Más capas formales (entities, use cases, interface adapters). | Encaje directo: Presentation → Application → Domain → Infrastructure. El código actual está más cerca de esto. |
| **Documentación / skills** | Muy buena: "Hexagonal FastAPI", "Ports and Adapters Python" con muchos resultados; Alistair Cockburn estándar. | Muy buena; a veces más orientada a enterprise/Java; en Python hay muchos ejemplos. | Buena; "Layered architecture FastAPI" o "N-tier"; a veces genérico o mezclado con "onion". |
| **Claridad del nombre** | Un solo patrón muy reconocido: ports & adapters. | Muy reconocido (Uncle Bob); terminología de círculos e interactors. | Estándar pero menos "marca" única; se solapa con "capas" o "onion". |
| **Complejidad de adopción** | Estructura mínima clara: core + ports + adapters. Migración desde estado actual: introducir ports y mover persistencia a driven. | Riesgo de sobreingeniería si se aplican todas las capas al pie de la letra; en la práctica para una API REST se solapa con Hexagonal. | La más sencilla de adoptar respecto al código actual; menos vocabulario específico. |

**Por qué no Clean Architecture (como nombre único)**: En la práctica para una API REST con FastAPI, Clean y Hexagonal se traducen en una estructura muy similar. Clean añade más terminología (círculos, interactors) y capas formales; para este proyecto Hexagonal ofrece el mismo beneficio (dominio aislado, dependencias invertidas) con un nombre igual de reconocido y menos riesgo de sobreingeniería.

**Por qué no Layered / N-tier (como nombre único)**: Encaja bien y es fácil de adoptar, pero "Layered" es más genérico y menos útil como búsqueda única para skills y tutoriales. Hexagonal da un patrón con nombre concreto (ports & adapters) y la misma separación de responsabilidades.

**Vertical Slice**: Se consideró; es más común en ecosistemas .NET (MediatR). En Python/FastAPI hay menos recursos y el proyecto ya está organizado por capas/dominio; no se eligió.

---

## Por qué Hexagonal (resumen)

| Criterio | Hexagonal |
|----------|------------|
| **Reconocible** | Nombre estándar (Alistair Cockburn); muchos artículos, cursos y ejemplos. |
| **Bien definido** | Core sin dependencias de frameworks; puertos (interfaces); adaptadores (entrada/salida). |
| **Compatible con FastAPI** | Routers = adaptadores de entrada; schemas = contrato HTTP; DI para inyectar puertos. |
| **Ni corto ni sobreingeniería** | Estructura mínima clara: core + ports + adapters (driving + driven). |
| **No Frankenstein** | Un solo patrón; no mezcla de "un poco de Clean + un poco de DDD" con nombres propios. |

---

## Estructura de carpetas (estándar Hexagonal)

```
apps/api/
├── main.py
├── config.py
├── dependencies.py          # get_db, get_current_user, require_admin (usados por adapters)
│
├── core/                     # HEXAGON: centro (sin dependencias de FastAPI ni SQLAlchemy en lógica)
│   ├── domain/               # Entidades y servicios de dominio
│   │   ├── models.py         # Entidades (ORM aquí por simplicidad; opcionalmente en driven)
│   │   └── permission_service.py
│   ├── application/         # Casos de uso (orquestan puertos + dominio)
│   │   ├── user.py
│   │   ├── tag.py
│   │   ├── group.py
│   │   └── ...              # Un módulo por agregado/feature
│   └── ports/               # PUERTOS: interfaces (contratos que el core necesita)
│       ├── user_repository.py   # Protocol/ABC: get_by_id, list_by_tenant, create, ...
│       ├── tag_repository.py
│       └── ...
│
├── adapters/
│   ├── driving/             # ADAPTADORES DE ENTRADA (llamadas que entran al sistema)
│   │   ├── http/            # FastAPI
│   │   │   ├── admin/       # Rutas /admin/*
│   │   │   │   └── routes.py
│   │   │   └── auth/        # Rutas /auth/*
│   │   │       └── routes.py
│   │   └── schemas/         # Pydantic: request/response (contrato HTTP)
│   │       ├── user.py
│   │       ├── tag.py
│   │       └── ...
│   │
│   └── driven/              # ADAPTADORES DE SALIDA (llamadas que salen: BD, colas, etc.)
│       └── persistence/
│           ├── db.py        # SessionLocal, get_db si se desea agrupar aquí
│           ├── user_repository.py   # Implementa ports.UserRepository
│           ├── tag_repository.py
│           └── ...
│
├── migrations/
└── tests/
```

---

## Mapeo de conceptos

| Concepto Hexagonal | En este proyecto |
|--------------------|------------------|
| **Core** | `core/` (domain + application + ports). Sin imports de FastAPI ni Session en application/domain. |
| **Puerto** | Interfaz en `core/ports/` (ej. `UserRepository`: list_by_tenant, get_by_id, create, ...). |
| **Adaptador de entrada** | `adapters/driving/http/`: routers FastAPI; usan schemas y llaman a application (use cases). |
| **Adaptador de salida** | `adapters/driven/persistence/`: clases que implementan los ports y usan Session + ORM. |
| **Dominio** | `core/domain/`: entidades (models) y `permission_service` (domain service). |
| **Casos de uso** | `core/application/*.py`: reciben puertos por inyección y orquestan flujos (crear usuario, listar tags, etc.). |

---

## Reglas prácticas

1. **Routers (driving)** solo: validar entrada (schemas), llamar a un caso de uso en `core.application`, devolver respuesta (schema). No acceden a BD ni conocen repositorios concretos.
2. **Casos de uso (application)** reciben los **ports** (repositorios) por inyección; no importan implementaciones de `adapters.driven`.
3. **Implementaciones de repos** (driven) viven en `adapters/driven/persistence/` e implementan las interfaces de `core/ports`.
4. **Tenant y auth**: se resuelven en el adaptador de entrada (dependencies) y se pasan a los use cases (ej. `tenant_id`, `current_user_id`); el core no conoce JWT ni FastAPI.
5. **Config y DB**: `config.py` y la creación de `Session` pueden estar en raíz o en `adapters/driven/persistence/db.py`; `get_db` se inyecta en los routers y se pasa a los use cases que lo necesiten (o se inyectan los repos ya construidos con la sesión).

---

## Referencias útiles

- Búsquedas recomendadas: *"Hexagonal Architecture FastAPI"*, *"Ports and Adapters Python"*.
- La documentación oficial de FastAPI no impone una arquitectura; esta estructura es compatible con [FastAPI – Project Structure](https://fastapi.tiangolo.com/tutorial/bigger-applications/) agrupando por **capas hexagonales** (core / driving / driven) en lugar de solo por feature.

---

## Resumen en una frase

**La API sigue Hexagonal Architecture (Ports & Adapters): core (domain + application + ports), adapters driving (HTTP con FastAPI y schemas), adapters driven (persistence con implementaciones de los ports).**
