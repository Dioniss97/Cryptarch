"""Request/response schemas for Group admin API."""
import uuid

from pydantic import BaseModel

from core.domain.models import Group


class GroupCreateBody(BaseModel):
    name: str
    user_filter_ids: list[uuid.UUID] = []
    action_filter_ids: list[uuid.UUID] = []
    document_filter_ids: list[uuid.UUID] = []


class GroupUpdateBody(BaseModel):
    name: str | None = None
    user_filter_ids: list[uuid.UUID] | None = None
    action_filter_ids: list[uuid.UUID] | None = None
    document_filter_ids: list[uuid.UUID] | None = None


def _ensure_canonical(value: str) -> str:
    try:
        if len(value) == 32 and "-" not in value:
            return str(uuid.UUID(hex=value))
        return str(uuid.UUID(value))
    except (ValueError, TypeError):
        return value


def group_to_response(
    group: Group,
    user_filter_ids: list[str],
    action_filter_ids: list[str],
    document_filter_ids: list[str],
) -> dict:
    """Serialize Group to JSON. All id fields in canonical form (with hyphens)."""
    return {
        "id": _ensure_canonical(str(group.id)),
        "tenant_id": _ensure_canonical(str(group.tenant_id)),
        "name": group.name,
        "user_filter_ids": user_filter_ids,
        "action_filter_ids": action_filter_ids,
        "document_filter_ids": document_filter_ids,
    }
