from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from browser_sessions.base import BrowserSessionResult
from runtime_types import AccountLike, Platform, WorkflowActionType


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
    metadata: dict[str, Any] | None = None


class Provider(Protocol):
    """Platform provider interface used by orchestration services."""

    platform_name: Platform
    display_name: str
    home_url: str
    login_url: str

    def get_storage_directory(self, account: AccountLike) -> Path:
        ...

    def get_profile_directory(self, account: AccountLike) -> Path:
        ...

    async def create_session(self, account: AccountLike) -> BrowserSessionResult:
        ...

    async def finish_session(
        self,
        account: AccountLike,
        active_session: object | None = None,
    ) -> BrowserSessionResult:
        ...

    async def validate_session(self, account: AccountLike) -> BrowserSessionResult:
        ...

    async def refresh_session(self, account: AccountLike) -> BrowserSessionResult:
        ...

    async def delete_session(self, account: AccountLike) -> BrowserSessionResult:
        ...

    async def logout(self, account: AccountLike) -> BrowserSessionResult:
        ...

    async def close_session(self, active_session: object) -> None:
        ...

    async def open_persistent_context(self, account: AccountLike, *, headless: bool) -> object:
        ...

    async def open_browser(self, account: AccountLike) -> BrowserSessionResult:
        ...

    async def open_home(self, account: AccountLike) -> BrowserSessionResult:
        ...

    async def open_url(self, account: AccountLike, url: str) -> BrowserSessionResult:
        ...

    async def sync_profile(self, account: AccountLike) -> ProviderProfileData:
        ...

    async def health_check(self, account: AccountLike) -> dict[str, Any]:
        ...

    async def start_behavior_session(self, account: AccountLike) -> Any:
        ...

    async def close_behavior_session(self, session: Any | None) -> None:
        ...

    async def execute_action(
        self,
        account: AccountLike,
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
