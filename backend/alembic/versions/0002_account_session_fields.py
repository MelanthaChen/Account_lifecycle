"""add account browser session fields

Revision ID: 0002_account_session_fields
Revises: 0001_initial_schema
Create Date: 2026-07-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_account_session_fields"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("accounts", sa.Column("session_path", sa.String(length=500), nullable=True))
    op.add_column("accounts", sa.Column("session_status", sa.String(length=40), nullable=True))
    op.add_column("accounts", sa.Column("last_login", sa.DateTime(timezone=True), nullable=True))
    op.add_column("accounts", sa.Column("last_validation", sa.DateTime(timezone=True), nullable=True))
    op.add_column("accounts", sa.Column("browser_profile", sa.String(length=160), nullable=True))
    op.add_column("accounts", sa.Column("provider", sa.String(length=80), nullable=True))


def downgrade() -> None:
    op.drop_column("accounts", "provider")
    op.drop_column("accounts", "browser_profile")
    op.drop_column("accounts", "last_validation")
    op.drop_column("accounts", "last_login")
    op.drop_column("accounts", "session_status")
    op.drop_column("accounts", "session_path")
