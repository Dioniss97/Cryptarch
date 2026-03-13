"""User preference use cases for authenticated users."""
from core.domain.models import UserPreference
from core.ports.user_preferences_repository import UserPreferencesRepository


def get_user_preferences(
    tenant_id: str, user_id: str, repo: UserPreferencesRepository
) -> UserPreference:
    existing = repo.get_by_user(tenant_id, user_id)
    if existing is not None:
        return existing
    return UserPreference(tenant_id=tenant_id, user_id=user_id)


def set_user_preferences(
    tenant_id: str,
    user_id: str,
    repo: UserPreferencesRepository,
    *,
    language: str | None = None,
    theme: str | None = None,
    table_density: str | None = None,
    metadata: dict | None = None,
) -> UserPreference:
    current = get_user_preferences(tenant_id, user_id, repo)
    if language is not None:
        current.language = language
    if theme is not None:
        current.theme = theme
    if table_density is not None:
        current.table_density = table_density
    if metadata is not None:
        current.metadata = metadata
    return repo.upsert(current)
