from __future__ import annotations

from pathlib import Path
import re
import shutil

from app.models.account import Account
from app.services.browser_sessions.base import BrowserLoginRequest, BrowserSessionResult


VALID_STATUS = "VALID"
INVALID_STATUS = "INVALID"
NOT_LOGGED_IN_STATUS = "NOT_LOGGED_IN"


class RedditSessionProvider:
    platform = "reddit"
    home_url = "https://www.reddit.com/"
    login_url = "https://www.reddit.com/login/"

    def __init__(self, storage_root: Path | str = "storage") -> None:
        self.storage_root = Path(storage_root)

    def get_storage_directory(self, account: Account) -> Path:
        if account.storage_directory:
            return Path(account.storage_directory)
        return self.storage_root / self.platform / self._account_directory_name(account)

    def get_profile_directory(self, account: Account) -> Path:
        if account.browser_profile_path:
            return Path(account.browser_profile_path)
        return self.get_storage_directory(account) / "profile"

    def get_state_path(self, account: Account) -> Path:
        return self.get_storage_directory(account) / "state.json"

    def login(self, account: Account, request: BrowserLoginRequest) -> BrowserSessionResult:
        from playwright.sync_api import sync_playwright

        storage_directory = self.ensure_storage_directories(account)
        state_path = storage_directory / "state.json"
        profile_directory = self.get_profile_directory(account)
        is_visible = True if request.launch_visible_browser is None else request.launch_visible_browser

        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile_directory),
                headless=not is_visible,
                accept_downloads=True,
                downloads_path=str(storage_directory / "downloads"),
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(self.login_url, wait_until="domcontentloaded")
            self._fill_login_form(page, request)

            try:
                for _ in range(300):
                    if page.is_closed():
                        raise RuntimeError("Login browser was closed before a session was detected.")

                    cookies = context.cookies(self.home_url)
                    if self._has_authenticated_cookie(cookies):
                        context.storage_state(path=str(state_path))
                        break

                    page.wait_for_timeout(2000)
                else:
                    raise TimeoutError("Timed out waiting for Reddit login to complete.")
            finally:
                context.close()

        return self._result(
            account,
            session_path=str(state_path),
            session_status=VALID_STATUS,
            last_login_changed=True,
            last_validation_changed=True,
        )

    def validate(self, account: Account) -> BrowserSessionResult:
        from playwright.sync_api import sync_playwright

        state_path = Path(account.session_path) if account.session_path else self.get_state_path(account)
        storage_directory = self.ensure_storage_directories(account)
        profile_directory = self.get_profile_directory(account)

        if not profile_directory.exists():
            return self._result(
                account,
                session_path=None,
                session_status=NOT_LOGGED_IN_STATUS,
                last_validation_changed=True,
            )

        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile_directory),
                headless=True,
                accept_downloads=True,
                downloads_path=str(storage_directory / "downloads"),
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(self.home_url, wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
            cookies = context.cookies(self.home_url)
            context.storage_state(path=str(state_path))
            context.close()

        return self._result(
            account,
            session_path=str(state_path),
            session_status=VALID_STATUS if self._has_authenticated_cookie(cookies) else INVALID_STATUS,
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
            storage_directory=None,
            browser_profile_path=None,
            session_status=NOT_LOGGED_IN_STATUS,
            last_validation_changed=True,
        )

    def logout(self, account: Account) -> BrowserSessionResult:
        from playwright.sync_api import sync_playwright

        storage_directory = self.ensure_storage_directories(account)
        profile_directory = self.get_profile_directory(account)
        state_path = self.get_state_path(account)

        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile_directory),
                headless=True,
                accept_downloads=True,
                downloads_path=str(storage_directory / "downloads"),
            )
            context.clear_cookies()
            context.close()

        if state_path.exists():
            state_path.unlink()

        return self._result(
            account,
            session_path=None,
            session_status=NOT_LOGGED_IN_STATUS,
            last_validation_changed=True,
        )

    def open_browser(self, account: Account) -> BrowserSessionResult:
        return self.open_url(account, "about:blank")

    def open_url(self, account: Account, url: str) -> BrowserSessionResult:
        from playwright.sync_api import sync_playwright

        storage_directory = self.ensure_storage_directories(account)
        profile_directory = self.get_profile_directory(account)

        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile_directory),
                headless=False,
                accept_downloads=True,
                downloads_path=str(storage_directory / "downloads"),
            )
            page = context.pages[0] if context.pages else context.new_page()
            if url != "about:blank":
                page.goto(url, wait_until="domcontentloaded")
            while any(not item.is_closed() for item in context.pages):
                page.wait_for_timeout(1000)
            context.storage_state(path=str(self.get_state_path(account)))
            context.close()

        return self._result(account, session_status=account.session_status)

    def open_home(self, account: Account) -> BrowserSessionResult:
        return self.open_url(account, self.home_url)

    def ensure_storage_directories(self, account: Account) -> Path:
        storage_directory = self.get_storage_directory(account)
        for child in ["profile", "screenshots", "downloads", "logs", "exports"]:
            (storage_directory / child).mkdir(parents=True, exist_ok=True)
        return storage_directory

    def _result(
        self,
        account: Account,
        *,
        session_path: str | None = None,
        session_status: str | None = None,
        last_login_changed: bool = False,
        last_validation_changed: bool = False,
    ) -> BrowserSessionResult:
        storage_directory = self.get_storage_directory(account)
        return BrowserSessionResult(
            session_path=session_path,
            storage_directory=str(storage_directory),
            browser_profile_path=str(self.get_profile_directory(account)),
            session_status=session_status,
            last_login_changed=last_login_changed,
            last_validation_changed=last_validation_changed,
        )

    @staticmethod
    def _fill_login_form(page, request: BrowserLoginRequest) -> None:
        if not request.username or not request.password:
            return

        username_selectors = [
            'input[name="username"]',
            "#login-username",
            'input[autocomplete="username"]',
        ]
        password_selectors = [
            'input[name="password"]',
            "#login-password",
            'input[type="password"]',
        ]

        username_filled = RedditSessionProvider._fill_first_available(page, username_selectors, request.username)
        password_filled = RedditSessionProvider._fill_first_available(page, password_selectors, request.password)
        if username_filled and password_filled:
            submit = page.locator('button[type="submit"]').first
            if submit.count() > 0:
                submit.click()

    @staticmethod
    def _fill_first_available(page, selectors: list[str], value: str) -> bool:
        for selector in selectors:
            locator = page.locator(selector).first
            try:
                if locator.count() > 0 and locator.is_visible(timeout=1000):
                    locator.fill(value)
                    return True
            except Exception:
                continue
        return False

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
