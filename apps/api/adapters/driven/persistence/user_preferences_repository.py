"""User preferences repository implementation."""
from sqlalchemy.orm import Session

from adapters.driven.persistence.models import UserPreferenceOrm
from adapters.driven.persistence.uuid_utils import normalize_uuid, parse_uuid, to_hex
from core.domain.models import UserPreference
from core.ports.user_preferences_repository import UserPreferencesRepository


def _orm_to_domain(orm: UserPreferenceOrm) -> UserPreference:
    return UserPreference(
        id=str(orm.id),
        tenant_id=str(orm.tenant_id),
        user_id=str(orm.user_id),
        language=orm.language,
        theme=orm.theme,
        table_density=orm.table_density,
        metadata=orm.metadata_json,
    )


class UserPreferencesRepositoryImpl(UserPreferencesRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_user(self, tenant_id: str, user_id: str) -> UserPreference | None:
        tid = normalize_uuid(tenant_id)
        uid = normalize_uuid(user_id)
        if not tid or not uid:
            return None
        orm = (
            self._session.query(UserPreferenceOrm)
            .filter(
                UserPreferenceOrm.tenant_id.in_([tid, to_hex(tid)]),
                UserPreferenceOrm.user_id.in_([uid, to_hex(uid)]),
            )
            .first()
        )
        if orm is None:
            return None
        return _orm_to_domain(orm)

    def upsert(self, preferences: UserPreference) -> UserPreference:
        current = self.get_by_user(preferences.tenant_id, preferences.user_id)
        if current is None:
            tenant_uuid = parse_uuid(preferences.tenant_id)
            user_uuid = parse_uuid(preferences.user_id)
            orm = UserPreferenceOrm(
                tenant_id=tenant_uuid.hex if tenant_uuid else preferences.tenant_id,
                user_id=user_uuid.hex if user_uuid else preferences.user_id,
                language=preferences.language,
                theme=preferences.theme,
                table_density=preferences.table_density,
                metadata_json=preferences.metadata,
            )
            self._session.add(orm)
            self._session.flush()
            self._session.refresh(orm)
            return _orm_to_domain(orm)

        orm = (
            self._session.query(UserPreferenceOrm)
            .filter(UserPreferenceOrm.id.in_([current.id, to_hex(current.id)]))
            .first()
        )
        if orm is None:
            return preferences
        orm.language = preferences.language
        orm.theme = preferences.theme
        orm.table_density = preferences.table_density
        orm.metadata_json = preferences.metadata
        self._session.flush()
        self._session.refresh(orm)
        return _orm_to_domain(orm)
