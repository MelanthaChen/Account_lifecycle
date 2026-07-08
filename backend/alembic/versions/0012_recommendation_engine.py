"""add recommendation engine

Revision ID: 0012_recommendation_engine
Revises: 0011_account_health
Create Date: 2026-07-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0012_recommendation_engine"
down_revision: str | None = "0011_account_health"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    recommendation_type = sa.Enum(
        "RUN_WARM_UP",
        "RUN_QUICK_UPVOTE",
        "RUN_CASUAL_READER",
        "RUN_DEEP_READER",
        "SYNC_PROFILE",
        "REFRESH_SESSION",
        "NO_ACTION",
        name="recommendation_type",
    )
    recommendation_priority = sa.Enum("HIGH", "MEDIUM", "LOW", name="recommendation_priority")
    recommendation_status = sa.Enum("ACTIVE", "DISMISSED", "COMPLETED", name="recommendation_status")
    recommendation_type.create(op.get_bind(), checkfirst=True)
    recommendation_priority.create(op.get_bind(), checkfirst=True)
    recommendation_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "account_recommendations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column(
            "recommendation_type",
            postgresql.ENUM(name="recommendation_type", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "priority",
            postgresql.ENUM(name="recommendation_priority", create_type=False),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("recommended_template_id", sa.Uuid(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(name="recommendation_status", create_type=False),
            nullable=False,
        ),
        sa.Column("reason", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recommended_template_id"], ["behavior_templates.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_account_recommendations_account_id"),
        "account_recommendations",
        ["account_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_account_recommendations_priority"),
        "account_recommendations",
        ["priority"],
        unique=False,
    )
    op.create_index(
        op.f("ix_account_recommendations_recommendation_type"),
        "account_recommendations",
        ["recommendation_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_account_recommendations_recommended_template_id"),
        "account_recommendations",
        ["recommended_template_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_account_recommendations_status"),
        "account_recommendations",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_account_recommendations_status"), table_name="account_recommendations")
    op.drop_index(op.f("ix_account_recommendations_recommended_template_id"), table_name="account_recommendations")
    op.drop_index(op.f("ix_account_recommendations_recommendation_type"), table_name="account_recommendations")
    op.drop_index(op.f("ix_account_recommendations_priority"), table_name="account_recommendations")
    op.drop_index(op.f("ix_account_recommendations_account_id"), table_name="account_recommendations")
    op.drop_table("account_recommendations")
    sa.Enum(name="recommendation_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="recommendation_priority").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="recommendation_type").drop(op.get_bind(), checkfirst=True)
