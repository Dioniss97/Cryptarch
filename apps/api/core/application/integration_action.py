"""IntegrationAction use cases.

Backward-compatible semantic layer over action use cases.
"""
from core.application import action as action_use_cases
from core.domain.models import IntegrationAction
from core.ports.action_repository import IntegrationActionRepository
from core.ports.connector_repository import IntegrationRepository
from core.ports.tag_repository import TagRepository

IntegrationActionNotFoundError = action_use_cases.ActionNotFoundError
IntegrationNotFoundError = action_use_cases.ConnectorNotFoundError
IntegrationActionTagNotFoundError = action_use_cases.TagNotFoundError


def list_integration_actions(
    tenant_id: str,
    repo: IntegrationActionRepository,
    integration_id: str | None = None,
) -> list[IntegrationAction]:
    actions = action_use_cases.list_actions(
        tenant_id=tenant_id,
        repo=repo,
        connector_id=integration_id,
    )
    return [IntegrationAction(**action.__dict__) for action in actions]


def get_integration_action(
    integration_action_id: str,
    tenant_id: str,
    repo: IntegrationActionRepository,
) -> IntegrationAction | None:
    action = action_use_cases.get_action(
        action_id=integration_action_id,
        tenant_id=tenant_id,
        repo=repo,
    )
    if action is None:
        return None
    return IntegrationAction(**action.__dict__)


def create_integration_action(
    tenant_id: str,
    integration_id: str,
    method: str,
    path: str,
    name: str | None,
    request_config: dict | None,
    tag_ids: list[str],
    repo: IntegrationActionRepository,
    integration_repo: IntegrationRepository,
    tag_repo: TagRepository,
) -> IntegrationAction:
    action = action_use_cases.create_action(
        tenant_id=tenant_id,
        connector_id=integration_id,
        method=method,
        path=path,
        name=name,
        request_config=request_config,
        tag_ids=tag_ids,
        repo=repo,
        connector_repo=integration_repo,
        tag_repo=tag_repo,
    )
    return IntegrationAction(**action.__dict__)


def update_integration_action(
    integration_action_id: str,
    tenant_id: str,
    method: str | None,
    path: str | None,
    name: str | None,
    request_config: dict | None,
    tag_ids: list[str] | None,
    repo: IntegrationActionRepository,
    tag_repo: TagRepository,
) -> IntegrationAction:
    action = action_use_cases.update_action(
        action_id=integration_action_id,
        tenant_id=tenant_id,
        method=method,
        path=path,
        name=name,
        request_config=request_config,
        tag_ids=tag_ids,
        repo=repo,
        tag_repo=tag_repo,
    )
    return IntegrationAction(**action.__dict__)


def delete_integration_action(
    integration_action_id: str,
    tenant_id: str,
    repo: IntegrationActionRepository,
) -> None:
    action_use_cases.delete_action(
        action_id=integration_action_id,
        tenant_id=tenant_id,
        repo=repo,
    )
