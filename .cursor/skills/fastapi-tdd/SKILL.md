---
name: fastapi-tdd
description: Implementar features de backend en FastAPI con flujo test-first estricto y capas claras. Usar al diseñar o implementar endpoints, dominio o repositorios.
---

# FastAPI TDD

Implementar trabajo de backend con TDD: contratos primero, tests en rojo, código mínimo, refactor, verificar límites de tenant y permisos.

- Escribir tests que definan el contrato antes de la implementación.
- Capas: presentation → application → domain → infrastructure.
- No saltar tests en lógica crítica ni en fronteras de tenancy.
