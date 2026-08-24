"""add automation worker heartbeat state

Revision ID: 0016_remote_agent_heartbeat
Revises: 0015_automation_jobs
Create Date: 2026-08-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0016_remote_agent_heartbeat"
down_revision: str | None = "0015_automation_jobs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "automation_workers",
        sa.Column("worker_id", sa.String(length=120), nullable=False),
        sa.Column("hostname", sa.String(length=255), nullable=True),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("running_job", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["running_job"], ["automation_jobs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("worker_id"),
    )


def downgrade() -> None:
    op.drop_table("automation_workers")
