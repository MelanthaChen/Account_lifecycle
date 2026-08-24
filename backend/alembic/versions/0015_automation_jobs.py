"""add automation job queue

Revision ID: 0015_automation_jobs
Revises: 0014_comment_engine
Create Date: 2026-08-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0015_automation_jobs"
down_revision: str | None = "0014_comment_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    job_status = sa.Enum("QUEUED", "RUNNING", "SUCCESS", "FAILED", "CANCELLED", name="automation_job_status")
    job_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "automation_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("campaign_id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_id", sa.Uuid(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(name="automation_job_status", create_type=False),
            nullable=False,
        ),
        sa.Column("queued_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("worker_id", sa.String(length=120), nullable=True),
        sa.Column("result_json", sa.JSON(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workflow_id"], ["workflow_steps.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_automation_jobs_account_id"), "automation_jobs", ["account_id"])
    op.create_index(op.f("ix_automation_jobs_campaign_id"), "automation_jobs", ["campaign_id"])
    op.create_index(op.f("ix_automation_jobs_status"), "automation_jobs", ["status"])
    op.create_index(op.f("ix_automation_jobs_worker_id"), "automation_jobs", ["worker_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_automation_jobs_worker_id"), table_name="automation_jobs")
    op.drop_index(op.f("ix_automation_jobs_status"), table_name="automation_jobs")
    op.drop_index(op.f("ix_automation_jobs_campaign_id"), table_name="automation_jobs")
    op.drop_index(op.f("ix_automation_jobs_account_id"), table_name="automation_jobs")
    op.drop_table("automation_jobs")
    sa.Enum(name="automation_job_status").drop(op.get_bind(), checkfirst=True)
