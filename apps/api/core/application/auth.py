"""Auth use case: login. Depends only on core.ports; no JWT, no config."""
from core.domain.models import User
from core.ports.password_hasher import PasswordHasher
from core.ports.user_repository import UserRepository


def login(
    tenant_id: str,
    email: str,
    password: str,
    user_repo: UserRepository,
    password_hasher: PasswordHasher,
) -> User | None:
    """
    Look up user by tenant_id and email; verify password.
    Returns User if valid, None otherwise.
    """
    user = user_repo.get_by_email(tenant_id, email)
    if not user or not user.password_hash:
        return None
    if not password_hasher.verify(password, user.password_hash):
        return None
    return user
