"""
List actions visible to an end user from effective permissions (groups + filters).
"""

from dataclasses import dataclass
from typing import Any

from core.domain import permission_service
from core.ports.action_repository import ActionRepository
from core.ports.permission_query import PermissionQueryPort


@dataclass(frozen=True)
class PermittedActionSummary:
    """Action fields safe to expose to non-admin API consumers."""

    id: str
    name: str | None
    connector_id: str
    input_schema_json: Any | None
    input_schema_version: str | None
    tag_ids: list[str]


def list_permitted_actions_for_user(
    tenant_id: str,
    user_id: str,
    permission_port: PermissionQueryPort,
    action_repo: ActionRepository,
) -> list[PermittedActionSummary]:
    allowed_ids = permission_service.resolve_effective_action_ids(
        permission_port, tenant_id, user_id
    )
    summaries: list[PermittedActionSummary] = []
    for aid in sorted(allowed_ids, key=lambda x: str(x).lower()):
        action = action_repo.get_by_id(aid, tenant_id)
        if action is None:
            continue
        tag_ids = action_repo.get_action_tag_ids(aid)
        summaries.append(
            PermittedActionSummary(
                id=action.id or aid,
                name=action.name,
                connector_id=action.connector_id,
                input_schema_json=action.input_schema_json,
                input_schema_version=action.input_schema_version,
                tag_ids=tag_ids,
            )
        )
    return summaries
