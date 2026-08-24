from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from runtime_types import AccountLike


@dataclass(frozen=True)
class BrowserSessionResult:
    session_path: str | None = None
    storage_directory: str | None = None
    browser_profile_path: str | None = None
    session_status: str | None = None
    last_login_changed: bool = False
    last_validation_changed: bool = False
    active_session: object | None = None


class BrowserSessionProvider(Protocol):
    def get_storage_directory(self, account: AccountLike) -> Path:
        ...

    def get_profile_directory(self, account: AccountLike) -> Path:
        ...

    async def create_session(self, account: AccountLike) -> BrowserSessionResult:
        ...

    async def finish_session(self, account: AccountLike, active_session: object | None = None) -> BrowserSessionResult:
        ...

    async def close_session(self, active_session: object) -> None:
        ...

    async def open_persistent_context(self, account: AccountLike, *, headless: bool) -> object:
        ...

    async def validate(self, account: AccountLike) -> BrowserSessionResult:
        ...

    async def refresh(self, account: AccountLike) -> BrowserSessionResult:
        ...

    async def delete(self, account: AccountLike) -> BrowserSessionResult:
        ...

    async def logout(self, account: AccountLike) -> BrowserSessionResult:
        ...

    async def open_browser(self, account: AccountLike) -> BrowserSessionResult:
        ...

    async def open_url(self, account: AccountLike, url: str) -> BrowserSessionResult:
        ...

    async def open_home(self, account: AccountLike) -> BrowserSessionResult:
        ...
