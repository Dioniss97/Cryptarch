"""Use cases for current-user preferences."""

from shared_contract import USER_THEME_SYSTEM

from core.domain.models import UserPreferences
from core.ports.user_preferences_repository import UserPreferencesRepository

DEFAULT_LANGUAGE = "es"
DEFAULT_TABLE_DENSITY = "comfortable"
DEFAULT_METADATA: dict = {}


def _defaults(tenant_id: str, user_id: str) -> UserPreferences:
    return UserPreferences(
        tenant_id=tenant_id,
        user_id=user_id,
        theme=USER_THEME_SYSTEM,
        language=DEFAULT_LANGUAGE,
        table_density=DEFAULT_TABLE_DENSITY,
        metadata=dict(DEFAULT_METADATA),
    )


def get_preferences(
    tenant_id: str,
    user_id: str,
    repo: UserPreferencesRepository,
) -> UserPreferences:
    stored = repo.get_by_user(tenant_id, user_id)
    if stored is None:
        return _defaults(tenant_id, user_id)
    return stored


def update_preferences(
    tenant_id: str,
    user_id: str,
    *,
    theme: str | None = None,
    language: str | None = None,
    table_density: str | None = None,
    metadata: dict | None = None,
    repo: UserPreferencesRepository,
) -> UserPreferences:
    current = get_preferences(tenant_id, user_id, repo)
    updated = UserPreferences(
        tenant_id=tenant_id,
        user_id=user_id,
        theme=theme if theme is not None else current.theme,
        language=language if language is not None else current.language,
        table_density=(
            table_density if table_density is not None else current.table_density
        ),
        metadata=(
            dict(metadata) if metadata is not None else dict(current.metadata or {})
        ),
    )
    return repo.upsert(updated)
