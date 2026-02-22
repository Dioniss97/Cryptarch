# Project memory for Claude Code

## Import project context
- @docs/project-overview.md
- @docs/architecture.md
- @docs/domain-model.md
- @docs/security-notes.md
- @docs/backlog.md
- @docs/agents.md
- @docs/sprints/sprint-checklist.md

## Working style
- Follow TDD for all critical backend logic.
- Prefer small, reviewable commits.
- Keep tenant boundaries explicit (`tenant_id` everywhere in structured entities).
- When changing domain rules, update docs first (or in the same change).

## Build order
Layer-oriented sprints:
1. foundation / monorepo / infra
2. domain + schema + migrations + repository contracts
3. auth + tenancy + admin API
4. admin UI
5. ingestion + queue + vectorizer
6. chat orchestration + RAG + action execution
7. hardening / observability / optimization

## Non-negotiable domain rules
- Tags are metadata only.
- Saved filters define selection logic (currently tag-based AND).
- Groups bind saved filters.
- Users inherit permissions via groups.
- Effective permissions are the union of all group-derived permissions.

## Chat constraints
- Normal users only see chat UI.
- Chat may use only allowed documents and allowed actions resolved server-side.

## Ingestion constraints (phase 1)
- Text-only extraction (PDF/TXT/CSV, no OCR)
- Vectorization via Redis queue + worker
- Statuses: queued, processing, indexed, error

## Connector/action constraints
- Connector stores auth/base config
- Action belongs to connector and carries route/method/request mapping
- Tags are attached to actions for permissions

## Sprint workflow

- These are custom slash commands stored in `.claude/commands/` and mirrored by project Skills for automatic discovery.
- Use `/sprint-next` to pick the next unchecked sprint
- Use `/sprint-start <sprint-id>` to load scope
- Use `/sprint-audit <sprint-id>` before marking complete
