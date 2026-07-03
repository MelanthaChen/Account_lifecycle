"""add account browser identity fields

Revision ID: 0003_browser_identity
Revises: 0002_account_session_fields
Create Date: 2026-07-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_browser_identity"
down_revision: str | None = "0002_account_session_fields"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("accounts", sa.Column("browser_profile_path", sa.String(length=500), nullable=True))
    op.add_column("accounts", sa.Column("storage_directory", sa.String(length=500), nullable=True))
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
    op.add_column(
        "accounts",
        sa.Column("launch_visible_browser", sa.Boolean(), server_default=sa.true(), nullable=False),
    )
    op.alter_column("accounts", "remember_credentials", server_default=None)
    op.alter_column("accounts", "auto_login", server_default=None)
    op.alter_column("accounts", "launch_visible_browser", server_default=None)


def downgrade() -> None:
    op.drop_column("accounts", "launch_visible_browser")
    op.drop_column("accounts", "auto_login")
    op.drop_column("accounts", "remember_credentials")
    op.drop_column("accounts", "saved_password")
    op.drop_column("accounts", "saved_username")
    op.drop_column("accounts", "storage_directory")
    op.drop_column("accounts", "browser_profile_path")
