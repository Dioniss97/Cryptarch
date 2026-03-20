# sprint-05-chat-rag-actions

## Goal
Deliver production chat orchestration with permission-scoped RAG and real action execution.

## In scope
- chat orchestration and API contract for user conversations
- chat API
- effective permission resolution at request time
- RAG constrained to allowed docs
- action execution constrained to allowed actions

## Acceptance criteria
- normal users only see chat
- unauthorized docs/actions are blocked in tests
- at least one end-to-end action and one RAG path work
- UX shell/foundation is reused from Sprint 03.1 without exposing technical controls
