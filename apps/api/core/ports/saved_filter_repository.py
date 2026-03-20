"""Port for SavedFilter persistence."""
from typing import Protocol

from core.domain.models import SavedFilter


class SavedFilterRepository(Protocol):
    def list_by_tenant(self, tenant_id: str) -> list[SavedFilter]:
        ...

    def get_by_id(self, filter_id: str, tenant_id: str) -> SavedFilter | None:
        ...

    def get_filter_tag_ids(self, filter_id: str) -> list[str]:
        ...

    def add(self, saved_filter: SavedFilter, tag_ids: list[str]) -> SavedFilter:
        ...

    def save(self, saved_filter: SavedFilter, tag_ids: list[str] | None) -> SavedFilter:
        ...

    def delete(self, saved_filter: SavedFilter) -> None:
        ...
