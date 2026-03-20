"""Tag use cases. No SQLAlchemy; orchestrate via TagRepository port."""
from core.domain.models import Tag
from core.ports.tag_repository import TagRepository


class TagNameExistsError(Exception):
    """Raised when create/update would duplicate tag name in tenant."""


def list_tags(tenant_id: str, repo: TagRepository) -> list[Tag]:
    """List all tags for the tenant."""
    return repo.list_by_tenant(tenant_id)


def get_tag(tag_id: str, tenant_id: str, repo: TagRepository) -> Tag | None:
    """Get tag by id (hex or canonical) and tenant; None if not found."""
    return repo.get_by_id(tag_id, tenant_id)


def create_tag(tenant_id: str, name: str, repo: TagRepository) -> Tag:
    """Create tag in tenant. Raises TagNameExistsError if name already exists."""
    existing = repo.get_by_name(tenant_id, name)
    if existing:
        raise TagNameExistsError()
    tag = Tag(tenant_id=tenant_id, name=name)
    return repo.add(tag)


def update_tag(
    tag_id: str, tenant_id: str, name: str | None, repo: TagRepository
) -> Tag | None:
    """Update tag; None if not found. Raises TagNameExistsError if new name duplicates."""
    tag = repo.get_by_id(tag_id, tenant_id)
    if not tag:
        return None
    if name is not None:
        duplicate = repo.get_by_name(tenant_id, name)
        if duplicate and str(duplicate.id) != str(tag.id):
            raise TagNameExistsError()
        tag.name = name
        return repo.save(tag)
    return tag


def delete_tag(tag_id: str, tenant_id: str, repo: TagRepository) -> bool:
    """Delete tag; True if deleted, False if not found."""
    tag = repo.get_by_id(tag_id, tenant_id)
    if not tag:
        return False
    repo.delete(tag)
    return True
