"""add behavior workflow actions

Revision ID: 0009_behavior_engine
Revises: 0008_workflow_engine
Create Date: 2026-07-07
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0009_behavior_engine"
down_revision: str | None = "0008_workflow_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE workflow_action_type ADD VALUE IF NOT EXISTS 'WAIT'")
    op.execute("ALTER TYPE workflow_action_type ADD VALUE IF NOT EXISTS 'SCROLL'")
    op.execute("ALTER TYPE workflow_action_type ADD VALUE IF NOT EXISTS 'OPEN_POST'")
    op.execute("ALTER TYPE workflow_action_type ADD VALUE IF NOT EXISTS 'BACK'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values without recreating the type.
    pass
