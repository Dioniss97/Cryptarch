"""
Implements SavedFilterRepository port. Uses Session and ORM models (SavedFilterOrm, SavedFilterTagOrm).
"""
from typing import List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from adapters.driven.persistence.models import SavedFilterOrm, SavedFilterTagOrm
from adapters.driven.persistence.uuid_utils import normalize_uuid, parse_uuid, to_hex
from core.domain.models import SavedFilter
from core.ports.saved_filter_repository import SavedFilterRepository


def _orm_to_domain(orm: SavedFilterOrm) -> SavedFilter:
    return SavedFilter(
        id=str(orm.id),
        tenant_id=str(orm.tenant_id),
        target_type=orm.target_type,
        name=orm.name,
    )


class SavedFilterRepositoryImpl(SavedFilterRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_tenant(self, tenant_id: str) -> List[SavedFilter]:
        tid = parse_uuid(tenant_id)
        if tid is None:
            return []
        rows = (
            self._session.query(SavedFilterOrm)
            .filter(
                or_(
                    SavedFilterOrm.tenant_id == tid.hex,
                    SavedFilterOrm.tenant_id == str(tid),
                )
            )
            .all()
        )
        return [_orm_to_domain(r) for r in rows]

    def get_by_id(self, filter_id: str, tenant_id: str) -> SavedFilter | None:
        fid = parse_uuid(filter_id)
        if fid is None:
            return None
        f_hex, f_canonical = fid.hex, str(fid)
        orm = (
            self._session.query(SavedFilterOrm)
            .filter(or_(SavedFilterOrm.id == f_hex, SavedFilterOrm.id == f_canonical))
            .first()
        )
        if not orm or normalize_uuid(str(orm.tenant_id)) != normalize_uuid(tenant_id):
            return None
        return _orm_to_domain(orm)

    def get_filter_tag_ids(self, filter_id: str) -> List[str]:
        """Return tag_ids for the filter as canonical UUID strings. filter_id can be hex or canonical."""
        fid = parse_uuid(filter_id)
        if fid is None:
            return []
        f_hex, f_canonical = fid.hex, str(fid)
        rows = (
            self._session.query(SavedFilterTagOrm.tag_id)
            .filter(
                or_(
                    SavedFilterTagOrm.saved_filter_id == f_hex,
                    SavedFilterTagOrm.saved_filter_id == f_canonical,
                )
            )
            .all()
        )
        result = []
        for (tag_id,) in rows:
            u = parse_uuid(tag_id) if tag_id else None
            result.append(str(u) if u else str(tag_id))
        return result

    def add(self, saved_filter: SavedFilter, tag_ids: List[str]) -> SavedFilter:
        orm = SavedFilterOrm(
            tenant_id=saved_filter.tenant_id,
            target_type=saved_filter.target_type,
            name=saved_filter.name,
        )
        self._session.add(orm)
        self._session.flush()
        filter_id = orm.id
        for tag_id in tag_ids:
            self._session.add(
                SavedFilterTagOrm(
                    saved_filter_id=filter_id,
                    tag_id=to_hex(tag_id),
                )
            )
        self._session.flush()
        self._session.refresh(orm)
        return _orm_to_domain(orm)

    def save(
        self, saved_filter: SavedFilter, tag_ids: List[str] | None
    ) -> SavedFilter:
        fid = parse_uuid(saved_filter.id)
        if fid is None:
            return saved_filter
        f_hex, f_canonical = fid.hex, str(fid)
        orm = (
            self._session.query(SavedFilterOrm)
            .filter(or_(SavedFilterOrm.id == f_hex, SavedFilterOrm.id == f_canonical))
            .first()
        )
        if not orm:
            return saved_filter
        if tag_ids is not None:
            self._session.query(SavedFilterTagOrm).filter(
                SavedFilterTagOrm.saved_filter_id == orm.id
            ).delete()
            for tag_id in tag_ids:
                self._session.add(
                    SavedFilterTagOrm(
                        saved_filter_id=orm.id,
                        tag_id=to_hex(tag_id),
                    )
                )
        if saved_filter.name is not None:
            orm.name = saved_filter.name
        self._session.flush()
        self._session.refresh(orm)
        return _orm_to_domain(orm)

    def delete(self, saved_filter: SavedFilter) -> None:
        fid = parse_uuid(saved_filter.id)
        if fid is None:
            return
        f_hex, f_canonical = fid.hex, str(fid)
        orm = (
            self._session.query(SavedFilterOrm)
            .filter(or_(SavedFilterOrm.id == f_hex, SavedFilterOrm.id == f_canonical))
            .first()
        )
        if orm is not None:
            self._session.query(SavedFilterTagOrm).filter(
                SavedFilterTagOrm.saved_filter_id == orm.id
            ).delete()
            self._session.delete(orm)
