"""add comment engine campaign configuration

Revision ID: 0014_comment_engine
Revises: 0013_scheduler_engine
Create Date: 2026-08-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0014_comment_engine"
down_revision: str | None = "0013_scheduler_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("campaigns", sa.Column("comment_text", sa.Text(), nullable=True))
    op.execute("ALTER TYPE workflow_action_type ADD VALUE IF NOT EXISTS 'COMMENT'")


def downgrade() -> None:
    op.drop_column("campaigns", "comment_text")
