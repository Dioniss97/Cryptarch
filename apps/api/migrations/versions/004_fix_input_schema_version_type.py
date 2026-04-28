"""fix_input_schema_version_type_to_varchar128

Revision ID: 004
Revises: 003
Create Date: Alinear BDs legadas donde `input_schema_version` quedó como INTEGER
con el tipo correcto VARCHAR(128) definido en la migración 003.

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: str | Sequence[str] | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "actions",
        "input_schema_version",
        existing_type=sa.Integer(),
        type_=sa.String(length=128),
        existing_nullable=True,
        postgresql_using="input_schema_version::text",
    )


def downgrade() -> None:
    op.alter_column(
        "actions",
        "input_schema_version",
        existing_type=sa.String(length=128),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="NULLIF(input_schema_version, '')::integer",
    )
