"""
Action use cases. Orchestrate ActionRepository, ConnectorRepository, TagRepository.
Validate connector_id and tag_ids in tenant. No Session or DB in this module; ports are injected.
"""
from core.domain.models import Action
from core.ports.action_repository import ActionRepository
from core.ports.connector_repository import ConnectorRepository
from core.ports.tag_repository import TagRepository


class ActionNotFoundError(Exception):
    """Raised when an action does not exist or does not belong to the tenant."""


class ConnectorNotFoundError(Exception):
    """Raised when connector_id does not exist or does not belong to the tenant."""


class TagNotFoundError(Exception):
    """Raised when one or more tag_ids do not exist or do not belong to the tenant."""


def _validate_tag_ids_in_tenant(
    tag_ids: list[str],
    tenant_id: str,
    tag_repo: TagRepository,
) -> None:
    """Raise TagNotFoundError if any tag_id is not found or not in tenant."""
    for tag_id in tag_ids:
        tag = tag_repo.get_by_id(tag_id, tenant_id)
        if not tag:
            raise TagNotFoundError("Tag not found")


def list_actions(
    tenant_id: str,
    repo: ActionRepository,
    connector_id: str | None = None,
) -> list[Action]:
    """List actions for the tenant. Optionally filter by connector_id (must be tenant's connector)."""
    return repo.list_by_tenant(tenant_id, connector_id)


def get_action(
    action_id: str,
    tenant_id: str,
    repo: ActionRepository,
) -> Action | None:
    """Get action by id; None if not found or not in tenant."""
    return repo.get_by_id(action_id, tenant_id)


def create_action(
    tenant_id: str,
    connector_id: str,
    method: str,
    path: str,
    name: str | None,
    request_config: dict | None,
    tag_ids: list[str],
    repo: ActionRepository,
    connector_repo: ConnectorRepository,
    tag_repo: TagRepository,
) -> Action:
    """Create action. Raises ConnectorNotFoundError or TagNotFoundError if validation fails."""
    connector = connector_repo.get_by_id(connector_id, tenant_id)
    if not connector:
        raise ConnectorNotFoundError("Connector not found")
    _validate_tag_ids_in_tenant(tag_ids, tenant_id, tag_repo)
    action = Action(
        tenant_id=tenant_id,
        connector_id=connector.id,
        method=method,
        path=path,
        name=name,
        request_config=request_config,
    )
    return repo.add(action, tag_ids)


def update_action(
    action_id: str,
    tenant_id: str,
    method: str | None,
    path: str | None,
    name: str | None,
    request_config: dict | None,
    tag_ids: list[str] | None,
    repo: ActionRepository,
    tag_repo: TagRepository,
) -> Action:
    """Update action. Raises ActionNotFoundError if not found; TagNotFoundError if tag_ids invalid."""
    action = repo.get_by_id(action_id, tenant_id)
    if not action:
        raise ActionNotFoundError("Action not found")
    if tag_ids is not None:
        _validate_tag_ids_in_tenant(tag_ids, tenant_id, tag_repo)
    if method is not None:
        action.method = method
    if path is not None:
        action.path = path
    if name is not None:
        action.name = name
    if request_config is not None:
        action.request_config = request_config
    return repo.save(action, tag_ids)


def delete_action(
    action_id: str,
    tenant_id: str,
    repo: ActionRepository,
) -> None:
    """Delete action. Raises ActionNotFoundError if not found."""
    action = repo.get_by_id(action_id, tenant_id)
    if not action:
        raise ActionNotFoundError("Action not found")
    repo.delete(action)
