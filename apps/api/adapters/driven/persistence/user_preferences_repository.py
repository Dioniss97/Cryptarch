"""UserPreferences repository implementation."""

from core.domain.models import UserPreferences
from core.ports.user_preferences_repository import UserPreferencesRepository
from sqlalchemy.orm import Session

from adapters.driven.persistence.models import UserPreferencesOrm
from adapters.driven.persistence.uuid_utils import eq_uuid, normalize_uuid, parse_uuid


def _orm_to_domain(orm: UserPreferencesOrm) -> UserPreferences:
    meta = orm.metadata_
    return UserPreferences(
        user_id=str(orm.user_id),
        tenant_id=str(orm.tenant_id),
        theme=orm.theme,
        language=orm.language,
        table_density=orm.table_density,
        metadata=dict(meta) if meta is not None else {},
    )


class UserPreferencesRepositoryImpl(UserPreferencesRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def _query_for_user(self, tenant_id: str, user_id: str):
        uid = parse_uuid(user_id)
        tid = parse_uuid(tenant_id)
        if uid is None or tid is None:
            return None
        uid_hex = uid.hex
        uid_canonical = str(uid)
        tid_hex = tid.hex
        tid_canonical = str(tid)
        return self._session.query(UserPreferencesOrm).filter(
            UserPreferencesOrm.tenant_id.in_([tid_hex, tid_canonical]),
            UserPreferencesOrm.user_id.in_([uid_hex, uid_canonical]),
        )

    def get_by_user(self, tenant_id: str, user_id: str) -> UserPreferences | None:
        q = self._query_for_user(tenant_id, user_id)
        if q is None:
            return None
        orm = q.first()
        if orm is None:
            return None
        if not eq_uuid(str(orm.tenant_id), tenant_id):
            return None
        return _orm_to_domain(orm)

    def upsert(self, preferences: UserPreferences) -> UserPreferences:
        uid = parse_uuid(preferences.user_id)
        if uid is None:
            return preferences
        uid_hex = uid.hex
        q = self._query_for_user(preferences.tenant_id, preferences.user_id)
        orm = q.first() if q is not None else None
        tid = normalize_uuid(preferences.tenant_id) or preferences.tenant_id
        meta = preferences.metadata if preferences.metadata is not None else {}
        if orm is None:
            orm = UserPreferencesOrm(
                tenant_id=tid,
                user_id=uid_hex,
                theme=preferences.theme,
                language=preferences.language,
                table_density=preferences.table_density,
                metadata_=meta,
            )
            self._session.add(orm)
        else:
            orm.theme = preferences.theme
            orm.language = preferences.language
            orm.table_density = preferences.table_density
            orm.metadata_ = meta
        self._session.flush()
        self._session.refresh(orm)
        return _orm_to_domain(orm)
