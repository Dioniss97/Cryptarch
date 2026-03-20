"""Request/response schemas and serialization for Tags."""
import uuid
from pydantic import BaseModel


def _parse_uuid(value: str) -> uuid.UUID | None:
    if not value or not isinstance(value, str):
        return None
    value = value.strip()
    try:
        if len(value) == 32 and "-" not in value:
            return uuid.UUID(hex=value)
        return uuid.UUID(value)
    except (ValueError, TypeError):
        return None


class TagCreateBody(BaseModel):
    name: str


class TagUpdateBody(BaseModel):
    name: str | None = None


def tag_to_response(tag) -> dict:
    """Serialize Tag to response dict. id and tenant_id in canonical form."""
    ui = _parse_uuid(str(tag.id)) if getattr(tag, "id", None) else None
    ti = _parse_uuid(str(tag.tenant_id)) if getattr(tag, "tenant_id", None) else None
    return {
        "id": str(ui) if ui else str(getattr(tag, "id", "")),
        "tenant_id": str(ti) if ti else str(getattr(tag, "tenant_id", "")),
        "name": tag.name,
    }
