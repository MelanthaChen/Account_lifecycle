from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import AccountStatus, Platform


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("platform", "username", name="uq_accounts_platform_username"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nickname: Mapped[str] = mapped_column(String(120), nullable=False)
    username: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    status: Mapped[AccountStatus] = mapped_column(
        Enum(
            AccountStatus,
            name="account_status",
            values_callable=lambda enum: [item.value for item in enum],
            validate_strings=True,
        ),
        default=AccountStatus.ACTIVE,
        nullable=False,
    )
    platform: Mapped[Platform] = mapped_column(
        Enum(
            Platform,
            name="platform",
            values_callable=lambda enum: [item.value for item in enum],
            validate_strings=True,
        ),
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
    session_path: Mapped[str | None] = mapped_column(String(500))
    session_status: Mapped[str | None] = mapped_column(String(40))
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_validation: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    browser_profile: Mapped[str | None] = mapped_column(String(160))
    provider: Mapped[str | None] = mapped_column(String(80))
    browser_profile_path: Mapped[str | None] = mapped_column(String(500))
    storage_directory: Mapped[str | None] = mapped_column(String(500))
    saved_username: Mapped[str | None] = mapped_column(String(160))
    saved_password: Mapped[str | None] = mapped_column(String(500))
    remember_credentials: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    auto_login: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    launch_visible_browser: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
