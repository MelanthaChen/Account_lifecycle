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


class BrowserSessionProvider(Protocol):
    def get_storage_directory(self, account: Account) -> Path:
        ...

    def get_profile_directory(self, account: Account) -> Path:
        ...

    def create_session(self, account: Account) -> BrowserSessionResult:
        ...

    def finish_session(self, account: Account) -> BrowserSessionResult:
        ...

    def validate(self, account: Account) -> BrowserSessionResult:
        ...

    def refresh(self, account: Account) -> BrowserSessionResult:
        ...

    def delete(self, account: Account) -> BrowserSessionResult:
        ...

    def logout(self, account: Account) -> BrowserSessionResult:
        ...

    def open_browser(self, account: Account) -> BrowserSessionResult:
        ...

    def open_url(self, account: Account, url: str) -> BrowserSessionResult:
        ...

    def open_home(self, account: Account) -> BrowserSessionResult:
        ...
