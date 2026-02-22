# Architecture

## Components
1. React web app (admin + user chat)
2. FastAPI API
3. Postgres (structured data)
4. Redis (queue)
5. Worker (vectorization)
6. Qdrant (vectors)

## Upload flow
1. Admin uploads document
2. API creates metadata and status `queued`
3. API enqueues Redis job
4. Worker sets `processing`
5. Worker extracts/chunks/embeds/indexes to Qdrant
6. Worker sets `indexed` or `error`
7. Admin UI shows status badge

## Chat flow
1. User sends message
2. API resolves tenant + effective permissions
3. API constrains RAG documents and allowed actions
4. API orchestrates response
