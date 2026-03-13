"""sprint025_action_schema_and_user_preferences

Revision ID: 003
Revises: 002
Create Date: Sprint 02.5 - action input schema and user preferences

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "003"
down_revision: Union[str, Sequence[str], None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "actions",
        sa.Column("input_schema_json", postgresql.JSONB(), nullable=True),
    )
    op.add_column(
        "actions",
        sa.Column("input_schema_version", sa.Integer(), nullable=True, server_default="1"),
    )

    op.create_table(
        "user_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("language", sa.String(32), nullable=False, server_default="es"),
        sa.Column("theme", sa.String(32), nullable=False, server_default="system"),
        sa.Column(
            "table_density", sa.String(32), nullable=False, server_default="comfortable"
        ),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.UniqueConstraint(
            "tenant_id", "user_id", name="uq_user_preferences_tenant_user"
        ),
    )
    op.create_index(
        "ix_user_preferences_tenant_id", "user_preferences", ["tenant_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_user_preferences_tenant_id", table_name="user_preferences")
    op.drop_table("user_preferences")
    op.drop_column("actions", "input_schema_version")
    op.drop_column("actions", "input_schema_json")
