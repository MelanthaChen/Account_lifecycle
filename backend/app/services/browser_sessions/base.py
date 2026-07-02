from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from app.models.account import Account


@dataclass(frozen=True)
class BrowserSessionResult:
    session_path: str | None = None
    session_status: str | None = None
    last_login_changed: bool = False
    last_validation_changed: bool = False


class BrowserSessionProvider(Protocol):
    def get_storage_directory(self, account: Account) -> Path:
        ...

    def login(self, account: Account) -> BrowserSessionResult:
        ...

    def validate(self, account: Account) -> BrowserSessionResult:
        ...

    def refresh(self, account: Account) -> BrowserSessionResult:
        ...

    def delete(self, account: Account) -> BrowserSessionResult:
        ...
