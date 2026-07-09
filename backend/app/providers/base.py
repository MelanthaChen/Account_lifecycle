from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from app.models.account import Account
from app.models.enums import Platform, WorkflowActionType
from app.services.browser_sessions.base import BrowserSessionResult


@dataclass(frozen=True)
class ProviderProfileData:
    display_name: str | None = None
    provider_username: str | None = None
    avatar_url: str | None = None
    karma_post: int | None = None
    karma_comment: int | None = None
    cake_day: str | None = None
    verified_email: bool | None = None
    is_nsfw: bool | None = None
    is_moderator: bool | None = None
    is_gold: bool | None = None


@dataclass(frozen=True)
class ProviderActionResult:
    account: str
    opened: bool = False
    clicked: bool = False
    verified: bool = False
    success: bool = False
    reason: str | None = None
    detail: str | None = None


class Provider(Protocol):
    """Platform provider interface used by orchestration services."""

    platform_name: Platform
    display_name: str
    home_url: str
    login_url: str

    def get_storage_directory(self, account: Account) -> Path:
        ...

    def get_profile_directory(self, account: Account) -> Path:
        ...

    async def create_session(self, account: Account) -> BrowserSessionResult:
        ...

    async def finish_session(
        self,
        account: Account,
        active_session: object | None = None,
    ) -> BrowserSessionResult:
        ...

    async def validate_session(self, account: Account) -> BrowserSessionResult:
        ...

    async def refresh_session(self, account: Account) -> BrowserSessionResult:
        ...

    async def delete_session(self, account: Account) -> BrowserSessionResult:
        ...

    async def logout(self, account: Account) -> BrowserSessionResult:
        ...

    async def close_session(self, active_session: object) -> None:
        ...

    async def open_persistent_context(self, account: Account, *, headless: bool) -> object:
        ...

    async def open_browser(self, account: Account) -> BrowserSessionResult:
        ...

    async def open_home(self, account: Account) -> BrowserSessionResult:
        ...

    async def open_url(self, account: Account, url: str) -> BrowserSessionResult:
        ...

    async def sync_profile(self, account: Account) -> ProviderProfileData:
        ...

    async def health_check(self, account: Account) -> dict[str, Any]:
        ...

    async def start_behavior_session(self, account: Account) -> Any:
        ...

    async def close_behavior_session(self, session: Any | None) -> None:
        ...

    async def execute_action(
        self,
        account: Account,
        action_type: WorkflowActionType,
        *,
        target_url: str | None = None,
        config: dict[str, Any] | None = None,
        session: Any | None = None,
    ) -> ProviderActionResult:
        ...

    def supported_actions(self) -> set[WorkflowActionType]:
        ...

    def supported_behaviors(self) -> set[WorkflowActionType]:
        ...
