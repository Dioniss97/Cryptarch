---
description: Start a sprint by loading its scope, acceptance criteria, and first implementation steps.
---

# Sprint Start

You are starting a sprint.

## Inputs
- Sprint id or filename: `{arg1}`

## Instructions
1. Open `docs/sprints/{arg1}.md` if `{arg1}` is a filename.
2. If `{arg1}` is a short id like `sprint-00`, resolve the matching file in `docs/sprints/`.
3. Summarize:
   - objective
   - scope boundaries
   - acceptance criteria
   - dependencies
4. Propose the first 5 tasks in TDD-friendly order.
5. Start with Task 1 only unless the user asks for more.
6. Do not skip tests for backend-critical behavior.
7. If the sprint file is missing, ask to create it and suggest a skeleton.
