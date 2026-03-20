"""Port for Group persistence."""
from typing import Protocol

from core.domain.models import Group


class GroupRepository(Protocol):
    def list_by_tenant(self, tenant_id: str) -> list[Group]:
        ...

    def get_by_id(self, group_id: str, tenant_id: str) -> Group | None:
        ...

    def get_group_filter_ids(
        self, group_id: str
    ) -> tuple[list[str], list[str], list[str]]:
        """Return (user_filter_ids, action_filter_ids, document_filter_ids)."""
        ...

    def add(
        self,
        group: Group,
        user_filter_ids: list[str],
        action_filter_ids: list[str],
        document_filter_ids: list[str],
    ) -> Group:
        ...

    def save(
        self,
        group: Group,
        user_filter_ids: list[str] | None,
        action_filter_ids: list[str] | None,
        document_filter_ids: list[str] | None,
    ) -> Group:
        ...

    def delete(self, group: Group) -> None:
        ...
