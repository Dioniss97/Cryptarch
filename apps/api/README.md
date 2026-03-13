# apps/api

FastAPI backend. **Arquitectura: Hexagonal (Ports & Adapters).**

- **Core**: `core/` — domain (entidades, domain services), application (casos de uso), ports (interfaces de repositorios).
- **Adapters driving**: `adapters/driving/` — HTTP (FastAPI routers + Pydantic schemas).
- **Adapters driven**: `adapters/driven/` — persistencia (implementaciones de los ports, SQLAlchemy/Postgres).

Toda la API es tenant-scoped; auth y tenant se resuelven en dependencies y se pasan al core. TDD para lógica crítica.

Detalle y estructura de carpetas: [docs/architecture/api-architecture-decision.md](../../docs/architecture/api-architecture-decision.md).
