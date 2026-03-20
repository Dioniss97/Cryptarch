"""Admin HTTP routes for Documents. Uses core.application.document and DocumentRepository + TagRepository."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from adapters.driven.persistence.document_repository import SqlAlchemyDocumentRepository
from adapters.driven.persistence.tag_repository import SqlAlchemyTagRepository
from adapters.driving.schemas.document import (
    DocumentCreateBody,
    DocumentUpdateBody,
    document_to_response,
)
from core.application import document as document_use_cases
from core.application.document import TagNotFoundError
from dependencies import CurrentUser, get_db, require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


def _tag_ids_to_str(tag_ids: list) -> list[str]:
    """Convert list of UUID to canonical string list."""
    return [str(t) for t in tag_ids]


@router.get("/documents")
def list_documents(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """List documents of the current tenant. Response includes tag_ids."""
    repo = SqlAlchemyDocumentRepository(db)
    docs = document_use_cases.list_documents(current_user.tenant_id, repo)
    return [
        document_to_response(d, tag_ids=repo.get_document_tag_ids(d.id))
        for d in docs
    ]


@router.get("/documents/{document_id}")
def get_document(
    document_id: str,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Get document by id; 404 if not in current tenant. Response includes tag_ids."""
    repo = SqlAlchemyDocumentRepository(db)
    doc = document_use_cases.get_document(
        document_id, current_user.tenant_id, repo
    )
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    tag_ids = repo.get_document_tag_ids(doc.id)
    return document_to_response(doc, tag_ids=tag_ids)


@router.post("/documents", status_code=status.HTTP_201_CREATED)
def create_document(
    body: DocumentCreateBody,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Create document in current tenant. tag_ids must exist and belong to tenant; 404 if not."""
    repo = SqlAlchemyDocumentRepository(db)
    tag_repo = SqlAlchemyTagRepository(db)
    tag_ids_str = _tag_ids_to_str(body.tag_ids)
    try:
        doc = document_use_cases.create_document(
            current_user.tenant_id,
            body.status,
            body.file_path,
            tag_ids_str,
            repo,
            tag_repo,
        )
        db.commit()
    except TagNotFoundError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
    return document_to_response(doc, tag_ids=tag_ids_str)


@router.patch("/documents/{document_id}")
def update_document(
    document_id: str,
    body: DocumentUpdateBody,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Update document; 404 if not in current tenant. tag_ids must exist and belong to tenant."""
    repo = SqlAlchemyDocumentRepository(db)
    tag_repo = SqlAlchemyTagRepository(db)
    tag_ids_str = _tag_ids_to_str(body.tag_ids) if body.tag_ids is not None else None
    try:
        doc = document_use_cases.update_document(
            document_id,
            current_user.tenant_id,
            body.status,
            body.file_path,
            tag_ids_str,
            repo,
            tag_repo,
        )
        db.commit()
    except TagNotFoundError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
    if doc is None:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    tag_ids = repo.get_document_tag_ids(doc.id)
    return document_to_response(doc, tag_ids=tag_ids)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Delete document; 404 if not in current tenant."""
    repo = SqlAlchemyDocumentRepository(db)
    deleted = document_use_cases.delete_document(
        document_id, current_user.tenant_id, repo
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    db.commit()
    return None
