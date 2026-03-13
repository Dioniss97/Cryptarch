"""
Implementation of PermissionQueryPort. Resolves allowed actions/documents for a user.
All SQL and Session usage lives here (driven adapter).
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from adapters.driven.persistence.models import (
    ActionOrm,
    ActionTagOrm,
    DocumentOrm,
    DocumentTagOrm,
    GroupActionFilterOrm,
    GroupDocumentFilterOrm,
    GroupOrm,
    GroupUserFilterOrm,
    SavedFilterTagOrm,
    UserTagOrm,
)
from adapters.driven.persistence.uuid_utils import normalize_uuid, parse_uuid, to_hex
from core.ports.permission_query import PermissionQueryPort


def entity_has_all_filter_tags(
    session: Session, target_type: str, entity_id: str, saved_filter_id: str
) -> bool:
    """True iff the entity has every tag required by the saved filter (AND semantics)."""
    filter_tag_ids = [
        r[0]
        for r in session.execute(
            select(SavedFilterTagOrm.tag_id).where(
                SavedFilterTagOrm.saved_filter_id == saved_filter_id
            )
        ).all()
    ]
    if not filter_tag_ids:
        return True
    if target_type == "user":
        entity_tag_ids = [
            r[0]
            for r in session.execute(
                select(UserTagOrm.tag_id).where(UserTagOrm.user_id == entity_id)
            ).all()
        ]
    elif target_type == "action":
        entity_tag_ids = [
            r[0]
            for r in session.execute(
                select(ActionTagOrm.tag_id).where(ActionTagOrm.action_id == entity_id)
            ).all()
        ]
    elif target_type == "document":
        entity_tag_ids = [
            r[0]
            for r in session.execute(
                select(DocumentTagOrm.tag_id).where(
                    DocumentTagOrm.document_id == entity_id
                )
            ).all()
        ]
    else:
        raise ValueError(f"Unknown target_type: {target_type}")
    return set(filter_tag_ids) <= set(entity_tag_ids)


def _group_ids_where_user_matches(session: Session, tenant_id: str, user_id: str) -> list:
    """Return group ids (DB ids) where the user matches the group's user filter.

    Accepts tenant_id and user_id in hex or canonical form; comparisons are done in a
    tolerant way so tests that pass either representation still work.
    """
    # Normalize tenant id to support both hex and canonical.
    tid_norm = normalize_uuid(tenant_id)
    tid_parsed = parse_uuid(tenant_id)
    tenant_hex = tid_parsed.hex if tid_parsed else tenant_id

    rows = (
        session.execute(
            select(GroupUserFilterOrm.group_id, GroupUserFilterOrm.saved_filter_id)
            .select_from(GroupUserFilterOrm)
            .join(GroupOrm, GroupOrm.id == GroupUserFilterOrm.group_id)
            .where(
                GroupOrm.tenant_id.in_(
                    [
                        tenant_hex,
                        tid_norm,
                    ]
                )
            )
        ).all()
    )
    result = []
    for (group_id, saved_filter_id) in rows:
        if entity_has_all_filter_tags(session, "user", user_id, saved_filter_id):
            result.append(group_id)
    return result


def _action_ids_matching_filter(
    session: Session, tenant_id: str, saved_filter_id: str
) -> set[str]:
    filter_tag_ids = [
        r[0]
        for r in session.execute(
            select(SavedFilterTagOrm.tag_id).where(
                SavedFilterTagOrm.saved_filter_id == saved_filter_id
            )
        ).all()
    ]
    if not filter_tag_ids:
        return set()
    tid_norm = normalize_uuid(tenant_id)
    tid_parsed = parse_uuid(tenant_id)
    tenant_hex = tid_parsed.hex if tid_parsed else tenant_id

    action_ids = [
        r[0]
        for r in session.execute(
            select(ActionOrm.id).where(
                ActionOrm.tenant_id.in_(
                    [
                        tenant_hex,
                        tid_norm,
                    ]
                )
            )
        ).all()
    ]

    def _norm(s: str | None) -> str | None:
        if s is None:
            return s
        # normalize to hex to match how ids are compared in domain
        return to_hex(str(s))

    return {
        _norm(aid)
        for aid in action_ids
        if entity_has_all_filter_tags(session, "action", aid, saved_filter_id)
    }


def _document_ids_matching_filter(
    session: Session, tenant_id: str, saved_filter_id: str
) -> set[str]:
    tid_norm = normalize_uuid(tenant_id)
    tid_parsed = parse_uuid(tenant_id)
    tenant_hex = tid_parsed.hex if tid_parsed else tenant_id

    doc_ids = [
        r[0]
        for r in session.execute(
            select(DocumentOrm.id).where(
                DocumentOrm.tenant_id.in_(
                    [
                        tenant_hex,
                        tid_norm,
                    ]
                )
            )
        ).all()
    ]

    def _norm(s: str | None) -> str | None:
        if s is None:
            return s
        return to_hex(str(s))

    return {
        _norm(did)
        for did in doc_ids
        if entity_has_all_filter_tags(session, "document", did, saved_filter_id)
    }


def resolve_effective_action_ids(
    session: Session, tenant_id: str, user_id: str
) -> set[str]:
    """Effective allowed action IDs for the user (tenant-scoped, union of groups)."""
    group_ids = _group_ids_where_user_matches(session, tenant_id, user_id)
    result: set[str] = set()
    for group_id in group_ids:
        rows = session.execute(
            select(GroupActionFilterOrm.saved_filter_id).where(
                GroupActionFilterOrm.group_id == group_id
            )
        ).all()
        for (saved_filter_id,) in rows:
            result |= _action_ids_matching_filter(session, tenant_id, saved_filter_id)
    return result


def resolve_effective_document_ids(
    session: Session, tenant_id: str, user_id: str
) -> set[str]:
    """Effective visible document IDs for the user (tenant-scoped, union of groups)."""
    group_ids = _group_ids_where_user_matches(session, tenant_id, user_id)
    result: set[str] = set()
    for group_id in group_ids:
        rows = session.execute(
            select(GroupDocumentFilterOrm.saved_filter_id).where(
                GroupDocumentFilterOrm.group_id == group_id
            )
        ).all()
        for (saved_filter_id,) in rows:
            result |= _document_ids_matching_filter(
                session, tenant_id, saved_filter_id
            )
    return result


class PermissionQueryImpl(PermissionQueryPort):
    """Implements PermissionQueryPort; receives Session at construction."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def resolve_effective_action_ids(self, tenant_id: str, user_id: str) -> set[str]:
        return resolve_effective_action_ids(self._session, tenant_id, user_id)

    def resolve_effective_document_ids(self, tenant_id: str, user_id: str) -> set[str]:
        return resolve_effective_document_ids(self._session, tenant_id, user_id)
