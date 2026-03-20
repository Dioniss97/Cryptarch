"""Admin HTTP routes for Tags. Uses core.application.tag use cases and SqlAlchemyTagRepository."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from adapters.driven.persistence.tag_repository import SqlAlchemyTagRepository
from adapters.driving.schemas.tag import (
    TagCreateBody,
    TagUpdateBody,
    tag_to_response,
)
from core.application import tag as tag_use_cases
from core.application.tag import TagNameExistsError
from dependencies import CurrentUser, get_db, require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/tags")
def list_tags(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """List tags of the current tenant."""
    repo = SqlAlchemyTagRepository(db)
    tags = tag_use_cases.list_tags(current_user.tenant_id, repo)
    return [tag_to_response(t) for t in tags]


@router.get("/tags/{tag_id}")
def get_tag(
    tag_id: str,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Get tag by id; 404 if not in current tenant."""
    repo = SqlAlchemyTagRepository(db)
    tag = tag_use_cases.get_tag(tag_id, current_user.tenant_id, repo)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag_to_response(tag)


@router.post("/tags", status_code=status.HTTP_201_CREATED)
def create_tag(
    body: TagCreateBody,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Create tag in current tenant. tenant_id from JWT only. 409 if name already exists."""
    repo = SqlAlchemyTagRepository(db)
    try:
        tag = tag_use_cases.create_tag(
            current_user.tenant_id, body.name, repo
        )
        db.commit()
    except TagNameExistsError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tag name already exists in tenant",
        )
    return tag_to_response(tag)


@router.patch("/tags/{tag_id}")
def update_tag(
    tag_id: str,
    body: TagUpdateBody,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Update tag; 404 if not in current tenant; 409 if new name duplicates in tenant."""
    repo = SqlAlchemyTagRepository(db)
    try:
        tag = tag_use_cases.update_tag(
            tag_id, current_user.tenant_id, body.name, repo
        )
        if tag is None:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
        db.commit()
    except TagNameExistsError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tag name already exists in tenant",
        )
    return tag_to_response(tag)


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: str,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Delete tag; 404 if not in current tenant."""
    repo = SqlAlchemyTagRepository(db)
    deleted = tag_use_cases.delete_tag(tag_id, current_user.tenant_id, repo)
    if not deleted:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    db.commit()
    return None
