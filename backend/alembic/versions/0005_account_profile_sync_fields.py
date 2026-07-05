"""add account profile sync fields

Revision ID: 0005_profile_sync
Revises: 0004_remove_credentials
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_profile_sync"
down_revision: str | None = "0004_remove_credentials"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("accounts", sa.Column("display_name", sa.String(length=160), nullable=True))
    op.add_column("accounts", sa.Column("reddit_username", sa.String(length=120), nullable=True))
    op.add_column("accounts", sa.Column("avatar_url", sa.String(length=1000), nullable=True))
    op.add_column("accounts", sa.Column("karma_post", sa.Integer(), nullable=True))
    op.add_column("accounts", sa.Column("karma_comment", sa.Integer(), nullable=True))
    op.add_column("accounts", sa.Column("cake_day", sa.String(length=120), nullable=True))
    op.add_column("accounts", sa.Column("verified_email", sa.Boolean(), nullable=True))
    op.add_column("accounts", sa.Column("is_nsfw", sa.Boolean(), nullable=True))
    op.add_column("accounts", sa.Column("is_moderator", sa.Boolean(), nullable=True))
    op.add_column("accounts", sa.Column("is_gold", sa.Boolean(), nullable=True))
    op.add_column("accounts", sa.Column("last_profile_sync", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("accounts", "last_profile_sync")
    op.drop_column("accounts", "is_gold")
    op.drop_column("accounts", "is_moderator")
    op.drop_column("accounts", "is_nsfw")
    op.drop_column("accounts", "verified_email")
    op.drop_column("accounts", "cake_day")
    op.drop_column("accounts", "karma_comment")
    op.drop_column("accounts", "karma_post")
    op.drop_column("accounts", "avatar_url")
    op.drop_column("accounts", "reddit_username")
    op.drop_column("accounts", "display_name")
