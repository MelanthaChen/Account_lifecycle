"""add campaign engine

Revision ID: 0007_campaign_engine
Revises: 0006_activity_engine
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_campaign_engine"
down_revision: str | None = "0006_activity_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    campaign_action_type = sa.Enum("UPVOTE", name="campaign_action_type")
    campaign_status = sa.Enum("Draft", "Ready", "Running", "Completed", "Failed", name="campaign_status")
    campaign_action_type.create(op.get_bind(), checkfirst=True)
    campaign_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "campaigns",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("platform", postgresql.ENUM("reddit", name="platform", create_type=False), nullable=False),
        sa.Column(
            "action_type",
            postgresql.ENUM(name="campaign_action_type", create_type=False),
            nullable=False,
        ),
        sa.Column("target_url", sa.String(length=1000), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(name="campaign_status", create_type=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_campaigns_status"), "campaigns", ["status"], unique=False)

    op.create_table(
        "campaign_accounts",
        sa.Column("campaign_id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("execution_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("campaign_id", "account_id"),
        sa.UniqueConstraint("campaign_id", "account_id", name="uq_campaign_accounts_campaign_account"),
        sa.UniqueConstraint("campaign_id", "execution_order", name="uq_campaign_accounts_execution_order"),
    )


def downgrade() -> None:
    op.drop_table("campaign_accounts")
    op.drop_index(op.f("ix_campaigns_status"), table_name="campaigns")
    op.drop_table("campaigns")
    sa.Enum(name="campaign_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="campaign_action_type").drop(op.get_bind(), checkfirst=True)
