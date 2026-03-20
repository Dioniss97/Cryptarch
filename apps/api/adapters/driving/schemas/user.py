"""Request/response schemas for User admin API."""
import uuid
from pydantic import BaseModel

from core.domain.models import User


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


class UserCreateBody(BaseModel):
    email: str
    role: str  # admin | user
    password: str


class UserUpdateBody(BaseModel):
    email: str | None = None
    role: str | None = None
    password: str | None = None


def user_to_response(user: User) -> dict:
    """Serialize User to JSON. IDs in canonical form (with hyphens) for consistent API contract."""
    ui = _parse_uuid(str(user.id)) if user.id else None
    ti = _parse_uuid(str(user.tenant_id)) if user.tenant_id else None
    return {
        "id": str(ui) if ui else str(user.id),
        "tenant_id": str(ti) if ti else str(user.tenant_id),
        "email": user.email,
        "role": user.role,
    }
