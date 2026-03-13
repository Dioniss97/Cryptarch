"""Port for user preferences persistence."""
from typing import Protocol

from core.domain.models import UserPreference


class UserPreferencesRepository(Protocol):
    def get_by_user(self, tenant_id: str, user_id: str) -> UserPreference | None:
        ...

    def upsert(self, preferences: UserPreference) -> UserPreference:
        ...
