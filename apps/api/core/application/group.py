"""
Group use cases. Orchestrate GroupRepository; no direct DB access.

Validation: Saved filter ids (user_filter_ids, action_filter_ids, document_filter_ids) must exist
and belong to the tenant. This validation is performed in the **driven** layer (group_repository):
add() and save() raise FilterNotFoundInTenantError if any filter id is missing or not in tenant.
The driving layer (routes) maps that exception to 404.
"""
from __future__ import annotations

from core.domain.models import Group
from core.ports.group_repository import GroupRepository


def list_groups(tenant_id: str, repo: GroupRepository) -> list[Group]:
    """List all groups for the tenant."""
    return repo.list_by_tenant(tenant_id)


def get_group(group_id: str, tenant_id: str, repo: GroupRepository) -> Group | None:
    """Return group if it exists and belongs to tenant; else None."""
    return repo.get_by_id(group_id, tenant_id)


def create_group(
    tenant_id: str,
    name: str,
    user_filter_ids: list[str],
    action_filter_ids: list[str],
    document_filter_ids: list[str],
    repo: GroupRepository,
) -> Group:
    """
    Create a group with the given filter bindings.
    Filter ids must be canonical UUID strings. The repository validates that each
    saved filter exists and belongs to the tenant; it raises FilterNotFoundInTenantError
    if not (driving layer maps to 404).
    """
    group = Group(tenant_id=tenant_id, name=name)
    return repo.add(
        group,
        user_filter_ids=user_filter_ids,
        action_filter_ids=action_filter_ids,
        document_filter_ids=document_filter_ids,
    )


def update_group(
    group_id: str,
    tenant_id: str,
    repo: GroupRepository,
    name: str | None = None,
    user_filter_ids: list[str] | None = None,
    action_filter_ids: list[str] | None = None,
    document_filter_ids: list[str] | None = None,
) -> Group | None:
    """
    Update group name and/or filter lists. Returns None if group not found.
    If filter id lists are provided, the repository validates they exist and belong
    to the tenant (raises FilterNotFoundInTenantError otherwise).
    """
    group = repo.get_by_id(group_id, tenant_id)
    if not group:
        return None
    if name is not None:
        group.name = name
    return repo.save(
        group,
        user_filter_ids=user_filter_ids,
        action_filter_ids=action_filter_ids,
        document_filter_ids=document_filter_ids,
    )


def delete_group(group_id: str, tenant_id: str, repo: GroupRepository) -> bool:
    """Delete the group if it exists and belongs to tenant. Returns True if deleted, False if not found."""
    group = repo.get_by_id(group_id, tenant_id)
    if not group:
        return False
    repo.delete(group)
    return True
