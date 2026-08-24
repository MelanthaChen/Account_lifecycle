"""add comment automation job type

Revision ID: 0020_comment_job_type
Revises: 0019_upvote_job_type
Create Date: 2026-08-24
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0020_comment_job_type"
down_revision: str | None = "0019_upvote_job_type"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE automation_job_type ADD VALUE IF NOT EXISTS 'COMMENT'")


def downgrade() -> None:
    pass
