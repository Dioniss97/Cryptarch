"""Port for Connector persistence.

Integration is a transitional semantic alias over Connector.
"""
from typing import Any, Protocol

from core.domain.models import Connector


class ConnectorRepository(Protocol):
    def list_by_tenant(self, tenant_id: str) -> list[Connector]:
        ...

    def get_by_id(self, connector_id: str, tenant_id: str) -> Connector | None:
        ...

    def add(self, connector: Connector) -> Connector:
        ...

    def save(self, connector: Connector) -> Connector:
        ...

    def delete(self, connector: Connector) -> None:
        ...

    def has_actions(self, connector_id: str) -> bool:
        ...


# Transitional semantic alias for Sprint 02.5 task-08a.
# Keeps existing implementations untouched while enabling
# integration-centric naming in newer use cases.
IntegrationRepository = ConnectorRepository
