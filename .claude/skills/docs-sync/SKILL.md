---
name: docs-sync
description: Sync architecture/domain/sprint docs after implementation changes so Claude memory stays accurate.
allowed-tools: Read, Grep, Glob, Edit, Write
disable-model-invocation: true
---
Update docs to match code changes. Prefer small factual edits and record decisions clearly.
