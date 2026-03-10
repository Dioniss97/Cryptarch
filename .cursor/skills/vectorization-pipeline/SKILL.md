---
name: vectorization-pipeline
description: Implementar o revisar el pipeline de cola + worker (Redis, extracción, chunking, embeddings, Qdrant, actualización de estado). Usar al trabajar en ingestión de documentos o worker.
---

# Pipeline de vectorización

Trabajar en transiciones de estado de la cola/worker, extracción, chunking, embeddings, upserts a Qdrant y errores visibles para admin. Mantener jobs retry-safe e idempotentes.
