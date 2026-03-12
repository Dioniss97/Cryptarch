"""Admin-only routes. All require admin role via require_admin dependency. All data access is tenant-scoped by JWT."""
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from dependencies import CurrentUser, get_db, require_admin
from domain.models import (
    Group,
    GroupActionFilter,
    GroupDocumentFilter,
    GroupUserFilter,
    SavedFilter,
    SavedFilterTag,
    Tag,
    User,
)
from auth.service import hash_password


def _parse_uuid(value: str) -> uuid.UUID | None:
    """Parse UUID from path/body; accept both 32-char hex and canonical (dashed) form."""
    if not value or not isinstance(value, str):
        return None
    value = value.strip()
    try:
        if len(value) == 32 and "-" not in value:
            return uuid.UUID(hex=value)
        return uuid.UUID(value)
    except (ValueError, TypeError):
        return None


def _normalize_uuid(value: str) -> str:
    """Normalize UUID string to canonical form for DB comparison."""
    u = _parse_uuid(value)
    return str(u) if u else value

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/me")
def admin_me(current_user: CurrentUser = Depends(require_admin)):
    """Current admin user info from JWT. Used to verify admin guard."""
    return {
        "sub": current_user.sub,
        "tenant_id": current_user.tenant_id,
        "role": current_user.role,
    }


# --- Users CRUD (tenant-scoped) ---


class UserCreateBody(BaseModel):
    email: str
    role: str  # admin | user
    password: str


class UserUpdateBody(BaseModel):
    email: str | None = None
    role: str | None = None
    password: str | None = None


def _user_to_response(user: User) -> dict:
    """Serialize user to JSON. IDs in canonical form (with hyphens) for consistent API contract."""
    ui = _parse_uuid(str(user.id)) if user.id else None
    ti = _parse_uuid(str(user.tenant_id)) if user.tenant_id else None
    return {
        "id": str(ui) if ui else str(user.id),
        "tenant_id": str(ti) if ti else str(user.tenant_id),
        "email": user.email,
        "role": user.role,
    }


@router.get("/users")
def list_users(
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List users of the current tenant."""
    users = db.query(User).filter(User.tenant_id == current_user.tenant_id).all()
    return [_user_to_response(u) for u in users]


@router.get("/users/{user_id}")
def get_user(
    user_id: str,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get user by id; 404 if not in current tenant."""
    uid_parsed = _parse_uuid(user_id)
    if uid_parsed is None:
        raise HTTPException(status_code=404, detail="User not found")
    # DB/driver may return UUID as hex or canonical; accept both
    uid_hex = uid_parsed.hex
    uid_canonical = str(uid_parsed)
    user = db.query(User).filter(or_(User.id == uid_hex, User.id == uid_canonical)).first()
    if not user or _normalize_uuid(str(user.tenant_id)) != _normalize_uuid(current_user.tenant_id):
        raise HTTPException(status_code=404, detail="User not found")
    return _user_to_response(user)


@router.post("/users", status_code=201)
def create_user(
    body: UserCreateBody,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create user in current tenant. tenant_id from JWT only."""
    existing = (
        db.query(User)
        .filter(User.tenant_id == current_user.tenant_id, User.email == body.email)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists in tenant")
    user = User(
        tenant_id=current_user.tenant_id,
        email=body.email,
        role=body.role,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_to_response(user)


@router.patch("/users/{user_id}")
def update_user(
    user_id: str,
    body: UserUpdateBody,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update user; 404 if not in current tenant."""
    uid_parsed = _parse_uuid(user_id)
    if uid_parsed is None:
        raise HTTPException(status_code=404, detail="User not found")
    uid_hex = uid_parsed.hex
    uid_canonical = str(uid_parsed)
    user = db.query(User).filter(or_(User.id == uid_hex, User.id == uid_canonical)).first()
    if not user or _normalize_uuid(str(user.tenant_id)) != _normalize_uuid(current_user.tenant_id):
        raise HTTPException(status_code=404, detail="User not found")
    if body.email is not None:
        user.email = body.email
    if body.role is not None:
        user.role = body.role
    if body.password is not None:
        user.password_hash = hash_password(body.password)
    db.commit()
    db.refresh(user)
    return _user_to_response(user)


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: str,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete user; 404 if not in current tenant."""
    uid_parsed = _parse_uuid(user_id)
    if uid_parsed is None:
        raise HTTPException(status_code=404, detail="User not found")
    uid_hex = uid_parsed.hex
    uid_canonical = str(uid_parsed)
    user = db.query(User).filter(or_(User.id == uid_hex, User.id == uid_canonical)).first()
    if not user or _normalize_uuid(str(user.tenant_id)) != _normalize_uuid(current_user.tenant_id):
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return None


# --- Tags CRUD (tenant-scoped) ---


class TagCreateBody(BaseModel):
    name: str


class TagUpdateBody(BaseModel):
    name: str | None = None


def _tag_to_response(tag: Tag) -> dict:
    """Serialize tag to JSON. IDs in canonical form (with hyphens)."""
    ui = _parse_uuid(str(tag.id)) if tag.id else None
    ti = _parse_uuid(str(tag.tenant_id)) if tag.tenant_id else None
    return {
        "id": str(ui) if ui else str(tag.id),
        "tenant_id": str(ti) if ti else str(tag.tenant_id),
        "name": tag.name,
    }


@router.get("/tags")
def list_tags(
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List tags of the current tenant."""
    tags = db.query(Tag).filter(Tag.tenant_id == current_user.tenant_id).all()
    return [_tag_to_response(t) for t in tags]


@router.get("/tags/{tag_id}")
def get_tag(
    tag_id: str,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get tag by id; 404 if not in current tenant."""
    uid_parsed = _parse_uuid(tag_id)
    if uid_parsed is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    uid_hex = uid_parsed.hex
    uid_canonical = str(uid_parsed)
    tag = db.query(Tag).filter(or_(Tag.id == uid_hex, Tag.id == uid_canonical)).first()
    if not tag or _normalize_uuid(str(tag.tenant_id)) != _normalize_uuid(current_user.tenant_id):
        raise HTTPException(status_code=404, detail="Tag not found")
    return _tag_to_response(tag)


@router.post("/tags", status_code=201)
def create_tag(
    body: TagCreateBody,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create tag in current tenant. tenant_id from JWT only. 409 if name already exists."""
    existing = (
        db.query(Tag)
        .filter(Tag.tenant_id == current_user.tenant_id, Tag.name == body.name)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Tag name already exists in tenant")
    tag = Tag(
        tenant_id=current_user.tenant_id,
        name=body.name,
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return _tag_to_response(tag)


@router.patch("/tags/{tag_id}")
def update_tag(
    tag_id: str,
    body: TagUpdateBody,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update tag; 404 if not in current tenant; 409 if new name duplicates in tenant."""
    uid_parsed = _parse_uuid(tag_id)
    if uid_parsed is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    uid_hex = uid_parsed.hex
    uid_canonical = str(uid_parsed)
    tag = db.query(Tag).filter(or_(Tag.id == uid_hex, Tag.id == uid_canonical)).first()
    if not tag or _normalize_uuid(str(tag.tenant_id)) != _normalize_uuid(current_user.tenant_id):
        raise HTTPException(status_code=404, detail="Tag not found")
    if body.name is not None:
        duplicate = (
            db.query(Tag)
            .filter(
                Tag.tenant_id == current_user.tenant_id,
                Tag.name == body.name,
                Tag.id != tag.id,
            )
            .first()
        )
        if duplicate:
            raise HTTPException(status_code=409, detail="Tag name already exists in tenant")
        tag.name = body.name
    db.commit()
    db.refresh(tag)
    return _tag_to_response(tag)


@router.delete("/tags/{tag_id}", status_code=204)
def delete_tag(
    tag_id: str,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete tag; 404 if not in current tenant."""
    uid_parsed = _parse_uuid(tag_id)
    if uid_parsed is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    uid_hex = uid_parsed.hex
    uid_canonical = str(uid_parsed)
    tag = db.query(Tag).filter(or_(Tag.id == uid_hex, Tag.id == uid_canonical)).first()
    if not tag or _normalize_uuid(str(tag.tenant_id)) != _normalize_uuid(current_user.tenant_id):
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.commit()
    return None


# --- Saved Filters CRUD (tenant-scoped) ---


class FilterCreateBody(BaseModel):
    name: str
    target_type: Literal["user", "action", "document"]
    tag_ids: list[uuid.UUID] = []


class FilterUpdateBody(BaseModel):
    name: str | None = None
    tag_ids: list[uuid.UUID] | None = None


def _get_filter_by_id(db: Session, filter_id: str, tenant_id: str) -> SavedFilter | None:
    """Return SavedFilter if exists and belongs to tenant; else None."""
    fid = _parse_uuid(filter_id)
    if fid is None:
        return None
    f_hex, f_canonical = fid.hex, str(fid)
    obj = db.query(SavedFilter).filter(
        or_(SavedFilter.id == f_hex, SavedFilter.id == f_canonical)
    ).first()
    if not obj or _normalize_uuid(str(obj.tenant_id)) != _normalize_uuid(tenant_id):
        return None
    return obj


def _filter_tag_ids(db: Session, filter_id: str) -> list[str]:
    """Return list of tag_id (canonical) for a saved filter."""
    rows = (
        db.query(SavedFilterTag.tag_id)
        .filter(SavedFilterTag.saved_filter_id == filter_id)
        .all()
    )
    return [str(_parse_uuid(r[0]) or r[0]) for r in rows]


def _filter_to_response(f: SavedFilter, tag_ids: list[str] | None = None, db: Session | None = None) -> dict:
    """Serialize SavedFilter to JSON; tag_ids from db if not provided."""
    if tag_ids is None and db is not None:
        tag_ids = _filter_tag_ids(db, f.id)
    elif tag_ids is None:
        tag_ids = []
    fi = _parse_uuid(str(f.id)) if f.id else None
    ti = _parse_uuid(str(f.tenant_id)) if f.tenant_id else None
    return {
        "id": str(fi) if fi else str(f.id),
        "tenant_id": str(ti) if ti else str(f.tenant_id),
        "target_type": f.target_type,
        "name": f.name,
        "tag_ids": tag_ids,
    }


def _validate_tag_ids_in_tenant(db: Session, tag_ids: list[uuid.UUID], tenant_id: str) -> None:
    """Raise 404 if any tag does not exist or is not in tenant."""
    for tid in tag_ids:
        t_hex, t_canonical = tid.hex, str(tid)
        tag = db.query(Tag).filter(or_(Tag.id == t_hex, Tag.id == t_canonical)).first()
        if not tag or _normalize_uuid(str(tag.tenant_id)) != _normalize_uuid(tenant_id):
            raise HTTPException(status_code=404, detail="Tag not found")


@router.get("/filters")
def list_filters(
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List saved filters of the current tenant."""
    filters = (
        db.query(SavedFilter)
        .filter(SavedFilter.tenant_id == current_user.tenant_id)
        .all()
    )
    return [_filter_to_response(f, db=db) for f in filters]


@router.get("/filters/{filter_id}")
def get_filter(
    filter_id: str,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get saved filter by id; 404 if not in current tenant. Response includes tag_ids."""
    f = _get_filter_by_id(db, filter_id, current_user.tenant_id)
    if not f:
        raise HTTPException(status_code=404, detail="Filter not found")
    return _filter_to_response(f, db=db)


@router.post("/filters", status_code=201)
def create_filter(
    body: FilterCreateBody,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create saved filter in current tenant. tag_ids must exist and belong to tenant; 404 if not."""
    _validate_tag_ids_in_tenant(db, body.tag_ids, current_user.tenant_id)
    f = SavedFilter(
        tenant_id=current_user.tenant_id,
        name=body.name,
        target_type=body.target_type,
    )
    db.add(f)
    db.commit()
    db.refresh(f)
    for tag_id in body.tag_ids:
        db.add(SavedFilterTag(saved_filter_id=f.id, tag_id=tag_id.hex))
    db.commit()
    return _filter_to_response(f, tag_ids=[str(t) for t in body.tag_ids], db=db)


@router.patch("/filters/{filter_id}")
def update_filter(
    filter_id: str,
    body: FilterUpdateBody,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update saved filter; 404 if not in current tenant. tag_ids must exist and belong to tenant."""
    f = _get_filter_by_id(db, filter_id, current_user.tenant_id)
    if not f:
        raise HTTPException(status_code=404, detail="Filter not found")
    if body.name is not None:
        f.name = body.name
    if body.tag_ids is not None:
        _validate_tag_ids_in_tenant(db, body.tag_ids, current_user.tenant_id)
        db.query(SavedFilterTag).filter(SavedFilterTag.saved_filter_id == f.id).delete()
        for tag_id in body.tag_ids:
            db.add(SavedFilterTag(saved_filter_id=f.id, tag_id=tag_id.hex))
    db.commit()
    db.refresh(f)
    return _filter_to_response(f, db=db)


@router.delete("/filters/{filter_id}", status_code=204)
def delete_filter(
    filter_id: str,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete saved filter; 404 if not in current tenant."""
    f = _get_filter_by_id(db, filter_id, current_user.tenant_id)
    if not f:
        raise HTTPException(status_code=404, detail="Filter not found")
    db.query(SavedFilterTag).filter(SavedFilterTag.saved_filter_id == f.id).delete()
    db.delete(f)
    db.commit()
    return None


# --- Groups CRUD (tenant-scoped) ---


class GroupCreateBody(BaseModel):
    name: str
    user_filter_ids: list[uuid.UUID] = []
    action_filter_ids: list[uuid.UUID] = []
    document_filter_ids: list[uuid.UUID] = []


class GroupUpdateBody(BaseModel):
    name: str | None = None
    user_filter_ids: list[uuid.UUID] | None = None
    action_filter_ids: list[uuid.UUID] | None = None
    document_filter_ids: list[uuid.UUID] | None = None


def _get_group_by_id(db: Session, group_id: str, tenant_id: str) -> Group | None:
    """Return Group if exists and belongs to tenant; else None."""
    gid = _parse_uuid(group_id)
    if gid is None:
        return None
    g_hex, g_canonical = gid.hex, str(gid)
    obj = db.query(Group).filter(or_(Group.id == g_hex, Group.id == g_canonical)).first()
    if not obj or _normalize_uuid(str(obj.tenant_id)) != _normalize_uuid(tenant_id):
        return None
    return obj


def _group_filter_ids(
    db: Session,
    group_id: str,
) -> tuple[list[str], list[str], list[str]]:
    """Return (user_filter_ids, action_filter_ids, document_filter_ids) in canonical form."""
    def ids_from_table(model, col):
        rows = db.query(col).filter(model.group_id == group_id).all()
        return [str(_parse_uuid(r[0]) or r[0]) for r in rows]
    uid_col = GroupUserFilter.saved_filter_id
    aid_col = GroupActionFilter.saved_filter_id
    did_col = GroupDocumentFilter.saved_filter_id
    uids = ids_from_table(GroupUserFilter, uid_col)
    aids = ids_from_table(GroupActionFilter, aid_col)
    dids = ids_from_table(GroupDocumentFilter, did_col)
    return (uids, aids, dids)


def _group_to_response(
    g: Group,
    user_filter_ids: list[str] | None = None,
    action_filter_ids: list[str] | None = None,
    document_filter_ids: list[str] | None = None,
    db: Session | None = None,
) -> dict:
    """Serialize Group to JSON; filter id lists from db if not provided."""
    if db is not None and user_filter_ids is None and action_filter_ids is None and document_filter_ids is None:
        uids, aids, dids = _group_filter_ids(db, g.id)
    else:
        uids = user_filter_ids or []
        aids = action_filter_ids or []
        dids = document_filter_ids or []
    gi = _parse_uuid(str(g.id)) if g.id else None
    ti = _parse_uuid(str(g.tenant_id)) if g.tenant_id else None
    return {
        "id": str(gi) if gi else str(g.id),
        "tenant_id": str(ti) if ti else str(g.tenant_id),
        "name": g.name,
        "user_filter_ids": uids,
        "action_filter_ids": aids,
        "document_filter_ids": dids,
    }


def _validate_saved_filter_ids_in_tenant(
    db: Session, filter_ids: list[uuid.UUID], tenant_id: str
) -> None:
    """Raise 404 if any saved filter does not exist or is not in tenant."""
    for fid in filter_ids:
        f = _get_filter_by_id(db, str(fid), tenant_id)
        if not f:
            raise HTTPException(status_code=404, detail="Filter not found")


@router.get("/groups")
def list_groups(
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List groups of the current tenant."""
    groups = (
        db.query(Group)
        .filter(Group.tenant_id == current_user.tenant_id)
        .all()
    )
    return [_group_to_response(g, db=db) for g in groups]


@router.get("/groups/{group_id}")
def get_group(
    group_id: str,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get group by id; 404 if not in current tenant. Response includes filter id lists."""
    g = _get_group_by_id(db, group_id, current_user.tenant_id)
    if not g:
        raise HTTPException(status_code=404, detail="Group not found")
    return _group_to_response(g, db=db)


@router.post("/groups", status_code=201)
def create_group(
    body: GroupCreateBody,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create group in current tenant. Saved filter ids must exist and belong to tenant; 404 if not."""
    _validate_saved_filter_ids_in_tenant(db, body.user_filter_ids, current_user.tenant_id)
    _validate_saved_filter_ids_in_tenant(db, body.action_filter_ids, current_user.tenant_id)
    _validate_saved_filter_ids_in_tenant(db, body.document_filter_ids, current_user.tenant_id)
    g = Group(tenant_id=current_user.tenant_id, name=body.name)
    db.add(g)
    db.commit()
    db.refresh(g)
    for fid in body.user_filter_ids:
        db.add(GroupUserFilter(group_id=g.id, saved_filter_id=fid.hex))
    for fid in body.action_filter_ids:
        db.add(GroupActionFilter(group_id=g.id, saved_filter_id=fid.hex))
    for fid in body.document_filter_ids:
        db.add(GroupDocumentFilter(group_id=g.id, saved_filter_id=fid.hex))
    db.commit()
    db.refresh(g)
    uids, aids, dids = _group_filter_ids(db, g.id)
    return _group_to_response(g, user_filter_ids=uids, action_filter_ids=aids, document_filter_ids=dids)


@router.patch("/groups/{group_id}")
def update_group(
    group_id: str,
    body: GroupUpdateBody,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update group name and/or filter lists; filters must exist and belong to tenant."""
    g = _get_group_by_id(db, group_id, current_user.tenant_id)
    if not g:
        raise HTTPException(status_code=404, detail="Group not found")
    if body.name is not None:
        g.name = body.name
    if body.user_filter_ids is not None:
        _validate_saved_filter_ids_in_tenant(db, body.user_filter_ids, current_user.tenant_id)
        db.query(GroupUserFilter).filter(GroupUserFilter.group_id == g.id).delete()
        for fid in body.user_filter_ids:
            db.add(GroupUserFilter(group_id=g.id, saved_filter_id=fid.hex))
    if body.action_filter_ids is not None:
        _validate_saved_filter_ids_in_tenant(db, body.action_filter_ids, current_user.tenant_id)
        db.query(GroupActionFilter).filter(GroupActionFilter.group_id == g.id).delete()
        for fid in body.action_filter_ids:
            db.add(GroupActionFilter(group_id=g.id, saved_filter_id=fid.hex))
    if body.document_filter_ids is not None:
        _validate_saved_filter_ids_in_tenant(db, body.document_filter_ids, current_user.tenant_id)
        db.query(GroupDocumentFilter).filter(GroupDocumentFilter.group_id == g.id).delete()
        for fid in body.document_filter_ids:
            db.add(GroupDocumentFilter(group_id=g.id, saved_filter_id=fid.hex))
    db.commit()
    db.refresh(g)
    return _group_to_response(g, db=db)


@router.delete("/groups/{group_id}", status_code=204)
def delete_group(
    group_id: str,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete group; 404 if not in current tenant."""
    g = _get_group_by_id(db, group_id, current_user.tenant_id)
    if not g:
        raise HTTPException(status_code=404, detail="Group not found")
    db.query(GroupUserFilter).filter(GroupUserFilter.group_id == g.id).delete()
    db.query(GroupActionFilter).filter(GroupActionFilter.group_id == g.id).delete()
    db.query(GroupDocumentFilter).filter(GroupDocumentFilter.group_id == g.id).delete()
    db.delete(g)
    db.commit()
    return None
