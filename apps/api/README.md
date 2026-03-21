# apps/api

Backend en FastAPI. **Arquitectura: Hexagonal (Ports & Adapters).**

---

## Estructura principal

| Capa | Ruta | Responsabilidad |
| --- | --- | --- |
| Core | `core/` | Domain (entidades, domain services), application (casos de uso) y ports (interfaces de repositorios). |
| Adapters driving | `adapters/driving/` | HTTP (routers de FastAPI + schemas de Pydantic). |
| Adapters driven | `adapters/driven/` | Persistencia (implementaciones de ports, SQLAlchemy/Postgres). |

---

## Contrato compartido (`shared_contract.py`)

Al arrancar, la API lee **`packages/shared/data/domain.json`** (raíz del monorepo respecto a `apps/api`). De ahí salen constantes y enums (`UserRole`, `DocumentStatus`, `SavedFilterTarget`, etc.) usados en schemas y guards. **No hace falta Node** en la imagen Python; si despliegas solo `apps/api` sin el monorepo, falta el JSON y la importación fallará.

## Notas de diseño

- Toda la API es tenant-scoped.
- Auth y tenant se resuelven en dependencies y se pasan al core.
- TDD para lógica crítica.

## Desarrollo local (formato / lint)

- En la raíz del monorepo, `pyproject.toml` define **Ruff** para `apps/api` y el worker.
- Opcional: `pip install -r requirements-dev.txt` (incluye Ruff acotado) y desde la raíz del repo ejecutar `ruff format apps/api` y `ruff check apps/api`.

---

## Siguiente lectura

- Detalle y estructura de carpetas: [docs/architecture/api-architecture-decision.md](../../docs/architecture/api-architecture-decision.md).
