# Project Overview

## Product intent
A multi-tenant internal AI assistant platform for companies.

## Roles
- Admin: manages users, tags, filters, groups, connectors, actions, documents
- User: only sees chat

## Scope assumptions (phase 1)
- Multi-tenant from day 1 (`tenant_id` row isolation)
- Local auth first (no SSO)
- Text documents only (no OCR)
- Embeddings local
- Queue + worker included early

## Stack
- React
- FastAPI
- Postgres
- Qdrant
- Redis
