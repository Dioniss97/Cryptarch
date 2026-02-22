# sprint-01-domain-db

## Goal
Model the core relational domain and prove permissions semantics.

## In scope
- Postgres migrations for tenants/users/tags/connectors/actions/documents/saved_filters/groups
- join tables for tags and bindings
- repositories + domain services
- tests for tag AND + permission unions + tenant isolation

## Acceptance criteria
- migrations apply cleanly
- domain tests pass
- indexes exist for tenant-heavy joins
