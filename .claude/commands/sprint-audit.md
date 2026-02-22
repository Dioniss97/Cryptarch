---
description: Audit a sprint against its acceptance criteria and report what is complete, missing, or broken.
---

# Sprint Audit

Audit sprint completion before marking it done.

## Inputs
- Sprint id or filename: `{arg1}`

## Instructions
1. Open the sprint file in `docs/sprints/`.
2. Extract acceptance criteria / checklist items.
3. Inspect relevant code, tests, docs, and config changed for this sprint.
4. Produce a strict audit:
   - complete
   - partially complete
   - missing
   - risky / needs refactor
5. Verify tests exist for backend-critical behavior.
6. Recommend exact next fixes before marking the sprint as done.
7. Do not mark the sprint complete automatically unless explicitly asked.
