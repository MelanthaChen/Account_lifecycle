from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.comment import Comment


class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("account_id", "reddit_id", name="uq_posts_account_reddit_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    reddit_id: Mapped[str] = mapped_column(String(32), index=True)
    account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(500))
    subreddit: Mapped[str] = mapped_column(String(120), index=True)
    url: Mapped[str | None] = mapped_column(Text)
    score: Mapped[int] = mapped_column(Integer, default=0)
    num_comments: Mapped[int] = mapped_column(Integer, default=0)
    created_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    body: Mapped[str | None] = mapped_column(Text)

    account: Mapped["Account"] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(back_populates="post", cascade="all, delete-orphan")
