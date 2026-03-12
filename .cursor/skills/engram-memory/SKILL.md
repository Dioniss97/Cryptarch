---
name: engram-memory
description: Persistent project memory using Engram. Use when starting a task, digesting docs, storing discoveries, or when the user mentions memory, tasks, docs, or knowledge.
---

# Engram memory

This skill manages persistent project knowledge using Engram (MCP tools: `mem_save`, `mem_search`, `mem_context`, `mem_get_observation`, `mem_timeline`, `mem_session_summary`, etc.).

## Memory structure (casi todo vive aquí)

| Family | Purpose |
|--------|---------|
| **sprints/** | One memory per sprint: goal, scope, acceptance criteria, task list, **Status**. Source of truth for sprint state. |
| **tasks/** | One memory per task: description, scope, **Status**. Source of truth for "what to do next" and outcome. |
| **docs/** | Architecture summaries and technical documentation. |
| **knowledge/** | Reusable discoveries: debugging findings, patterns, conventions, gotchas. |

Consult Engram first for sprint/task state; markdown files are for bootstrap or human reference only.

## Workflow

### 1. Retrieve memory

Before starting work, search Engram for relevant `sprints/*`, `tasks/*`, `docs/*`, and `knowledge/*`:

- `mem_search` with 2–5 keywords (component + intent).
- If a result is relevant: `mem_timeline(observation_id=...)` for context, then `mem_get_observation(id=...)` for full content.
- Do not dump large blocks; summarize and cite observation IDs.

### 2. Task initialization

When a new task (e.g. Jira ID or task-XX) appears:

- Create or update memory with `topic_key`: `tasks/<task_id>`.
- Store: task goal, expected scope, suspected files; include **Status: pending** in content.
- Use `mem_save` with `topic_key` so later updates upsert the same memory.

When **starting a sprint**: ensure all tasks for that sprint exist in Engram (see `docs/sprints/tasks.md` and `.cursor/skills/sprint-start/SKILL.md`). Create each `tasks/task-XX` for the sprint with Status: pending if not already present. Optionally create/update `sprints/sprint-XX`. The sprint’s checklist is then the set of these task memories.

### 3. Discoveries

If reusable technical knowledge appears (pattern, gotcha, fix):

- Store with `topic_key`: `knowledge/<topic>`.
- Format: What / Why / Where / Learned; keep concise.

### 4. Task completion

Update `tasks/<task_id>` with:

- **What**: What was implemented.
- **Why**: Reason for the change.
- **Where**: Files or modules affected.
- **Learned**: Risks, gotchas, or follow-ups.
- **Status**: Set to `done` only when tests pass, code is committed and a PR is opened (human reviews PRs on GitHub).

### 5. Task and sprint status (autonomous workflow)

Every task and sprint memory must include in its **content** a line:

`Status: pending | in_progress | blocked | done`

- **pending**: not started.
- **in_progress**: being worked on.
- **blocked**: blocked (note reason in content).
- **done**: tests + commit + PR; human only reviews PRs.

**When to update status:** Start task → `Status: in_progress`. Blocked → `Status: blocked`. Tests + commit + PR → `Status: done`; optionally update `sprints/sprint-XX` (e.g. `sprints/sprint-02`) with the same status convention.

**How to find work:** Use `mem_search` with phrases like: "Status: pending", "Status: in_progress", "tasks pending", "sprint blocked", "sprints sprint-02". No separate checklist type — status is inside the same observation content for `tasks/<id>` and `sprints/sprint-XX`.

## Guidelines

- Prefer updating existing memories (same `topic_key`) over creating duplicates.
- Keep entries concise; avoid trivial or narrative content.
- Sprints and tasks live in Engram (`sprints/sprint-XX`, `tasks/task-XX`); use them as the source of truth. Markdown is reference or seed only.
- After context reset or compaction, call `mem_context` to recover state.
