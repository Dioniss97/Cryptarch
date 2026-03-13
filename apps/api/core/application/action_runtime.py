"""Read action schema and execute action with payload validation."""
import uuid
from typing import Any

from core.domain.input_schema import PayloadValidationError, validate_payload_against_schema
from core.ports.action_repository import ActionRepository
from core.ports.permission_query import PermissionQueryPort


class ActionForbiddenError(Exception):
    """Raised when action exists but user cannot access it."""


class ActionNotFoundError(Exception):
    """Raised when action is not found in tenant."""


def get_action_input_schema(
    action_id: str,
    tenant_id: str,
    user_id: str,
    action_repo: ActionRepository,
    permission_query: PermissionQueryPort,
) -> dict[str, Any]:
    action = action_repo.get_by_id(action_id, tenant_id)
    if action is None:
        raise ActionNotFoundError("Action not found")
    allowed_action_ids = permission_query.resolve_effective_action_ids(tenant_id, user_id)
    if _to_hex(action.id) not in allowed_action_ids:
        raise ActionForbiddenError("Action not allowed")
    return {
        "action_id": action.id,
        "input_schema_version": action.input_schema_version or 1,
        "input_schema_json": action.input_schema_json,
    }


def execute_action(
    action_id: str,
    tenant_id: str,
    user_id: str,
    payload: dict[str, Any] | None,
    action_repo: ActionRepository,
    permission_query: PermissionQueryPort,
) -> dict[str, Any]:
    action = action_repo.get_by_id(action_id, tenant_id)
    if action is None:
        raise ActionNotFoundError("Action not found")

    allowed_action_ids = permission_query.resolve_effective_action_ids(tenant_id, user_id)
    if _to_hex(action.id) not in allowed_action_ids:
        raise ActionForbiddenError("Action not allowed")

    validate_payload_against_schema(action.input_schema_json, payload or {})
    return {
        "ok": True,
        "action_id": action.id,
        "result": {
            "mode": "stub-sync",
            "message": "Action executed in stub mode",
            "action": {
                "name": action.name,
                "method": action.method,
                "path": action.path,
            },
            "echo": {
                "payload": payload or {},
            },
        },
    }


def build_validation_error(error: PayloadValidationError) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Payload does not match input schema",
            "details": error.details,
        },
    }


def _to_hex(value: str | None) -> str:
    if not value:
        return ""
    try:
        if len(value) == 32 and "-" not in value:
            return value
        return uuid.UUID(value).hex
    except (ValueError, TypeError):
        return value
