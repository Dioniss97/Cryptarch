"""Port for Document persistence."""
from typing import Protocol

from core.domain.models import Document


class DocumentRepository(Protocol):
    def list_by_tenant(self, tenant_id: str) -> list[Document]:
        ...

    def get_by_id(self, document_id: str, tenant_id: str) -> Document | None:
        ...

    def get_document_tag_ids(self, document_id: str) -> list[str]:
        ...

    def add(self, document: Document, tag_ids: list[str]) -> Document:
        ...

    def save(self, document: Document, tag_ids: list[str] | None) -> Document:
        ...

    def delete(self, document: Document) -> None:
        ...
