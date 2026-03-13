"""
GroupRepository implementation. Persists Group and filter bindings (GroupUserFilter,
GroupActionFilter, GroupDocumentFilter). Validates that saved filter ids exist and
belong to the group's tenant before add/save; raises FilterNotFoundInTenantError
if any filter is missing or not in tenant.
"""
from sqlalchemy import or_
from sqlalchemy.orm import Session

from adapters.driven.persistence.models import (
    GroupActionFilterOrm,
    GroupDocumentFilterOrm,
    GroupOrm,
    GroupUserFilterOrm,
    SavedFilterOrm,
)
from adapters.driven.persistence.uuid_utils import (
    canonical_to_hex,
    normalize_uuid,
    parse_uuid,
    to_hex,
)
from core.domain.models import Group
from core.ports.group_repository import GroupRepository


class FilterNotFoundInTenantError(Exception):
    """Raised when a saved filter id does not exist or does not belong to the tenant."""


def _orm_to_domain(orm: GroupOrm) -> Group:
    return Group(id=str(orm.id), tenant_id=str(orm.tenant_id), name=orm.name)


class GroupRepositoryImpl(GroupRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_tenant(self, tenant_id: str) -> list[Group]:
        tid_norm = normalize_uuid(tenant_id)
        tid_parsed = parse_uuid(tenant_id)
        tenant_hex = tid_parsed.hex if tid_parsed else tenant_id
        rows = (
            self._session.query(GroupOrm)
            .filter(
                or_(GroupOrm.tenant_id == tenant_hex, GroupOrm.tenant_id == tid_norm)
            )
            .all()
        )
        return [_orm_to_domain(r) for r in rows]

    def get_by_id(self, group_id: str, tenant_id: str) -> Group | None:
        gid = parse_uuid(group_id)
        if gid is None:
            return None
        g_hex, g_canonical = gid.hex, str(gid)
        orm = (
            self._session.query(GroupOrm)
            .filter(or_(GroupOrm.id == g_hex, GroupOrm.id == g_canonical))
            .first()
        )
        if not orm or normalize_uuid(str(orm.tenant_id)) != normalize_uuid(tenant_id):
            return None
        return _orm_to_domain(orm)

    def get_group_filter_ids(
        self, group_id: str
    ) -> tuple[list[str], list[str], list[str]]:
        """Return (user_filter_ids, action_filter_ids, document_filter_ids) in canonical form."""

        gid = parse_uuid(group_id)
        if gid is None:
            return ([], [], [])
        g_hex, g_canonical = gid.hex, str(gid)

        def ids_from_table(model, col) -> list[str]:
            rows = (
                self._session.query(col)
                .filter(
                    or_(
                        model.group_id == g_hex,
                        model.group_id == g_canonical,
                    )
                )
                .all()
            )
            return [str(parse_uuid(r[0]) or r[0]) for r in rows]

        uids = ids_from_table(GroupUserFilterOrm, GroupUserFilterOrm.saved_filter_id)
        aids = ids_from_table(GroupActionFilterOrm, GroupActionFilterOrm.saved_filter_id)
        dids = ids_from_table(
            GroupDocumentFilterOrm, GroupDocumentFilterOrm.saved_filter_id
        )
        return (uids, aids, dids)

    def _validate_filter_ids_in_tenant(
        self, filter_ids: list[str], tenant_id: str
    ) -> None:
        tid_norm = normalize_uuid(tenant_id)
        tid_parsed = parse_uuid(tenant_id)
        tenant_hex = tid_parsed.hex if tid_parsed else tenant_id
        for fid in filter_ids:
            fid_parsed = parse_uuid(fid)
            if fid_parsed is None:
                raise FilterNotFoundInTenantError(f"Invalid filter id: {fid}")
            f_hex, f_canonical = fid_parsed.hex, str(fid_parsed)
            sf = (
                self._session.query(SavedFilterOrm)
                .filter(
                    or_(SavedFilterOrm.id == f_hex, SavedFilterOrm.id == f_canonical),
                    or_(
                        SavedFilterOrm.tenant_id == tenant_hex,
                        SavedFilterOrm.tenant_id == tid_norm,
                    ),
                )
                .first()
            )
            if not sf:
                raise FilterNotFoundInTenantError(
                    f"Filter not found or not in tenant: {fid}"
                )

    def add(
        self,
        group: Group,
        user_filter_ids: list[str],
        action_filter_ids: list[str],
        document_filter_ids: list[str],
    ) -> Group:
        all_ids = user_filter_ids + action_filter_ids + document_filter_ids
        if all_ids:
            self._validate_filter_ids_in_tenant(all_ids, group.tenant_id)
        orm = GroupOrm(tenant_id=group.tenant_id, name=group.name)
        self._session.add(orm)
        self._session.flush()
        for fid in user_filter_ids:
            h = canonical_to_hex(fid) or to_hex(fid)
            self._session.add(
                GroupUserFilterOrm(group_id=orm.id, saved_filter_id=h)
            )
        for fid in action_filter_ids:
            h = canonical_to_hex(fid) or to_hex(fid)
            self._session.add(
                GroupActionFilterOrm(group_id=orm.id, saved_filter_id=h)
            )
        for fid in document_filter_ids:
            h = canonical_to_hex(fid) or to_hex(fid)
            self._session.add(
                GroupDocumentFilterOrm(group_id=orm.id, saved_filter_id=h)
            )
        self._session.flush()
        self._session.refresh(orm)
        return _orm_to_domain(orm)

    def save(
        self,
        group: Group,
        user_filter_ids: list[str] | None,
        action_filter_ids: list[str] | None,
        document_filter_ids: list[str] | None,
    ) -> Group:
        tenant_id = str(group.tenant_id)
        gid = parse_uuid(group.id)
        if gid is None:
            return group
        g_hex, g_canonical = gid.hex, str(gid)
        orm = (
            self._session.query(GroupOrm)
            .filter(or_(GroupOrm.id == g_hex, GroupOrm.id == g_canonical))
            .first()
        )
        if not orm:
            return group

        if user_filter_ids is not None:
            self._validate_filter_ids_in_tenant(user_filter_ids, tenant_id)
        if action_filter_ids is not None:
            self._validate_filter_ids_in_tenant(action_filter_ids, tenant_id)
        if document_filter_ids is not None:
            self._validate_filter_ids_in_tenant(document_filter_ids, tenant_id)

        if group.name is not None:
            orm.name = group.name

        if user_filter_ids is not None:
            self._session.query(GroupUserFilterOrm).filter(
                GroupUserFilterOrm.group_id == orm.id
            ).delete()
            for fid in user_filter_ids:
                h = canonical_to_hex(fid) or to_hex(fid)
                self._session.add(
                    GroupUserFilterOrm(group_id=orm.id, saved_filter_id=h)
                )
        if action_filter_ids is not None:
            self._session.query(GroupActionFilterOrm).filter(
                GroupActionFilterOrm.group_id == orm.id
            ).delete()
            for fid in action_filter_ids:
                h = canonical_to_hex(fid) or to_hex(fid)
                self._session.add(
                    GroupActionFilterOrm(group_id=orm.id, saved_filter_id=h)
                )
        if document_filter_ids is not None:
            self._session.query(GroupDocumentFilterOrm).filter(
                GroupDocumentFilterOrm.group_id == orm.id
            ).delete()
            for fid in document_filter_ids:
                h = canonical_to_hex(fid) or to_hex(fid)
                self._session.add(
                    GroupDocumentFilterOrm(group_id=orm.id, saved_filter_id=h)
                )
        self._session.flush()
        self._session.refresh(orm)
        return _orm_to_domain(orm)

    def delete(self, group: Group) -> None:
        """Remove filter bindings and then the group."""
        gid = parse_uuid(group.id)
        if gid is None:
            return
        g_hex, g_canonical = gid.hex, str(gid)
        orm = (
            self._session.query(GroupOrm)
            .filter(or_(GroupOrm.id == g_hex, GroupOrm.id == g_canonical))
            .first()
        )
        if orm is not None:
            self._session.query(GroupUserFilterOrm).filter(
                GroupUserFilterOrm.group_id == orm.id
            ).delete()
            self._session.query(GroupActionFilterOrm).filter(
                GroupActionFilterOrm.group_id == orm.id
            ).delete()
            self._session.query(GroupDocumentFilterOrm).filter(
                GroupDocumentFilterOrm.group_id == orm.id
            ).delete()
            self._session.delete(orm)