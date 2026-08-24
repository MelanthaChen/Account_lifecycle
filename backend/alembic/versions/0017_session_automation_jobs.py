"""add session automation job types

Revision ID: 0017_session_automation_jobs
Revises: 0016_remote_agent_heartbeat
Create Date: 2026-08-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0017_session_automation_jobs"
down_revision: str | None = "0016_remote_agent_heartbeat"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    job_type = sa.Enum(
        "WORKFLOW",
        "SESSION_LOGIN",
        "SESSION_VALIDATE",
        "SESSION_REFRESH",
        "SESSION_DELETE",
        "OPEN_BROWSER",
        "OPEN_HOME",
        "PROFILE_SYNC",
        name="automation_job_type",
    )
    job_type.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "automation_jobs",
        sa.Column(
            "job_type",
            postgresql.ENUM(name="automation_job_type", create_type=False),
            server_default="WORKFLOW",
            nullable=False,
        ),
    )
    op.create_index(op.f("ix_automation_jobs_job_type"), "automation_jobs", ["job_type"])
    op.alter_column("automation_jobs", "campaign_id", existing_type=sa.Uuid(), nullable=True)


def downgrade() -> None:
    op.alter_column("automation_jobs", "campaign_id", existing_type=sa.Uuid(), nullable=False)
    op.drop_index(op.f("ix_automation_jobs_job_type"), table_name="automation_jobs")
    op.drop_column("automation_jobs", "job_type")
    sa.Enum(name="automation_job_type").drop(op.get_bind(), checkfirst=True)
