# Informe: Evaluación Opción C y comparativa A vs B vs C

**Autor**: architecture-reviewer  
**Fecha**: 2025-03-12  
**Alcance**: Recomendación de arquitectura para `apps/api` (FastAPI) del proyecto Cryptarch.

---

## 1. Descripción de la Opción C adaptada a Cryptarch

### 1.1 Idea general

Cada **módulo** es una carpeta con mini Clean Architecture interna:

- **domain/**: entidades y políticas (reglas de negocio puras).
- **application/**: DTOs, commands/queries, casos de uso (orquestación).
- **infrastructure/**: modelos ORM y repositorio (Postgres).
- **presentation/**: router, schemas Pydantic, dependencias propias del módulo.

### 1.2 Qué cuenta como módulo en Cryptarch

| Módulo | Contenido típico | Notas |
|--------|------------------|--------|
| **tenant** | CRUD tenants (si existe en API); políticas de tenant | Suele ser mínimo (solo super-admin). |
| **user** | CRUD users, user_tags; políticas de usuario | |
| **tag** | CRUD tags | |
| **saved_filter** | CRUD saved_filters, saved_filter_tags | |
| **group** | CRUD groups, group_user_filter, group_action_filter, group_document_filter | |
| **connector** | CRUD connectors | |
| **action** | CRUD actions, action_tags | |
| **document** | CRUD documents, document_tags; estado indexing; futuro enlace a ingestión | |
| **auth** | Login, JWT, hash/verify password, get_current_user, require_admin | |

**Recomendación de módulos para Cryptarch**: `auth`, `user`, `tag`, `saved_filter`, `group`, `connector`, `action`, `document`. Opcionalmente `tenant` si la API expone CRUD de tenants. Evitar módulos por cada tabla de enlace; las tablas de enlace viven en el módulo del agregado (ej. `UserTag` en user, `GroupUserFilter` en group).

### 1.3 Árbol de carpetas sugerido (Opción C)

```
apps/api/
├── main.py
├── config.py
├── shared/                          # Compartido entre módulos
│   ├── __init__.py
│   ├── db.py                        # get_db, SessionLocal, engine
│   ├── auth.py                      # CurrentUser, get_current_user, require_admin
│   ├── uuid_utils.py                # _parse_uuid, _normalize_uuid
│   └── domain/
│       ├── __init__.py
│       └── permission_service.py   # entity_has_all_filter_tags, resolve_effective_*_ids
├── modules/
│   ├── auth/
│   │   ├── domain/                  # (vacío o políticas de auth)
│   │   ├── application/             # LoginUseCase, DTOs
│   │   ├── infrastructure/          # (hash en application o shared si se prefiere)
│   │   └── presentation/            # router, schemas, dependencies
│   ├── user/
│   │   ├── domain/                  # Entidad User (o interfaces); políticas
│   │   ├── application/             # CreateUser, UpdateUser, ListUsers, DTOs
│   │   ├── infrastructure/         # User ORM, UserTag ORM, UserRepository
│   │   └── presentation/            # router, schemas (UserCreateBody, etc.)
│   ├── tag/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/          # Tag ORM, TagRepository
│   │   └── presentation/
│   ├── saved_filter/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/          # SavedFilter, SavedFilterTag, Repository
│   │   └── presentation/
│   ├── group/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/          # Group, Group*Filter, Repository
│   │   └── presentation/
│   ├── connector/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── presentation/
│   ├── action/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/          # Action, ActionTag, Repository
│   │   └── presentation/
│   └── document/
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       └── presentation/
├── migrations/                      # Alembic; importa Base desde shared o desde un único módulo “schema”
└── tests/
    ├── conftest.py
    ├── test_auth.py
    └── ... (por módulo o por capa)
```

**Decisiones importantes para Opción C**:

- **Modelos ORM y Base**: Las entidades SQLAlchemy con FKs entre sí (User → Tenant, Action → Connector, etc.) pueden vivir en un único sitio para no duplicar relaciones: por ejemplo `shared/infrastructure/models.py` (o `shared/domain/models.py` si se mantiene la convención actual de “domain = modelos”) con todos los modelos, y cada módulo solo expone **repositorios** que usan esos modelos. Así se evita tener que importar “User” desde `modules.user.infrastructure` en `modules.group.infrastructure` para FKs.
- **permission_service**: Sigue en **shared/domain/permission_service.py** porque cruza user, group, saved_filter, action, document. No se reparte por módulos.
- **shared/auth**: `get_db`, `CurrentUser`, `get_current_user`, `require_admin` en `shared/db.py` y `shared/auth.py` (o todo en `shared/auth.py`). Toda ruta admin depende de `require_admin`; las de chat dependerán de `get_current_user` y del permission_service.

### 1.4 Dónde vive lo compartido (resumen)

| Elemento | Ubicación en Opción C |
|----------|------------------------|
| tenant_id / scoping | Inyectado vía `CurrentUser` (JWT); cada repositorio/use case recibe `tenant_id` y filtra. No middleware obligatorio; depende de `require_admin` + uso consistente en repos. |
| CurrentUser, get_current_user, require_admin | `shared/auth.py` |
| get_db, SessionLocal, engine | `shared/db.py` |
| permission_service (entity_has_all_filter_tags, resolve_effective_*) | `shared/domain/permission_service.py` |
| UUID parse/normalize | `shared/uuid_utils.py` |
| Modelos ORM (Base, Tenant, User, Tag, …) | Recomendado: `shared/infrastructure/models.py` (o mantener `shared/domain/models.py` por coherencia con docs). |

---

## 2. Comparativa A vs B vs C

| Criterio | A – Por capas técnicas | B – Por feature/dominio | C – Módulos autocontenidos |
|----------|-------------------------|--------------------------|-----------------------------|
| **Estructura** | `schemas/`, `services/`, `repositories/`, `domain/`, routers en `api/v1/admin` y `auth` | `features/users/`, `features/tags/`, etc., cada uno con schemas, repository, service, router (sin subcapas) | `modules/<nombre>/` con domain, application, infrastructure, presentation + `shared/` |
| **Multi-tenant** | Fácil: un solo lugar para repos/servicios; tenant_id en dependencias. | Fácil: cada feature aplica tenant en su repo/servicio. | Fácil si shared expone CurrentUser y todos los use cases reciben tenant_id; riesgo de olvido en un módulo. |
| **TDD / tests** | Tests por capa (domain, services, repos) o por endpoint. | Tests por feature (aislamiento por carpeta). | Tests por módulo o por capa dentro del módulo; más archivos pero mejor encapsulación. |
| **Evolución chat/RAG/permisos** | permission_service en domain; chat consume mismo servicio. | permission_service en feature “permissions” o shared. | permission_service en shared; chat sería otro “módulo” o conjunto de rutas que usan shared. |
| **Tamaño actual (~1100 líneas admin)** | Refactor: extraer services + repos desde routes; schemas ya separables. | Refactor: partir routes en features (users, tags, …); cada uno con su servicio/repo. | Refactor más grande: crear 8+ módulos, repartir domain/application/infra/presentation; mayor número de archivos. |
| **Equipo pequeño / solo** | Bajo overhead; estructura simple y predecible. | Medio; nombres de features claros. | Alto: muchas carpetas y convenciones; más complejidad de navegación y “dónde pongo X”. |
| **Duplicación** | Poca; una capa por tipo. | Baja por feature. | Riesgo de duplicar lógica entre módulos si no se disciplina shared. |
| **Cohesión** | Por tipo técnico (todos los repos juntos). | Por dominio (todo lo de “users” junto). | Máxima por dominio y por capa dentro del dominio. |
| **Acoplamiento** | Servicios y repos compartidos; permission_service natural en domain. | Features pueden depender de otros; permission_service cruza varios. | Módulos dependen de shared; permission_service en shared evita ciclos. |

---

## 3. Recomendación

**Recomendación: Opción B (por feature/dominio), con disciplina de capas ligera.**

Motivos principales:

1. **Requisitos del proyecto**: El proyecto ya pide “presentation, application, domain, infrastructure”. Eso se cumple con **B** sin necesidad de cuatro carpetas por feature: dentro de cada feature puede haber `router.py` (presentation), `service.py` (application), `repository.py` (infrastructure), y `domain` puede ser compartido (modelos + permission_service) o un `domain/` por feature con solo políticas. No hace falta la granularidad completa de C para cumplir la documentación.

2. **Tamaño y equipo**: Con ~1100 líneas en un solo `admin/routes.py` y equipo pequeño, **C** introduce muchas carpetas y decisiones (qué va en cada módulo, qué en shared). **B** permite partir por features (users, tags, saved_filters, groups, connectors, actions, documents) y opcionalmente auth, con menos overhead mental y de estructura.

3. **permission_service**: Es cross-cutting (user, group, saved_filter, action, document). En **A** vive en domain de forma natural. En **B** puede vivir en un feature `permissions` o en un `shared/` o `core/` (un solo lugar). En **C** debe vivir en shared. **B** con un `shared/domain` (o `core/domain`) para models + permission_service es más simple que C y evita el mismo problema.

4. **Migración desde el estado actual**: Hoy hay un solo `domain/` (models + permission_service), `admin/routes.py` y `dependencies.py`. Pasar a **B** significa: (1) Crear `features/users/`, `features/tags/`, etc. (2) Mover porciones de routes + schemas a cada feature (router, service, repository, schemas). (3) Dejar `domain/` (o `shared/domain/`) con models y permission_service. (4) Mantener `dependencies.py` (get_db, auth) en raíz o en `shared/`. Es un refactor acotado. Pasar a **C** implica definir 8+ módulos, decidir si los ORM están en shared o repartidos, y multiplicar carpetas; el beneficio en un equipo de uno no compensa el coste.

5. **Opción A** sigue siendo válida si se prefiere agrupar por “tipo técnico” (todos los repos en un sitio, todos los servicios en otro). La documentación no exige “por feature”; exige capas. **A** cumple capas; **B** añade cohesión por dominio sin llegar a la complejidad de C.

**Si se quisiera acercar a C sin adoptarla por completo** (variante “B+”):

- Estructura por feature como en B.
- Dentro de cada feature: `router.py`, `schemas.py`, `service.py` (use cases), `repository.py`, y opcionalmente una carpeta `domain/` con solo políticas de ese feature (si las hay).
- Mantener un **shared** (o `core`) con: `get_db`, `CurrentUser`, `get_current_user`, `require_admin`, `permission_service`, modelos ORM y utilidades (UUID). Así se obtiene parte de la claridad de “módulos” sin la explosión de carpetas de C.

---

## 4. Riesgos y adaptaciones

### 4.1 Si se elige B (recomendado)

| Riesgo | Mitigación |
|--------|------------|
| **Rutas admin muy grandes por feature** | Partir cada feature en router + service + repository; límite de tamaño por archivo (ej. router < 200–300 líneas). |
| **permission_service acoplado a muchos modelos** | Mantenerlo en un solo lugar (shared/ o domain/); tests en test_domain_permissions.py; no duplicar lógica en features. |
| **Fugas de tenant_id** | Siempre inyectar tenant_id desde CurrentUser en servicios/repos; tests que comprueben que list/get/create no devuelven datos de otro tenant. |
| **Duplicación de helpers (UUID, etc.)** | Extraer a `shared/utils.py` o `shared/uuid_utils.py` y usar desde todos los features. |

### 4.2 Si se eligiera C

| Riesgo | Mitigación |
|--------|------------|
| **Sobreingeniería** | Reducir módulos al mínimo (p. ej. no crear módulo “tenant” si no hay CRUD; agrupar tag + saved_filter si son muy pequeños). Mantener ORM en shared. |
| **Donde vive permission_service** | Siempre en shared/domain; no intentar repartirlo por módulos. |
| **Duplicación entre módulos** | Convención clara: todo lo que usan 2+ módulos va a shared (auth, db, permission_service, models, uuid). |
| **Navegación y onboarding** | Documentar en docs/architecture.md el mapa de módulos y qué va en cada capa (domain/application/infrastructure/presentation). |

### 4.3 Para cualquier opción

- **Tenant en servidor**: No confiar en cliente; `tenant_id` solo desde JWT (CurrentUser) en todos los endpoints admin.
- **TDD**: Lógica crítica (permission_service, reglas de negocio en servicios) con tests unitarios; repos y routers con tests de integración.
- **Endpoints admin**: Todos detrás de `require_admin`; no exponer a usuarios finales.

---

## 5. Pasos de adaptación si se eligiera C

Si el orquestador decidiera implantar C a pesar de la recomendación (p. ej. por proyección de crecimiento del equipo o de dominios):

1. **Definir shared**: Crear `shared/` con `db.py`, `auth.py`, `uuid_utils.py`, `domain/permission_service.py` y un único `shared/domain/models.py` (o `shared/infrastructure/models.py`) con Base y todos los ORM. Migraciones seguirían importando Base desde ahí.
2. **Definir lista de módulos**: auth, user, tag, saved_filter, group, connector, action, document (y tenant solo si aplica).
3. **Por cada módulo**: Crear `modules/<nombre>/` con domain/, application/, infrastructure/, presentation/. En domain solo políticas o interfaces si se desea; en infrastructure, repositorios que importen modelos desde shared. En presentation, router + schemas; dependencias de auth/db desde shared.
4. **Migrar por feature**: Sacar de `admin/routes.py` un feature (p. ej. users), crear use cases en application, repos en infrastructure, router y schemas en presentation; repetir para tags, saved_filters, etc.
5. **Tests**: Mover o duplicar tests a tests/ por módulo (test_user_*.py, test_tag_*.py, …) o mantener tests de integración por endpoint en tests/api/.
6. **Documentar**: Actualizar docs/architecture.md con el árbol de Opción C y la convención “shared = cross-cutting; módulo = un agregado de dominio”.

---

## Resumen ejecutivo

- **Opción C** está bien definida como “módulos con mini Clean Architecture” y puede aplicarse a Cryptarch con `shared/` para auth, db, permission_service, modelos ORM y utilidades; y módulos user, tag, saved_filter, group, connector, action, document, auth.
- **Comparativa**: A cumple capas con poco overhead; B añade cohesión por dominio con refactor moderado; C maximiza cohesión pero con más estructura y más adecuada a equipos o dominios más grandes.
- **Recomendación**: **B (por feature)** con shared para domain (models + permission_service) y dependencias (auth, db). Si se quiere algo más parecido a C, adoptar **B+** (features + shared bien definido) sin llegar a cuatro carpetas por módulo.
- **Riesgos**: En B, controlar tamaño de archivos y fugas de tenant; en C, sobreingeniería y ubicación única de permission_service y modelos en shared.
