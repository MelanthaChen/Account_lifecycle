from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.account import Account


class Subreddit(Base):
    __tablename__ = "subreddits"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(160))
    icon: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)

    account_links: Mapped[list["AccountSubreddit"]] = relationship(back_populates="subreddit")


class AccountSubreddit(Base):
    __tablename__ = "account_subreddits"
    __table_args__ = (UniqueConstraint("account_id", "subreddit_id", name="uq_account_subreddit"),)

    account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True)
    subreddit_id: Mapped[UUID] = mapped_column(ForeignKey("subreddits.id", ondelete="CASCADE"), primary_key=True)
    activity_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    account: Mapped["Account"] = relationship(back_populates="subreddit_links")
    subreddit: Mapped[Subreddit] = relationship(back_populates="account_links")
