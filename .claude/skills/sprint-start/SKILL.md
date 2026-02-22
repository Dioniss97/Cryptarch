---
name: sprint-start
description: Load a sprint spec and produce a concrete execution plan with TDD checkpoints.
argument-hint: [sprint-id]
allowed-tools: Read, Grep, Glob
disable-model-invocation: true
---
Load sprint `$0` from `docs/sprints/` and output: objective, in/out of scope, TDD order, implementation order, definition of done, docs to update.
