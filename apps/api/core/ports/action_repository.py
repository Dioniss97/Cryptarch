"""Port for Action persistence."""
from typing import Protocol

from core.domain.models import Action


class ActionRepository(Protocol):
    def list_by_tenant(
        self, tenant_id: str, connector_id: str | None = None
    ) -> list[Action]:
        ...

    def get_by_id(self, action_id: str, tenant_id: str) -> Action | None:
        ...

    def get_action_tag_ids(self, action_id: str) -> list[str]:
        ...

    def add(self, action: Action, tag_ids: list[str]) -> Action:
        ...

    def save(self, action: Action, tag_ids: list[str] | None) -> Action:
        ...

    def delete(self, action: Action) -> None:
        ...
