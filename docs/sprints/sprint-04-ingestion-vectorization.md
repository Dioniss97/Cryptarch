# sprint-04-ingestion-vectorization

## Goal
Implement uploads, async vectorization, and status tracking.

## In scope
- upload endpoint (single file)
- Redis enqueue
- worker processing
- extraction for PDF/TXT/CSV (no OCR)
- chunking + embeddings + Qdrant upsert
- status transitions and error messages

## Acceptance criteria
- upload queues jobs
- worker updates `queued/processing/indexed/error`
- indexed data lands in Qdrant with tenant metadata
