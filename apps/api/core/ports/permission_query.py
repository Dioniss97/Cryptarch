"""Port for resolving effective permissions (actions/documents allowed for a user)."""
from typing import Protocol


class PermissionQueryPort(Protocol):
    """Resolves allowed action and document IDs for a user in a tenant."""

    def resolve_effective_action_ids(self, tenant_id: str, user_id: str) -> set[str]:
        ...

    def resolve_effective_document_ids(self, tenant_id: str, user_id: str) -> set[str]:
        ...
