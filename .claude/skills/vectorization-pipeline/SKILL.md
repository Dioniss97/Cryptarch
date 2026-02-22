---
name: vectorization-pipeline
description: Implement or review document queue + worker pipeline (Redis, extraction, chunking, embeddings, Qdrant, status updates).
allowed-tools: Read, Grep, Glob, Bash
context: fork
agent: vector-pipeline-worker
---
Work on upload queue/worker state transitions, extraction, chunking, embeddings, Qdrant upserts, and admin-visible errors. Keep jobs retry-safe.
