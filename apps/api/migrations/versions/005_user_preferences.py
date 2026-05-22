"""user_preferences table

Revision ID: 005
Revises: 004
Create Date: User preferences (theme, language, table_density, metadata)

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "005"
down_revision: str | Sequence[str] | None = "004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
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
        sa.Column("theme", sa.String(32), nullable=False, server_default="system"),
        sa.Column("language", sa.String(32), nullable=False, server_default="es"),
        sa.Column(
            "table_density",
            sa.String(32),
            nullable=False,
            server_default="comfortable",
        ),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
    )
    op.create_index(
        "ix_user_preferences_tenant_id", "user_preferences", ["tenant_id"], unique=False
    )
    op.create_unique_constraint(
        "uq_user_preferences_tenant_user",
        "user_preferences",
        ["tenant_id", "user_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_user_preferences_tenant_user", "user_preferences", type_="unique"
    )
    op.drop_index("ix_user_preferences_tenant_id", table_name="user_preferences")
    op.drop_table("user_preferences")
