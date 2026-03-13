"""Port for Tag persistence."""
from typing import Protocol

from core.domain.models import Tag


class TagRepository(Protocol):
    def list_by_tenant(self, tenant_id: str) -> list[Tag]:
        ...

    def get_by_id(self, tag_id: str, tenant_id: str) -> Tag | None:
        ...

    def get_by_name(self, tenant_id: str, name: str) -> Tag | None:
        ...

    def add(self, tag: Tag) -> Tag:
        ...

    def save(self, tag: Tag) -> Tag:
        ...

    def delete(self, tag: Tag) -> None:
        ...
