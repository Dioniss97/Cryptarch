"""TagRepository implementation using Session and ORM Tag models."""
from sqlalchemy import or_
from sqlalchemy.orm import Session

from adapters.driven.persistence.models import TagOrm
from adapters.driven.persistence.uuid_utils import normalize_uuid, parse_uuid
from core.domain.models import Tag
from core.ports.tag_repository import TagRepository


def _orm_to_domain(orm: TagOrm) -> Tag:
    return Tag(id=str(orm.id), tenant_id=str(orm.tenant_id), name=orm.name)


class SqlAlchemyTagRepository(TagRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_tenant(self, tenant_id: str) -> list[Tag]:
        # Accept both canonical and hex tenant ids.
        tid_norm = normalize_uuid(tenant_id)
        tid_parsed = parse_uuid(tenant_id)
        tenant_hex = tid_parsed.hex if tid_parsed else tenant_id
        rows = (
            self._session.query(TagOrm)
            .filter(
                or_(
                    TagOrm.tenant_id == tenant_hex,
                    TagOrm.tenant_id == tid_norm,
                )
            )
            .all()
        )
        return [_orm_to_domain(r) for r in rows]

    def get_by_id(self, tag_id: str, tenant_id: str) -> Tag | None:
        uid = parse_uuid(tag_id)
        if uid is None:
            return None
        uid_hex = uid.hex
        uid_canonical = str(uid)
        orm = (
            self._session.query(TagOrm)
            .filter(or_(TagOrm.id == uid_hex, TagOrm.id == uid_canonical))
            .first()
        )
        if not orm or normalize_uuid(str(orm.tenant_id)) != normalize_uuid(tenant_id):
            return None
        return _orm_to_domain(orm)

    def get_by_name(self, tenant_id: str, name: str) -> Tag | None:
        tid_norm = normalize_uuid(tenant_id)
        orm = (
            self._session.query(TagOrm)
            .filter(TagOrm.tenant_id == tid_norm, TagOrm.name == name)
            .first()
        )
        return _orm_to_domain(orm) if orm else None

    def add(self, tag: Tag) -> Tag:
        orm = TagOrm(
            tenant_id=tag.tenant_id,
            name=tag.name,
        )
        self._session.add(orm)
        self._session.flush()
        self._session.refresh(orm)
        return _orm_to_domain(orm)

    def save(self, tag: Tag) -> Tag:
        uid = parse_uuid(tag.id)
        if uid is None:
            return tag
        uid_hex = uid.hex
        uid_canonical = str(uid)
        orm = (
            self._session.query(TagOrm)
            .filter(or_(TagOrm.id == uid_hex, TagOrm.id == uid_canonical))
            .first()
        )
        if not orm:
            return tag
        orm.name = tag.name
        self._session.flush()
        self._session.refresh(orm)
        return _orm_to_domain(orm)

    def delete(self, tag: Tag) -> None:
        uid = parse_uuid(tag.id)
        if uid is None:
            return
        uid_hex = uid.hex
        uid_canonical = str(uid)
        orm = (
            self._session.query(TagOrm)
            .filter(or_(TagOrm.id == uid_hex, TagOrm.id == uid_canonical))
            .first()
        )
        if orm is not None:
            self._session.delete(orm)
