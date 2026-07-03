from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AccountStatus, Platform


class AccountBase(BaseModel):
    nickname: str = Field(min_length=1, max_length=120)
    username: str = Field(min_length=1, max_length=120, pattern=r"^[A-Za-z0-9_.-]+$")
    status: AccountStatus = AccountStatus.ACTIVE
    platform: Platform = Platform.REDDIT
    notes: str | None = None
    is_active: bool = True
    provider: str | None = Field(default=None, max_length=80)
    saved_username: str | None = Field(default=None, max_length=160)
    remember_credentials: bool = False
    auto_login: bool = False
    launch_visible_browser: bool = True


class AccountCreate(AccountBase):
    saved_password: str | None = Field(default=None, max_length=500)


class AccountUpdate(BaseModel):
    nickname: str | None = Field(default=None, min_length=1, max_length=120)
    username: str | None = Field(default=None, min_length=1, max_length=120, pattern=r"^[A-Za-z0-9_.-]+$")
    platform: Platform | None = None
    status: AccountStatus | None = None
    notes: str | None = None
    is_active: bool | None = None
    provider: str | None = Field(default=None, max_length=80)
    browser_profile_path: str | None = Field(default=None, max_length=500)
    storage_directory: str | None = Field(default=None, max_length=500)
    saved_username: str | None = Field(default=None, max_length=160)
    saved_password: str | None = Field(default=None, max_length=500)
    remember_credentials: bool | None = None
    auto_login: bool | None = None
    launch_visible_browser: bool | None = None


class AccountLogin(BaseModel):
    username: str | None = Field(default=None, max_length=160)
    password: str | None = Field(default=None, max_length=500)
    remember_credentials: bool | None = None
    auto_login: bool | None = None
    launch_visible_browser: bool | None = None


class AccountRead(AccountBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    last_sync: datetime | None = None
    session_path: str | None = None
    session_status: str | None = None
    last_login: datetime | None = None
    last_validation: datetime | None = None
    browser_profile: str | None = None
    browser_profile_path: str | None = None
    storage_directory: str | None = None

    model_config = ConfigDict(from_attributes=True)
