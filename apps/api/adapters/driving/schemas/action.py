"""Request/response schemas for Action (admin)."""
import uuid
from typing import Any, Protocol

from pydantic import BaseModel


class ActionCreateBody(BaseModel):
    connector_id: uuid.UUID
    method: str
    path: str
    name: str | None = None
    request_config: dict[str, Any] | None = None
    tag_ids: list[uuid.UUID] = []


class ActionUpdateBody(BaseModel):
    method: str | None = None
    path: str | None = None
    name: str | None = None
    request_config: dict[str, Any] | None = None
    tag_ids: list[uuid.UUID] | None = None


def action_to_response(
    action: "ActionLike",
    tag_ids: list[str],
) -> dict:
    """Serialize Action to response dict. tag_ids must be canonical UUID strings."""
    return {
        "id": _canonical_str(action.id),
        "tenant_id": _canonical_str(action.tenant_id),
        "connector_id": _canonical_str(action.connector_id),
        "method": action.method,
        "path": action.path,
        "name": action.name,
        "request_config": action.request_config,
        "tag_ids": tag_ids,
    }


def _canonical_str(value: str | None) -> str:
    if not value:
        return ""
    try:
        if len(value) == 32 and "-" not in value:
            return str(uuid.UUID(hex=value))
        return str(uuid.UUID(value))
    except (ValueError, TypeError):
        return value


class ActionLike(Protocol):
    """Minimal interface for action_to_response (core.domain.models.Action)."""
    id: str
    tenant_id: str
    connector_id: str
    method: str
    path: str
    name: str | None
    request_config: dict[str, Any] | None
