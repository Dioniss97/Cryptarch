"""Port for User persistence."""
from typing import Protocol

from core.domain.models import User


class UserRepository(Protocol):
    def list_by_tenant(self, tenant_id: str) -> list[User]:
        ...

    def get_by_id(self, user_id: str, tenant_id: str) -> User | None:
        ...

    def get_by_email(self, tenant_id: str, email: str) -> User | None:
        ...

    def add(self, user: User) -> User:
        ...

    def save(self, user: User) -> User:
        ...

    def delete(self, user: User) -> None:
        ...
