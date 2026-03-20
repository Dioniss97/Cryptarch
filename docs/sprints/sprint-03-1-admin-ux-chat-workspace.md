# sprint-03-1-admin-ux-chat-workspace

## Goal
Rework admin/chat UX so the product feels guided, compact, and usable for non-technical admins.

## In scope
- compact admin/workspace shell with clean topbar and profile menu
- connectors as containers of actions (single integrated flow)
- guided HTTP integration builder (auth modes, content type, headers/query/body)
- adaptive action form behavior by HTTP method/content type
- tag create/reuse from users/actions/documents forms
- users view with integrated CRUD + table + filters + save filter
- chat as real assistant workspace (no `action_id` input, no manual schema load)
- preferences moved to profile menu and UX polish/microcopy

## Acceptance criteria
- no main UX flow requires manual technical IDs
- no main UX flow requires raw JSON editing
- connectors/actions feel unified and editable in context
- users can create/apply/save filters from the same user-management experience
- chat no longer exposes QA/developer controls and supports dynamic action prompts naturally
