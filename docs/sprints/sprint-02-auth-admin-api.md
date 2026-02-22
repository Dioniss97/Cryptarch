# sprint-02-auth-admin-api

## Goal
Implement local auth and admin CRUD APIs with tenant enforcement.

## In scope
- login/logout
- role checks (admin/user)
- admin CRUD for users/tags/filters/groups/connectors/actions/documents metadata
- tests for role and tenant guards

## Acceptance criteria
- non-admin blocked from admin routes
- cross-tenant access blocked
- CRUD works for core entities
