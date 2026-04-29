---
name: engram-memory
description: Persistent operational memory using Engram. Use when starting Jira tasks, digesting technical docs, storing agent discoveries, or when the user mentions memory, sessions, decisions, gotchas, or knowledge.
---

# Engram memory

This skill manages persistent project knowledge using Engram (MCP tools: `mem_save`, `mem_search`, `mem_context`, `mem_get_observation`, `mem_timeline`, `mem_session_summary`, etc.).

## Source-of-truth boundaries

- **Confluence**: futura zona cero no técnica: visión, producto, dominio, MVP, flujos y decisiones de negocio.
- **Jira (`CRYPT`)**: backlog y ejecución: épicas, historias, tareas, bugs, sprints, estados, prioridades y trabajo para agentes.
- **Engram**: memoria operativa de agentes: decisiones, convenciones, IDs, sesiones, gotchas y resúmenes de ejecución.
- **GitHub**: código, ramas, PRs, reviews y CI. No backlog de producto.

## Memory structure

| Family | Purpose |
|--------|---------|
| **sprints/** | Optional operational summaries of Jira sprints. Jira owns sprint state. |
| **tasks/** | One memory per Jira issue (`tasks/CRYPT-123`): execution context, findings and outcome. Jira owns backlog/status. |
| **docs/** | Technical documentation digests. Confluence owns product/domain truth when available. |
| **knowledge/** | Reusable discoveries: debugging findings, patterns, conventions, gotchas. |

Consult Jira first for backlog/sprint state. Consult Engram for operational context, previous decisions and gotchas.

## Workflow

### 1. Retrieve memory

Before starting work, read the Jira issue (`CRYPT-*`) and search Engram for relevant `sprints/*`, `tasks/*`, `docs/*`, and `knowledge/*`:

- `mem_search` with 2–5 keywords (component + intent).
- If a result is relevant: `mem_timeline(observation_id=...)` for context, then `mem_get_observation(id=...)` for full content.
- Do not dump large blocks; summarize and cite observation IDs.

### 2. Task initialization

When a new Jira task appears:

- Create or update memory with `topic_key`: `tasks/<jira_key>` (e.g. `tasks/CRYPT-9`).
- Store: Jira key, task goal, expected scope, suspected files, useful links and operational status.
- Use `mem_save` with `topic_key` so later updates upsert the same memory.

When **starting a sprint**: read Jira sprint membership first. Optionally create/update a concise Engram `sprints/<jira-sprint>` summary with links to `CRYPT-*` issues and execution notes. Do not use old sprint markdown as source of truth.

### 3. Discoveries

If reusable technical knowledge appears (pattern, gotcha, fix):

- Store with `topic_key`: `knowledge/<topic>`.
- Format: What / Why / Where / Learned; keep concise.

### 4. Task completion

Update `tasks/<jira_key>` with:

- **What**: What was implemented.
- **Why**: Reason for the change.
- **Where**: Files or modules affected.
- **Learned**: Risks, gotchas, or follow-ups.
- **Status**: Mirror the operational outcome after tests/PR/CI. Jira remains the workflow source of truth.

### 5. Task and sprint status (autonomous workflow)

Every task and sprint memory must include in its **content** a line:

`Status: pending | in_progress | blocked | done`

- **pending**: not started.
- **in_progress**: being worked on.
- **blocked**: blocked (note reason in content).
- **done**: tests + commit + PR + **CI checks relevantes verdes** en GitHub (o merge tras verde); human only reviews PRs.
- **blocked**: CI, permisos o decisión humana impiden cerrar; documentar motivo.

**When to update status:** Start task → `Status: in_progress`. Blocked → `Status: blocked`. Tests + commit + PR + **CI verde** (vía flujo orquestador + `ci-triage`) → `Status: done`; optionally update `sprints/sprint-XX` (e.g. `sprints/sprint-02`) with the same status convention.

**How to find work:** query Jira for `Ready for Agent`, `refinamiento`, sprint membership and priorities. Use Engram search to recover context for a known `CRYPT-*` task or previous decision.

## Guidelines

- Prefer updating existing memories (same `topic_key`) over creating duplicates.
- Keep entries concise; avoid trivial or narrative content.
- Jira owns sprints/tasks/status. Engram mirrors only useful operational context for agents.
- After context reset or compaction, call `mem_context` to recover state.
