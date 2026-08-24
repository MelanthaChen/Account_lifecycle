"""add profile sync automation job type

Revision ID: 0018_profile_sync_job_type
Revises: 0017_session_automation_jobs
Create Date: 2026-08-24
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0018_profile_sync_job_type"
down_revision: str | None = "0017_session_automation_jobs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE automation_job_type ADD VALUE IF NOT EXISTS 'PROFILE_SYNC'")


def downgrade() -> None:
    pass
