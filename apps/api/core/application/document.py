"""Document use cases. Orchestrate DocumentRepository and TagRepository (for tag_ids validation).
No Session or DB in this module; ports are injected.
"""
from core.domain.models import Document
from core.ports.document_repository import DocumentRepository
from core.ports.tag_repository import TagRepository


class DocumentNotFoundError(Exception):
    """Raised when a document does not exist or does not belong to the tenant."""


class TagNotFoundError(Exception):
    """Raised when one or more tag_ids do not exist or do not belong to the tenant."""


def _validate_tag_ids_in_tenant(
    tag_ids: list[str],
    tenant_id: str,
    tag_repo: TagRepository,
) -> None:
    """Raise TagNotFoundError if any tag_id is not found or not in tenant."""
    for tag_id in tag_ids:
        tag = tag_repo.get_by_id(tag_id, tenant_id)
        if not tag:
            raise TagNotFoundError("Tag not found")


def list_documents(
    tenant_id: str,
    repo: DocumentRepository,
) -> list[Document]:
    """List all documents for the tenant."""
    return repo.list_by_tenant(tenant_id)


def get_document(
    document_id: str,
    tenant_id: str,
    repo: DocumentRepository,
) -> Document | None:
    """Get document by id; None if not found or not in tenant."""
    return repo.get_by_id(document_id, tenant_id)


def create_document(
    tenant_id: str,
    status: str,
    file_path: str | None,
    tag_ids: list[str],
    repo: DocumentRepository,
    tag_repo: TagRepository,
) -> Document:
    """Create document in tenant. Raises TagNotFoundError if any tag_id is not in tenant."""
    if tag_ids:
        _validate_tag_ids_in_tenant(tag_ids, tenant_id, tag_repo)
    doc = Document(
        tenant_id=tenant_id,
        status=status,
        file_path=file_path,
    )
    return repo.add(doc, tag_ids)


def update_document(
    document_id: str,
    tenant_id: str,
    status: str | None,
    file_path: str | None,
    tag_ids: list[str] | None,
    repo: DocumentRepository,
    tag_repo: TagRepository,
) -> Document | None:
    """Update document. None if not found. Raises TagNotFoundError if tag_ids invalid."""
    doc = repo.get_by_id(document_id, tenant_id)
    if not doc:
        return None
    if tag_ids is not None:
        _validate_tag_ids_in_tenant(tag_ids, tenant_id, tag_repo)
    if status is not None:
        doc.status = status
    if file_path is not None:
        doc.file_path = file_path
    return repo.save(doc, tag_ids)


def delete_document(
    document_id: str,
    tenant_id: str,
    repo: DocumentRepository,
) -> bool:
    """Delete document; True if deleted, False if not found."""
    doc = repo.get_by_id(document_id, tenant_id)
    if not doc:
        return False
    repo.delete(doc)
    return True
