"""initial account management schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    account_status = postgresql.ENUM(
        "active",
        "paused",
        "error",
        "archived",
        name="account_status",
        create_type=False,
    )
    platform = postgresql.ENUM("reddit", name="platform", create_type=False)
    account_status.create(op.get_bind(), checkfirst=True)
    platform.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nickname", sa.String(length=120), nullable=False),
        sa.Column("platform", platform, nullable=False),
        sa.Column("username", sa.String(length=120), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", account_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_sync", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("platform", "username", name="uq_accounts_platform_username"),
    )
    op.create_index(op.f("ix_accounts_username"), "accounts", ["username"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_accounts_username"), table_name="accounts")
    op.drop_table("accounts")
    sa.Enum(name="platform").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="account_status").drop(op.get_bind(), checkfirst=True)
