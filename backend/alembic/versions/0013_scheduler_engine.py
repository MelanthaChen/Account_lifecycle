"""add scheduler engine

Revision ID: 0013_scheduler_engine
Revises: 0012_recommendation_engine
Create Date: 2026-07-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0013_scheduler_engine"
down_revision: str | None = "0012_recommendation_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    schedule_type = sa.Enum("ONCE", "DAILY", "WEEKLY", "CUSTOM_CRON", name="schedule_type")
    schedule_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "campaign_schedules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("campaign_id", sa.Uuid(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column(
            "schedule_type",
            postgresql.ENUM(name="schedule_type", create_type=False),
            nullable=False,
        ),
        sa.Column("cron_expression", sa.String(length=120), nullable=True),
        sa.Column("timezone", sa.String(length=80), nullable=False),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_status", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id"),
    )
    op.create_index(op.f("ix_campaign_schedules_campaign_id"), "campaign_schedules", ["campaign_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_campaign_schedules_campaign_id"), table_name="campaign_schedules")
    op.drop_table("campaign_schedules")
    sa.Enum(name="schedule_type").drop(op.get_bind(), checkfirst=True)
