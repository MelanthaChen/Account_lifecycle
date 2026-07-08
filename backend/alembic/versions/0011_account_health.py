"""add account health

Revision ID: 0011_account_health
Revises: 0010_behavior_library
Create Date: 2026-07-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0011_account_health"
down_revision: str | None = "0010_behavior_library"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    health_status = sa.Enum("HEALTHY", "WARNING", "CRITICAL", name="health_status")
    risk_level = sa.Enum("LOW", "MEDIUM", "HIGH", name="risk_level")
    health_status.create(op.get_bind(), checkfirst=True)
    risk_level.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "account_health",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("health_score", sa.Integer(), nullable=False),
        sa.Column(
            "health_status",
            postgresql.ENUM(name="health_status", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "risk_level",
            postgresql.ENUM(name="risk_level", create_type=False),
            nullable=False,
        ),
        sa.Column("signals", sa.JSON(), nullable=False),
        sa.Column("last_evaluated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id"),
    )
    op.create_index(op.f("ix_account_health_account_id"), "account_health", ["account_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_account_health_account_id"), table_name="account_health")
    op.drop_table("account_health")
    sa.Enum(name="risk_level").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="health_status").drop(op.get_bind(), checkfirst=True)
