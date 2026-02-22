---
name: sprint-audit
description: Audit a sprint against acceptance criteria before marking it complete.
argument-hint: [sprint-id]
allowed-tools: Read, Grep, Glob, Bash
disable-model-invocation: true
---
Read the sprint doc and checklist, inspect code/tests, then report PASS/FAIL, gaps, shortcuts, and follow-up tasks.
Do not auto-mark complete.
