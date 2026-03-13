"""Schemas for user preference endpoints."""
from typing import Any

from pydantic import BaseModel, Field

from core.domain.models import UserPreference


class UserPreferencesPatchBody(BaseModel):
    language: str | None = Field(default=None, min_length=2, max_length=16)
    theme: str | None = None
    table_density: str | None = None
    metadata: dict[str, Any] | None = None


def validate_allowed_values(body: UserPreferencesPatchBody) -> None:
    if body.theme is not None and body.theme not in {"system", "light", "dark"}:
        raise ValueError("theme must be one of: system, light, dark")
    if body.table_density is not None and body.table_density not in {
        "comfortable",
        "compact",
    }:
        raise ValueError("table_density must be one of: comfortable, compact")


def to_response(preferences: UserPreference) -> dict[str, Any]:
    return {
        "language": preferences.language,
        "theme": preferences.theme,
        "table_density": preferences.table_density,
        "metadata": preferences.metadata,
    }
