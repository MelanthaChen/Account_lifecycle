from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.post import Post


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (UniqueConstraint("account_id", "reddit_id", name="uq_comments_account_reddit_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    reddit_id: Mapped[str] = mapped_column(String(32), index=True)
    account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    post_id: Mapped[UUID | None] = mapped_column(ForeignKey("posts.id", ondelete="SET NULL"), index=True)
    subreddit: Mapped[str] = mapped_column(String(120), index=True)
    body: Mapped[str | None] = mapped_column(Text)
    score: Mapped[int] = mapped_column(Integer, default=0)
    created_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    account: Mapped["Account"] = relationship(back_populates="comments")
    post: Mapped["Post | None"] = relationship(back_populates="comments")
