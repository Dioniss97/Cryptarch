"""Port for UserPreferences persistence."""

from typing import Protocol

from core.domain.models import UserPreferences


class UserPreferencesRepository(Protocol):
    def get_by_user(self, tenant_id: str, user_id: str) -> UserPreferences | None: ...

    def upsert(self, preferences: UserPreferences) -> UserPreferences: ...
