"""User use cases. Depend only on core.ports; no adapters or sqlalchemy."""
from core.domain.models import User
from core.ports.password_hasher import PasswordHasher
from core.ports.user_repository import UserRepository


def list_users(tenant_id: str, repo: UserRepository) -> list[User]:
    """List all users for the tenant."""
    return repo.list_by_tenant(tenant_id)


def get_user(user_id: str, tenant_id: str, repo: UserRepository) -> User | None:
    """Get user by id (hex or canonical uuid); None if not found or wrong tenant."""
    return repo.get_by_id(user_id, tenant_id)


def create_user(
    tenant_id: str,
    email: str,
    role: str,
    password: str,
    repo: UserRepository,
    password_hasher: PasswordHasher,
) -> User:
    """Create user in tenant. Hashes password via PasswordHasher. Raises ValueError if email already exists."""
    existing = repo.get_by_email(tenant_id, email)
    if existing is not None:
        raise ValueError("Email already exists in tenant")
    user = User(
        id="",  # will be set by repository
        tenant_id=tenant_id,
        email=email,
        role=role,
        password_hash=password_hasher.hash(password),
    )
    return repo.add(user)


def update_user(
    user_id: str,
    tenant_id: str,
    repo: UserRepository,
    *,
    email: str | None = None,
    role: str | None = None,
    password: str | None = None,
    password_hasher: PasswordHasher | None = None,
) -> User | None:
    """Update user; returns updated user or None if not found."""
    user = repo.get_by_id(user_id, tenant_id)
    if user is None:
        return None
    if email is not None:
        user.email = email
    if role is not None:
        user.role = role
    if password is not None and password_hasher is not None:
        user.password_hash = password_hasher.hash(password)
    return repo.save(user)


def delete_user(user_id: str, tenant_id: str, repo: UserRepository) -> bool:
    """Delete user; returns True if deleted, False if not found."""
    user = repo.get_by_id(user_id, tenant_id)
    if user is None:
        return False
    repo.delete(user)
    return True
