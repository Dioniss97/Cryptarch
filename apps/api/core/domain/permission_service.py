"""
Resolve effective permissions via port: groups whose user-filters match the user,
then union of actions and documents from those groups' filters.
Tenant-scoped; tag AND semantics within each saved filter.
The core delegates to PermissionQueryPort; the implementation lives in driven adapters.
"""
from core.ports.permission_query import PermissionQueryPort


def resolve_effective_action_ids(
    port: PermissionQueryPort, tenant_id: str, user_id: str
) -> set[str]:
    """Effective allowed action IDs for the user (tenant-scoped, union of groups)."""
    return port.resolve_effective_action_ids(tenant_id, user_id)


def resolve_effective_document_ids(
    port: PermissionQueryPort, tenant_id: str, user_id: str
) -> set[str]:
    """Effective visible document IDs for the user (tenant-scoped, union of groups)."""
    return port.resolve_effective_document_ids(tenant_id, user_id)
