from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AccountStatus, Platform

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.post import Post
    from app.models.subreddit import AccountSubreddit
    from app.models.sync_job import SyncJob


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nickname: Mapped[str] = mapped_column(String(120), nullable=False)
    reddit_username: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus, name="account_status"),
        default=AccountStatus.ACTIVE,
        nullable=False,
    )
    platform: Mapped[Platform] = mapped_column(
        Enum(Platform, name="platform"),
        default=Platform.REDDIT,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_sync: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sync_jobs: Mapped[list["SyncJob"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    posts: Mapped[list["Post"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    subreddit_links: Mapped[list["AccountSubreddit"]] = relationship(
        back_populates="account",
        cascade="all, delete-orphan",
    )
