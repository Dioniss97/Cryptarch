"""sprint01_domain_tables

Revision ID: 001
Revises:
Create Date: Sprint 01 domain schema

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(255), nullable=True),
    )

    op.create_table(
        "tags",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
    )
    op.create_index("ix_tags_tenant_id", "tags", ["tenant_id"], unique=False)
    op.create_unique_constraint("uq_tags_tenant_name", "tags", ["tenant_id", "name"])

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"], unique=False)
    op.create_unique_constraint("uq_users_tenant_email", "users", ["tenant_id", "email"])

    op.create_table(
        "user_tags",
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("tag_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("tags.id"), primary_key=True),
    )

    op.create_table(
        "saved_filters",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("target_type", sa.String(32), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
    )
    op.create_index("ix_saved_filters_tenant_id", "saved_filters", ["tenant_id"], unique=False)

    op.create_table(
        "saved_filter_tags",
        sa.Column("saved_filter_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("saved_filters.id"), primary_key=True),
        sa.Column("tag_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("tags.id"), primary_key=True),
    )

    op.create_table(
        "groups",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
    )
    op.create_index("ix_groups_tenant_id", "groups", ["tenant_id"], unique=False)

    op.create_table(
        "group_user_filters",
        sa.Column("group_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("groups.id"), primary_key=True),
        sa.Column("saved_filter_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("saved_filters.id"), primary_key=True),
    )

    op.create_table(
        "group_action_filters",
        sa.Column("group_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("groups.id"), primary_key=True),
        sa.Column("saved_filter_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("saved_filters.id"), primary_key=True),
    )

    op.create_table(
        "group_document_filters",
        sa.Column("group_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("groups.id"), primary_key=True),
        sa.Column("saved_filter_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("saved_filters.id"), primary_key=True),
    )

    op.create_table(
        "connectors",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("base_url", sa.String(2048), nullable=False),
        sa.Column("auth_config", postgresql.JSONB(), nullable=True),
    )
    op.create_index("ix_connectors_tenant_id", "connectors", ["tenant_id"], unique=False)

    op.create_table(
        "actions",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("connector_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("connectors.id"), nullable=False),
        sa.Column("method", sa.String(16), nullable=False),
        sa.Column("path", sa.String(2048), nullable=False),
        sa.Column("request_config", postgresql.JSONB(), nullable=True),
        sa.Column("name", sa.String(255), nullable=True),
    )
    op.create_index("ix_actions_tenant_id", "actions", ["tenant_id"], unique=False)

    op.create_table(
        "action_tags",
        sa.Column("action_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("actions.id"), primary_key=True),
        sa.Column("tag_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("tags.id"), primary_key=True),
    )

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("file_path", sa.String(2048), nullable=True),
    )
    op.create_index("ix_documents_tenant_id", "documents", ["tenant_id"], unique=False)

    op.create_table(
        "document_tags",
        sa.Column("document_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("documents.id"), primary_key=True),
        sa.Column("tag_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("tags.id"), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("document_tags")
    op.drop_table("documents")
    op.drop_table("action_tags")
    op.drop_table("actions")
    op.drop_table("connectors")
    op.drop_table("group_document_filters")
    op.drop_table("group_action_filters")
    op.drop_table("group_user_filters")
    op.drop_table("groups")
    op.drop_table("saved_filter_tags")
    op.drop_table("saved_filters")
    op.drop_table("user_tags")
    op.drop_table("users")
    op.drop_table("tags")
    op.drop_table("tenants")
