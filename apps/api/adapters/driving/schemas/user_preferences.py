"""Request/response schemas for /me/preferences."""

from typing import Any, Literal

from core.domain.models import UserPreferences
from pydantic import BaseModel, Field, field_validator
from shared_contract import UserTheme

TableDensity = Literal["comfortable", "compact"]


class UserPreferencesResponse(BaseModel):
    theme: UserTheme
    language: str
    table_density: TableDensity
    metadata: dict[str, Any] = Field(default_factory=dict)


class UserPreferencesPatchBody(BaseModel):
    theme: UserTheme | None = None
    language: str | None = Field(default=None, min_length=2, max_length=16)
    table_density: TableDensity | None = None
    metadata: dict[str, Any] | None = None

    @field_validator("language")
    @classmethod
    def language_reasonable(cls, value: str | None) -> str | None:
        if value is None:
            return value
        stripped = value.strip()
        if not stripped:
            raise ValueError("language must not be empty")
        if not all(ch.isalpha() or ch == "-" for ch in stripped):
            raise ValueError("language must contain only letters and hyphens")
        return stripped


def preferences_to_response(prefs: UserPreferences) -> dict:
    return UserPreferencesResponse(
        theme=prefs.theme,
        language=prefs.language,
        table_density=prefs.table_density,
        metadata=prefs.metadata or {},
    ).model_dump()
