"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    account_status = sa.Enum("ACTIVE", "PAUSED", "ERROR", "ARCHIVED", name="account_status")
    platform = sa.Enum("REDDIT", name="platform")
    sync_job_status = sa.Enum("QUEUED", "RUNNING", "SUCCEEDED", "FAILED", name="sync_job_status")
    account_status.create(op.get_bind(), checkfirst=True)
    platform.create(op.get_bind(), checkfirst=True)
    sync_job_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nickname", sa.String(length=120), nullable=False),
        sa.Column("reddit_username", sa.String(length=32), nullable=False),
        sa.Column("status", account_status, nullable=False),
        sa.Column("platform", platform, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_sync", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_accounts_reddit_username"), "accounts", ["reddit_username"], unique=True)

    op.create_table(
        "subreddits",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=True),
        sa.Column("icon", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_subreddits_name"), "subreddits", ["name"], unique=True)

    op.create_table(
        "sync_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("status", sync_job_status, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sync_jobs_account_id"), "sync_jobs", ["account_id"], unique=False)

    op.create_table(
        "posts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("reddit_id", sa.String(length=32), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("subreddit", sa.String(length=120), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("num_comments", sa.Integer(), nullable=False),
        sa.Column("created_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id", "reddit_id", name="uq_posts_account_reddit_id"),
    )
    op.create_index(op.f("ix_posts_account_id"), "posts", ["account_id"], unique=False)
    op.create_index(op.f("ix_posts_created_utc"), "posts", ["created_utc"], unique=False)
    op.create_index(op.f("ix_posts_reddit_id"), "posts", ["reddit_id"], unique=False)
    op.create_index(op.f("ix_posts_subreddit"), "posts", ["subreddit"], unique=False)

    op.create_table(
        "comments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("reddit_id", sa.String(length=32), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("post_id", sa.Uuid(), nullable=True),
        sa.Column("subreddit", sa.String(length=120), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("created_utc", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id", "reddit_id", name="uq_comments_account_reddit_id"),
    )
    op.create_index(op.f("ix_comments_account_id"), "comments", ["account_id"], unique=False)
    op.create_index(op.f("ix_comments_created_utc"), "comments", ["created_utc"], unique=False)
    op.create_index(op.f("ix_comments_post_id"), "comments", ["post_id"], unique=False)
    op.create_index(op.f("ix_comments_reddit_id"), "comments", ["reddit_id"], unique=False)
    op.create_index(op.f("ix_comments_subreddit"), "comments", ["subreddit"], unique=False)

    op.create_table(
        "account_subreddits",
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("subreddit_id", sa.Uuid(), nullable=False),
        sa.Column("activity_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subreddit_id"], ["subreddits.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("account_id", "subreddit_id"),
        sa.UniqueConstraint("account_id", "subreddit_id", name="uq_account_subreddit"),
    )


def downgrade() -> None:
    op.drop_table("account_subreddits")
    op.drop_index(op.f("ix_comments_subreddit"), table_name="comments")
    op.drop_index(op.f("ix_comments_reddit_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_post_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_created_utc"), table_name="comments")
    op.drop_index(op.f("ix_comments_account_id"), table_name="comments")
    op.drop_table("comments")
    op.drop_index(op.f("ix_posts_subreddit"), table_name="posts")
    op.drop_index(op.f("ix_posts_reddit_id"), table_name="posts")
    op.drop_index(op.f("ix_posts_created_utc"), table_name="posts")
    op.drop_index(op.f("ix_posts_account_id"), table_name="posts")
    op.drop_table("posts")
    op.drop_index(op.f("ix_sync_jobs_account_id"), table_name="sync_jobs")
    op.drop_table("sync_jobs")
    op.drop_index(op.f("ix_subreddits_name"), table_name="subreddits")
    op.drop_table("subreddits")
    op.drop_index(op.f("ix_accounts_reddit_username"), table_name="accounts")
    op.drop_table("accounts")
    sa.Enum(name="sync_job_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="platform").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="account_status").drop(op.get_bind(), checkfirst=True)
