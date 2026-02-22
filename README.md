# Claude Code Project Context Pack

This repository is a **context-first scaffold** for Claude Code (CLI) to help build a multi-tenant RAG + Actions platform using **FastAPI + React + Postgres + Qdrant + Redis workers**.

It intentionally focuses on:
- project memory (`.claude/CLAUDE.md`)
- reusable skills (slash commands)
- subagents
- sprint docs
- architecture/domain rules

It does **not** include full application code yet. The goal is to let Claude Code generate code consistently from a strong project contract.

## Project objective

Build a multi-tenant SaaS where:
- **Admins** manage users, groups, tags, filters, connectors, actions, and documents.
- **Normal users** only see a **chat UI**.
- The chat can:
  - query only the documents allowed for the user's groups (RAG scope)
  - execute only the actions allowed for the user's groups (connector/action scope)

## Core authorization model (important)

Permissions are not stored directly on tags.

Instead:
1. Entities carry **tags** (`users`, `actions`, `documents`)
2. Admins create **saved filters** using tag AND logic
3. Groups bind to those saved filters:
   - one or more user filters
   - one or more action filters
   - one or more document filters
4. Effective permissions for a user = union of the permissions from all groups the user belongs to

## Recommended first use with Claude Code

1. Open this repo in terminal.
2. Start Claude Code.
3. Run `/memory` and verify `.claude/CLAUDE.md` is loaded.
4. Run `/agents` and inspect project subagents.
5. Run `/sprint-next` to pick the next sprint.
6. Run `/sprint-start sprint-00-foundation` to begin implementation.
