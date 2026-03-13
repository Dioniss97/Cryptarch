# sprint-02-5-backend-bridge

## Goal
Deliver backend contracts required by frontend for dynamic action forms, user preferences, and safe action execution (stub mode).

## In scope
- integration/integration-action transitional semantics over connector/action
- action input schema V1 stored per action (`input_schema_json`, `input_schema_version`)
- backend schema validator (types, required fields, i18n labels, regex compilation)
- backend payload validator at execution time
- user preferences persistence (`language`, `theme`, `table_density`, `metadata`)
- user endpoints:
  - `GET /me/preferences`
  - `PATCH /me/preferences`
  - `GET /actions/{action_id}/input-schema`
  - `POST /actions/{action_id}/execute`
- execute flow is synchronous and stub/mock (no queue in this sprint)

## Out of scope
- real external integration execution
- async queues/retries orchestration
- advanced schema DSL (conditional logic, nested arrays/objects builders)

## Acceptance criteria
- admin can create/update actions with valid input schema V1
- invalid schema is rejected by backend (`422`)
- runtime execute validates payload server-side and returns structured errors (`422`)
- execute endpoint returns stable stub success response (`200`) for valid payload
- endpoints respect tenant boundaries and effective permission checks
- user preferences are persisted per authenticated user and can be read/updated
- backend test suite passes including new tests for schema, runtime execute, and preferences
