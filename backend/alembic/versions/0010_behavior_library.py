"""add behavior library

Revision ID: 0010_behavior_library
Revises: 0009_behavior_engine
Create Date: 2026-07-07
"""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0010_behavior_library"
down_revision: str | None = "0009_behavior_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


behavior_templates = sa.table(
    "behavior_templates",
    sa.column("id", sa.Uuid()),
    sa.column("name", sa.String()),
    sa.column("description", sa.Text()),
    sa.column("platform", postgresql.ENUM("reddit", name="platform", create_type=False)),
    sa.column("category", sa.String()),
    sa.column("workflow_json", sa.JSON()),
    sa.column("is_builtin", sa.Boolean()),
)


def upgrade() -> None:
    op.create_table(
        "behavior_templates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("platform", postgresql.ENUM("reddit", name="platform", create_type=False), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("workflow_json", sa.JSON(), nullable=False),
        sa.Column("is_builtin", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.bulk_insert(
        behavior_templates,
        [
            {
                "id": uuid4(),
                "name": "Warm Up",
                "description": "Open the target, wait, scroll, inspect a post, return, then upvote.",
                "platform": "reddit",
                "category": "Warmup",
                "workflow_json": [
                    {"action": "OPEN_URL"},
                    {"action": "WAIT", "config": {"min_seconds": 5, "max_seconds": 12}},
                    {"action": "SCROLL", "config": {"count": 3}},
                    {"action": "OPEN_POST", "config": {"strategy": "random"}},
                    {"action": "WAIT", "config": {"min_seconds": 5, "max_seconds": 12}},
                    {"action": "BACK"},
                    {"action": "UPVOTE"},
                ],
                "is_builtin": True,
            },
            {
                "id": uuid4(),
                "name": "Quick Upvote",
                "description": "Open the target, pause briefly, then upvote.",
                "platform": "reddit",
                "category": "Quick",
                "workflow_json": [
                    {"action": "OPEN_URL"},
                    {"action": "WAIT", "config": {"min_seconds": 5, "max_seconds": 12}},
                    {"action": "UPVOTE"},
                ],
                "is_builtin": True,
            },
            {
                "id": uuid4(),
                "name": "Casual Reader",
                "description": "Browse lightly before opening a post and returning.",
                "platform": "reddit",
                "category": "Reading",
                "workflow_json": [
                    {"action": "OPEN_URL"},
                    {"action": "WAIT", "config": {"min_seconds": 5, "max_seconds": 12}},
                    {"action": "SCROLL", "config": {"count": 3}},
                    {"action": "WAIT", "config": {"min_seconds": 5, "max_seconds": 12}},
                    {"action": "OPEN_POST", "config": {"strategy": "random"}},
                    {"action": "WAIT", "config": {"min_seconds": 5, "max_seconds": 12}},
                    {"action": "BACK"},
                ],
                "is_builtin": True,
            },
            {
                "id": uuid4(),
                "name": "Deep Reader",
                "description": "Open a post first, read, scroll inside it, wait, and return.",
                "platform": "reddit",
                "category": "Reading",
                "workflow_json": [
                    {"action": "OPEN_URL"},
                    {"action": "WAIT", "config": {"min_seconds": 5, "max_seconds": 12}},
                    {"action": "OPEN_POST", "config": {"strategy": "random"}},
                    {"action": "WAIT", "config": {"min_seconds": 5, "max_seconds": 12}},
                    {"action": "SCROLL", "config": {"count": 3}},
                    {"action": "WAIT", "config": {"min_seconds": 5, "max_seconds": 12}},
                    {"action": "BACK"},
                ],
                "is_builtin": True,
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("behavior_templates")
