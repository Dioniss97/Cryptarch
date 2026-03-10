"""
Resolve effective permissions: groups whose user-filters match the user,
then union of actions and documents from those groups' filters.
Tenant-scoped; tag AND semantics within each saved filter.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.models import (
    Action,
    ActionTag,
    Document,
    DocumentTag,
    Group,
    GroupActionFilter,
    GroupDocumentFilter,
    GroupUserFilter,
    SavedFilter,
    SavedFilterTag,
    UserTag,
)


def entity_has_all_filter_tags(
    session: Session, target_type: str, entity_id: str, saved_filter_id: str
) -> bool:
    """True iff the entity has every tag required by the saved filter (AND semantics)."""
    filter_tag_ids = [
        r[0]
        for r in session.execute(
            select(SavedFilterTag.tag_id).where(
                SavedFilterTag.saved_filter_id == saved_filter_id
            )
        ).all()
    ]
    if not filter_tag_ids:
        return True
    if target_type == "user":
        entity_tag_ids = [
            r[0]
            for r in session.execute(
                select(UserTag.tag_id).where(UserTag.user_id == entity_id)
            ).all()
        ]
    elif target_type == "action":
        entity_tag_ids = [
            r[0]
            for r in session.execute(
                select(ActionTag.tag_id).where(ActionTag.action_id == entity_id)
            ).all()
        ]
    elif target_type == "document":
        entity_tag_ids = [
            r[0]
            for r in session.execute(
                select(DocumentTag.tag_id).where(DocumentTag.document_id == entity_id)
            ).all()
        ]
    else:
        raise ValueError(f"Unknown target_type: {target_type}")
    return set(filter_tag_ids) <= set(entity_tag_ids)


def _group_ids_where_user_matches(session: Session, tenant_id: str, user_id: str) -> list:
    """Group IDs in this tenant for which the user matches at least one user filter."""
    rows = session.execute(
        select(GroupUserFilter.group_id, GroupUserFilter.saved_filter_id)
        .select_from(GroupUserFilter)
        .join(Group, Group.id == GroupUserFilter.group_id)
        .where(Group.tenant_id == tenant_id)
    ).all()
    result = []
    for (group_id, saved_filter_id) in rows:
        if entity_has_all_filter_tags(session, "user", user_id, saved_filter_id):
            result.append(group_id)
    return result


def _action_ids_matching_filter(
    session: Session, tenant_id: str, saved_filter_id: str
) -> set[str]:
    """Action IDs in tenant that have ALL tags of the saved filter (AND)."""
    filter_tag_ids = [
        r[0]
        for r in session.execute(
            select(SavedFilterTag.tag_id).where(
                SavedFilterTag.saved_filter_id == saved_filter_id
            )
        ).all()
    ]
    if not filter_tag_ids:
        return set()
    action_ids = [
        r[0]
        for r in session.execute(
            select(Action.id).where(Action.tenant_id == tenant_id)
        ).all()
    ]
    def _norm(s):
        if s is None:
            return s
        return str(s).replace("-", "").lower()

    return {
        _norm(aid)
        for aid in action_ids
        if entity_has_all_filter_tags(session, "action", aid, saved_filter_id)
    }


def _document_ids_matching_filter(
    session: Session, tenant_id: str, saved_filter_id: str
) -> set[str]:
    """Document IDs in tenant that have ALL tags of the saved filter (AND)."""
    doc_ids = [
        r[0]
        for r in session.execute(
            select(Document.id).where(Document.tenant_id == tenant_id)
        ).all()
    ]
    def _norm(s):
        if s is None:
            return s
        return str(s).replace("-", "").lower()

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
    result = set()
    for group_id in group_ids:
        rows = session.execute(
            select(GroupActionFilter.saved_filter_id).where(
                GroupActionFilter.group_id == group_id
            )
        ).all()
        for (saved_filter_id,) in rows:
            result |= _action_ids_matching_filter(
                session, tenant_id, saved_filter_id
            )
    return result


def resolve_effective_document_ids(
    session: Session, tenant_id: str, user_id: str
) -> set[str]:
    """Effective visible document IDs for the user (tenant-scoped, union of groups)."""
    group_ids = _group_ids_where_user_matches(session, tenant_id, user_id)
    result = set()
    for group_id in group_ids:
        rows = session.execute(
            select(GroupDocumentFilter.saved_filter_id).where(
                GroupDocumentFilter.group_id == group_id
            )
        ).all()
        for (saved_filter_id,) in rows:
            result |= _document_ids_matching_filter(
                session, tenant_id, saved_filter_id
            )
    return result
