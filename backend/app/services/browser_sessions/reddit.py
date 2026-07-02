from __future__ import annotations

from pathlib import Path
import re
import shutil

from app.models.account import Account
from app.services.browser_sessions.base import BrowserSessionResult


class RedditSessionProvider:
    platform = "reddit"

    def __init__(self, storage_root: Path | str = "storage") -> None:
        self.storage_root = Path(storage_root)

    def get_storage_directory(self, account: Account) -> Path:
        return self.storage_root / self.platform / self._account_directory_name(account)

    def get_state_path(self, account: Account) -> Path:
        return self.get_storage_directory(account) / "state.json"

    def login(self, account: Account) -> BrowserSessionResult:
        from playwright.sync_api import sync_playwright

        storage_directory = self.ensure_storage_directories(account)
        state_path = storage_directory / "state.json"

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.goto("https://www.reddit.com/login/")

            try:
                for _ in range(300):
                    if page.is_closed():
                        raise RuntimeError("Login browser was closed before a session was detected.")

                    cookies = context.cookies("https://www.reddit.com")
                    if self._has_authenticated_cookie(cookies):
                        context.storage_state(path=str(state_path))
                        break

                    page.wait_for_timeout(2000)
                else:
                    raise TimeoutError("Timed out waiting for Reddit login to complete.")
            finally:
                browser.close()

        return BrowserSessionResult(
            session_path=str(state_path),
            session_status="valid",
            last_login_changed=True,
            last_validation_changed=True,
        )

    def validate(self, account: Account) -> BrowserSessionResult:
        from playwright.sync_api import sync_playwright

        state_path = Path(account.session_path) if account.session_path else self.get_state_path(account)

        if not state_path.exists():
            return BrowserSessionResult(
                session_path=None,
                session_status="missing",
                last_validation_changed=True,
            )

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(storage_state=str(state_path))
            page = context.new_page()
            page.goto("https://www.reddit.com/", wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
            cookies = context.cookies("https://www.reddit.com")
            browser.close()

        return BrowserSessionResult(
            session_path=str(state_path),
            session_status="valid" if self._has_authenticated_cookie(cookies) else "invalid",
            last_validation_changed=True,
        )

    def refresh(self, account: Account) -> BrowserSessionResult:
        return self.validate(account)

    def delete(self, account: Account) -> BrowserSessionResult:
        storage_directory = self.get_storage_directory(account)

        if storage_directory.exists():
            shutil.rmtree(storage_directory)

        return BrowserSessionResult(
            session_path=None,
            session_status="missing",
            last_validation_changed=True,
        )

    def ensure_storage_directories(self, account: Account) -> Path:
        storage_directory = self.get_storage_directory(account)
        for child in ["screenshots", "downloads", "logs"]:
            (storage_directory / child).mkdir(parents=True, exist_ok=True)
        return storage_directory

    @staticmethod
    def _account_directory_name(account: Account) -> str:
        raw_name = account.username or account.nickname or str(account.id)
        name = re.sub(r"[^A-Za-z0-9._-]+", "-", raw_name.strip())
        return name.strip("-") or str(account.id)

    @staticmethod
    def _has_authenticated_cookie(cookies: list[dict]) -> bool:
        return any(
            cookie.get("name") in {"reddit_session", "token_v2"}
            for cookie in cookies
        )
