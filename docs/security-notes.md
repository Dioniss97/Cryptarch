# Security Notes

## Phase-1 accepted tradeoffs
- Local auth instead of SSO
- Admin can view connector credentials in UI (temporary)
- Broad connector/action configurability for speed

## Still required now
- Never log secrets
- Enforce tenant checks server-side
- Keep connector credentials separate from action definitions
- Keep admin endpoints inaccessible to normal users

## Future hardening
- Outbound host allow-list for connectors
- Encryption at rest for connector secrets
- Action execution audit logs
- Rate limiting
- SSO
