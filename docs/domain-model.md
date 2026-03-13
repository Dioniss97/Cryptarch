# Domain Model

## Core rule
Tags are metadata only. Permissions come from saved filters and group bindings.

## Entities
- Tag (flat labels in phase 1)
- SavedFilter (target: user/action/document, tag AND logic)
- Group (binds user/action/document saved filters)
- User (role: admin or user; tagged; tenant-scoped)
- Connector (base URL + auth config; transitional semantic alias: Integration)
- Action (belongs to connector; method/path/request config; tagged; transitional semantic alias: IntegrationAction)
  - Input schema V1 per action: `input_schema_json` + `input_schema_version`
  - Dynamic field subset V1: `text`, `textarea`, `number`, `boolean`, `select`, `radio`, `date`
  - Backend validates schema definition and runtime payload (required/type/options/regex)
- Document (tenant file metadata; tagged; indexing status)
- UserPreference (per authenticated user): `language`, `theme`, `table_density`, optional `metadata`

## Effective permissions
1. Find groups whose user filters match the user
2. Union actions from those groups' action filters
3. Union documents from those groups' document filters

## Multi-tenant rule
Every structured entity is tenant-scoped (`tenant_id`), and tenant filters are applied before permission filters.

## Runtime action flow (V1)
1. Frontend requests schema: `GET /actions/{action_id}/input-schema`
2. Frontend renders dynamic form from stored schema
3. Frontend submits payload: `POST /actions/{action_id}/execute`
4. Backend re-validates payload and executes in stub/mock synchronous mode
5. Backend (not frontend) is the source of truth for validation and execution

## Future optimization
If joins get expensive, add precomputed permission tables recalculated on admin changes.
