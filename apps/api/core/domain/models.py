"""Pure domain entities (no SQLAlchemy).

Tags are metadata only; permissions via saved filters + groups.
Every entity is tenant-scoped.
"""
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Tenant:
    id: str
    name: Optional[str] = None


@dataclass
class Tag:
    tenant_id: str
    name: str
    id: str | None = None


@dataclass
class User:
    tenant_id: str
    email: str
    role: str  # admin | user
    password_hash: Optional[str] = None
    id: str | None = None


@dataclass
class SavedFilter:
    tenant_id: str
    target_type: str  # user | action | document
    name: str
    id: str | None = None


@dataclass
class Group:
    tenant_id: str
    name: str
    id: str | None = None


@dataclass
class Connector:
    tenant_id: str
    base_url: str
    auth_config: Optional[dict[str, Any]] = None
    id: str | None = None


@dataclass
class Integration(Connector):
    """Transitional semantic alias for Connector."""


@dataclass
class Action:
    tenant_id: str
    connector_id: str
    method: str
    path: str
    name: Optional[str] = None
    request_config: Optional[dict[str, Any]] = None
    id: str | None = None


@dataclass
class IntegrationAction(Action):
    """Transitional semantic alias for Action with integration terminology."""

    @property
    def integration_id(self) -> str:
        return self.connector_id

    @integration_id.setter
    def integration_id(self, value: str) -> None:
        self.connector_id = value


@dataclass
class Document:
    tenant_id: str
    status: str  # queued | processing | indexed | error
    file_path: Optional[str] = None
    id: str | None = None

