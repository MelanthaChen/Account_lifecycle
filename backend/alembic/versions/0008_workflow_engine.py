"""add workflow engine

Revision ID: 0008_workflow_engine
Revises: 0007_campaign_engine
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_workflow_engine"
down_revision: str | None = "0007_campaign_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    workflow_action_type = sa.Enum("OPEN_URL", "UPVOTE", name="workflow_action_type")
    workflow_action_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "workflow_steps",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("campaign_id", sa.Uuid(), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column(
            "action_type",
            postgresql.ENUM(name="workflow_action_type", create_type=False),
            nullable=False,
        ),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "step_order", name="uq_workflow_steps_campaign_order"),
    )
    op.create_index(op.f("ix_workflow_steps_campaign_id"), "workflow_steps", ["campaign_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_workflow_steps_campaign_id"), table_name="workflow_steps")
    op.drop_table("workflow_steps")
    sa.Enum(name="workflow_action_type").drop(op.get_bind(), checkfirst=True)
