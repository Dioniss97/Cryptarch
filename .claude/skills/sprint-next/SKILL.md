---
name: sprint-next
description: Find the next unchecked sprint in docs/sprints/sprint-checklist.md and summarize what should be done next.
allowed-tools: Read, Grep, Glob
disable-model-invocation: true
---
Read `docs/sprints/sprint-checklist.md` and identify the next unchecked sprint.
Return: sprint id/title, sprint file path, 5-bullet goal summary, top dependencies, and recommended subagent.
