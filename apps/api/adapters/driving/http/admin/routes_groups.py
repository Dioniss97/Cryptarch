"""Admin Groups CRUD. Tenant-scoped; requires admin role."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from adapters.driven.persistence.group_repository import (
    FilterNotFoundInTenantError,
    GroupRepositoryImpl,
)
from adapters.driving.schemas.group import (
    GroupCreateBody,
    GroupUpdateBody,
    group_to_response,
)
from core.application import group as group_use_cases
from dependencies import CurrentUser, get_db, require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


def _repo(session: Session) -> GroupRepositoryImpl:
    return GroupRepositoryImpl(session)


@router.get("/groups")
def list_groups(
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List groups of the current tenant."""
    repo = _repo(db)
    groups = group_use_cases.list_groups(current_user.tenant_id, repo)
    return [
        group_to_response(g, *repo.get_group_filter_ids(g.id))
        for g in groups
    ]


@router.get("/groups/{group_id}")
def get_group(
    group_id: str,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get group by id; 404 if not in current tenant. Response includes filter id lists."""
    repo = _repo(db)
    g = group_use_cases.get_group(group_id, current_user.tenant_id, repo)
    if not g:
        raise HTTPException(status_code=404, detail="Group not found")
    uids, aids, dids = repo.get_group_filter_ids(g.id)
    return group_to_response(g, uids, aids, dids)


@router.post("/groups", status_code=201)
def create_group(
    body: GroupCreateBody,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create group in current tenant. Saved filter ids must exist and belong to tenant; 404 if not."""
    repo = _repo(db)
    uids = [str(x) for x in body.user_filter_ids]
    aids = [str(x) for x in body.action_filter_ids]
    dids = [str(x) for x in body.document_filter_ids]
    try:
        g = group_use_cases.create_group(
            current_user.tenant_id,
            body.name,
            uids,
            aids,
            dids,
            repo,
        )
        db.commit()
    except FilterNotFoundInTenantError:
        db.rollback()
        raise HTTPException(status_code=404, detail="Filter not found")
    uids_out, aids_out, dids_out = repo.get_group_filter_ids(g.id)
    return group_to_response(g, uids_out, aids_out, dids_out)


@router.patch("/groups/{group_id}")
def update_group(
    group_id: str,
    body: GroupUpdateBody,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update group name and/or filter lists; filters must exist and belong to tenant."""
    repo = _repo(db)
    uids = [str(x) for x in body.user_filter_ids] if body.user_filter_ids is not None else None
    aids = [str(x) for x in body.action_filter_ids] if body.action_filter_ids is not None else None
    dids = [str(x) for x in body.document_filter_ids] if body.document_filter_ids is not None else None
    try:
        g = group_use_cases.update_group(
            group_id,
            current_user.tenant_id,
            repo,
            name=body.name,
            user_filter_ids=uids,
            action_filter_ids=aids,
            document_filter_ids=dids,
        )
        if not g:
            db.rollback()
            raise HTTPException(status_code=404, detail="Group not found")
        db.commit()
    except FilterNotFoundInTenantError:
        db.rollback()
        raise HTTPException(status_code=404, detail="Filter not found")
    uids_out, aids_out, dids_out = repo.get_group_filter_ids(g.id)
    return group_to_response(g, uids_out, aids_out, dids_out)


@router.delete("/groups/{group_id}", status_code=204)
def delete_group(
    group_id: str,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete group; 404 if not in current tenant."""
    repo = _repo(db)
    deleted = group_use_cases.delete_group(group_id, current_user.tenant_id, repo)
    if not deleted:
        db.rollback()
        raise HTTPException(status_code=404, detail="Group not found")
    db.commit()
    return None
