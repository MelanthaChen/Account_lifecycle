"""add activity engine

Revision ID: 0006_activity_engine
Revises: 0005_profile_sync
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_activity_engine"
down_revision: str | None = "0005_profile_sync"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    activity_type = sa.Enum(
        "LOGIN",
        "OPEN_BROWSER",
        "OPEN_HOME",
        "BROWSE",
        "UPVOTE",
        "DOWNVOTE",
        "COMMENT",
        "POST",
        "JOIN_SUBREDDIT",
        "LEAVE_SUBREDDIT",
        "SYNC_PROFILE",
        "VALIDATE_SESSION",
        "REFRESH_SESSION",
        "DELETE_SESSION",
        name="activity_type",
    )
    activity_status = sa.Enum(
        "PENDING",
        "RUNNING",
        "SUCCESS",
        "FAILED",
        "CANCELLED",
        name="activity_status",
    )
    activity_type.create(op.get_bind(), checkfirst=True)
    activity_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "activities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("platform", postgresql.ENUM("reddit", name="platform", create_type=False), nullable=False),
        sa.Column("activity_type", postgresql.ENUM(name="activity_type", create_type=False), nullable=False),
        sa.Column("status", postgresql.ENUM(name="activity_status", create_type=False), nullable=False),
        sa.Column("target_url", sa.String(length=1000), nullable=True),
        sa.Column("title", sa.String(length=240), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_activities_account_id"), "activities", ["account_id"], unique=False)
    op.create_index(op.f("ix_activities_activity_type"), "activities", ["activity_type"], unique=False)
    op.create_index(op.f("ix_activities_status"), "activities", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_activities_status"), table_name="activities")
    op.drop_index(op.f("ix_activities_activity_type"), table_name="activities")
    op.drop_index(op.f("ix_activities_account_id"), table_name="activities")
    op.drop_table("activities")
    sa.Enum(name="activity_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="activity_type").drop(op.get_bind(), checkfirst=True)
