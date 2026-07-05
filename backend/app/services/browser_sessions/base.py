from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from app.models.account import Account


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
    def get_storage_directory(self, account: Account) -> Path:
        ...

    def get_profile_directory(self, account: Account) -> Path:
        ...

    async def create_session(self, account: Account) -> BrowserSessionResult:
        ...

    async def finish_session(self, account: Account, active_session: object | None = None) -> BrowserSessionResult:
        ...

    async def close_session(self, active_session: object) -> None:
        ...

    async def open_persistent_context(self, account: Account, *, headless: bool) -> object:
        ...

    async def validate(self, account: Account) -> BrowserSessionResult:
        ...

    async def refresh(self, account: Account) -> BrowserSessionResult:
        ...

    async def delete(self, account: Account) -> BrowserSessionResult:
        ...

    async def logout(self, account: Account) -> BrowserSessionResult:
        ...

    async def open_browser(self, account: Account) -> BrowserSessionResult:
        ...

    async def open_url(self, account: Account, url: str) -> BrowserSessionResult:
        ...

    async def open_home(self, account: Account) -> BrowserSessionResult:
        ...
