"""Request/response schemas for Saved Filter (admin)."""
import uuid
from typing import Literal, Protocol

from pydantic import BaseModel


class FilterCreateBody(BaseModel):
    name: str
    target_type: Literal["user", "action", "document"]
    tag_ids: list[uuid.UUID] = []


class FilterUpdateBody(BaseModel):
    name: str | None = None
    tag_ids: list[uuid.UUID] | None = None


def filter_to_response(
    saved_filter: "SavedFilterLike",
    tag_ids: list[str] | None = None,
) -> dict:
    """Serialize SavedFilter to response dict. tag_ids must be canonical UUID strings."""
    if tag_ids is None:
        tag_ids = []
    id_val = _canonical_str(saved_filter.id)
    tenant_val = _canonical_str(saved_filter.tenant_id)
    return {
        "id": id_val,
        "tenant_id": tenant_val,
        "target_type": saved_filter.target_type,
        "name": saved_filter.name,
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


class SavedFilterLike(Protocol):
    """Minimal interface for filter_to_response (core.domain.models.SavedFilter)."""
    id: str
    tenant_id: str
    target_type: str
    name: str
