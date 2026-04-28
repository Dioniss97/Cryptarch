"""
List actions visible to an end user from effective permissions (groups + filters).
"""

import uuid
from dataclasses import dataclass
from typing import Any

from core.domain import permission_service
from core.domain.models import Action
from core.ports.action_repository import ActionRepository
from core.ports.permission_query import PermissionQueryPort


def _canonical_key(value: str) -> str | None:
    v = value.strip()
    try:
        if len(v) == 32 and "-" not in v:
            return str(uuid.UUID(hex=v))
        return str(uuid.UUID(v))
    except (ValueError, TypeError):
        return None


@dataclass(frozen=True)
class PermittedActionSummary:
    """Action fields safe to expose to non-admin API consumers."""

    id: str
    name: str | None
    connector_id: str
    method: str
    path: str
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
    actions = action_repo.list_by_ids(list(allowed_ids), tenant_id)
    action_by_canonical: dict[str, Action] = {}
    for a in actions:
        k = _canonical_key(a.id) if a.id else None
        if k:
            action_by_canonical[k] = a
    tag_map = action_repo.list_action_tag_ids_for_actions(
        [a.id for a in actions if a.id]
    )
    summaries: list[PermittedActionSummary] = []
    for aid in sorted(allowed_ids, key=lambda x: str(x).lower()):
        key = _canonical_key(aid)
        if not key:
            continue
        action = action_by_canonical.get(key)
        if action is None:
            continue
        tag_ids = tag_map.get(key, [])
        summaries.append(
            PermittedActionSummary(
                id=action.id or aid,
                name=action.name,
                connector_id=action.connector_id,
                method=action.method,
                path=action.path,
                input_schema_json=action.input_schema_json,
                input_schema_version=action.input_schema_version,
                tag_ids=tag_ids,
            )
        )
    return summaries
