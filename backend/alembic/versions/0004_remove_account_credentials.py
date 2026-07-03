"""remove account credential fields

Revision ID: 0004_remove_credentials
Revises: 0003_browser_identity
Create Date: 2026-07-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_remove_credentials"
down_revision: str | None = "0003_browser_identity"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("accounts", "auto_login")
    op.drop_column("accounts", "remember_credentials")
    op.drop_column("accounts", "saved_password")
    op.drop_column("accounts", "saved_username")


def downgrade() -> None:
    op.add_column("accounts", sa.Column("saved_username", sa.String(length=160), nullable=True))
    op.add_column("accounts", sa.Column("saved_password", sa.String(length=500), nullable=True))
    op.add_column(
        "accounts",
        sa.Column("remember_credentials", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column(
        "accounts",
        sa.Column("auto_login", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.alter_column("accounts", "remember_credentials", server_default=None)
    op.alter_column("accounts", "auto_login", server_default=None)
