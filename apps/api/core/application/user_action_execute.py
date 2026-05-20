"""
Execute an action on behalf of an end user (stub): permissions, tenant scope, payload validation.
"""

import uuid
from dataclasses import dataclass
from typing import Any

from core.domain import permission_service
from core.domain.input_schema_contract import validate_action_payload
from core.ports.action_repository import ActionRepository
from core.ports.permission_query import PermissionQueryPort


class ActionNotFoundError(Exception):
    """Action does not exist or is outside the tenant."""


class ActionNotPermittedError(Exception):
    """User lacks effective permission to execute this action."""


def _canonical_key(value: str) -> str | None:
    v = value.strip()
    try:
        if len(v) == 32 and "-" not in v:
            return str(uuid.UUID(hex=v))
        return str(uuid.UUID(v))
    except (ValueError, TypeError):
        return None


@dataclass(frozen=True)
class ExecuteActionResult:
    status: str
    message: str
    action_id: str
    received_payload: dict[str, Any]


def execute_action_for_user(
    tenant_id: str,
    user_id: str,
    action_id: str,
    payload: dict[str, Any],
    permission_port: PermissionQueryPort,
    action_repo: ActionRepository,
) -> ExecuteActionResult:
    action_key = _canonical_key(action_id)
    if not action_key:
        raise ActionNotFoundError(action_id)

    action = action_repo.get_by_id(action_id, tenant_id)
    if action is None or not action.id:
        raise ActionNotFoundError(action_id)

    allowed_ids = permission_service.resolve_effective_action_ids(
        permission_port, tenant_id, user_id
    )
    allowed_keys = {
        k for aid in allowed_ids if (k := _canonical_key(aid)) is not None
    }
    resolved_key = _canonical_key(action.id)
    if resolved_key is None or resolved_key not in allowed_keys:
        raise ActionNotPermittedError(action_id)

    validated = validate_action_payload(payload, action.input_schema_json)

    return ExecuteActionResult(
        status="ok",
        message="Action execution accepted (stub; connector call not implemented)",
        action_id=action.id,
        received_payload=validated,
    )
