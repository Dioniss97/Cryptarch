"""ORM facade for legacy imports.

This module exposes SQLAlchemy ORM models and ``Base`` for use by
Alembic migrations and tests that operate directly on the database.
Domain entities live in ``core.domain.models`` as pure dataclasses.
"""
from adapters.driven.persistence.models import (  # type: ignore[F401]
    ActionOrm,
    ActionTagOrm,
    Base,
    ConnectorOrm,
    DocumentOrm,
    DocumentTagOrm,
    GroupActionFilterOrm,
    GroupDocumentFilterOrm,
    GroupOrm,
    GroupUserFilterOrm,
    SavedFilterOrm,
    SavedFilterTagOrm,
    TagOrm,
    TenantOrm,
    UserOrm,
    UserPreferenceOrm,
    UserTagOrm,
)

# Re-export with legacy names so existing imports keep working.
Action = ActionOrm
ActionTag = ActionTagOrm
Connector = ConnectorOrm
Integration = ConnectorOrm
IntegrationAction = ActionOrm
Document = DocumentOrm
DocumentTag = DocumentTagOrm
Group = GroupOrm
GroupActionFilter = GroupActionFilterOrm
GroupDocumentFilter = GroupDocumentFilterOrm
GroupUserFilter = GroupUserFilterOrm
SavedFilter = SavedFilterOrm
SavedFilterTag = SavedFilterTagOrm
Tag = TagOrm
Tenant = TenantOrm
User = UserOrm
UserPreference = UserPreferenceOrm
UserTag = UserTagOrm

__all__ = [
    "Action",
    "ActionTag",
    "Base",
    "Connector",
    "Integration",
    "IntegrationAction",
    "Document",
    "DocumentTag",
    "Group",
    "GroupActionFilter",
    "GroupDocumentFilter",
    "GroupUserFilter",
    "SavedFilter",
    "SavedFilterTag",
    "Tag",
    "Tenant",
    "User",
    "UserPreference",
    "UserTag",
]
