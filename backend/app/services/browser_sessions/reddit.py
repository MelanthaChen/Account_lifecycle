from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
import re
import shutil

from app.models.account import Account
from app.services.browser_sessions.base import BrowserSessionResult


VALID_STATUS = "valid"
INVALID_STATUS = "invalid"
LOGIN_REQUIRED_STATUS = "login_required"
MISSING_STATUS = "missing"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
logger = logging.getLogger(__name__)


@dataclass
class ActiveBrowserSession:
    playwright: object
    context: object


class RedditSessionProvider:
    """Reddit-specific browser session provider using Playwright persistent contexts."""

    platform = "reddit"
    home_url = "https://www.reddit.com/"
    login_url = "https://www.reddit.com/login/"

    def __init__(self, storage_root: Path | str | None = None) -> None:
        storage_root = storage_root or PROJECT_ROOT / "storage"
        self.storage_root = Path(storage_root)

    def get_storage_directory(self, account: Account) -> Path:
        """Return the account-owned storage directory."""
        if account.storage_directory:
            return self._resolve_storage_path(Path(account.storage_directory))
        return self.storage_root / self.platform / self._account_directory_name(account)

    def get_profile_directory(self, account: Account) -> Path:
        """Return the persistent Chromium profile directory."""
        if account.browser_profile_path:
            return self._resolve_storage_path(Path(account.browser_profile_path))
        return self.get_storage_directory(account) / "profile"

    def get_state_path(self, account: Account) -> Path:
        """Return the Playwright storage state path for an account."""
        return self.get_storage_directory(account) / "storage_state.json"

    async def create_session(self, account: Account) -> BrowserSessionResult:
        """Launch Reddit login and keep the browser context alive for manual login."""
        return await self._create_session(account)

    async def validate(self, account: Account) -> BrowserSessionResult:
        """Validate whether Reddit authentication cookies are present."""
        return await self._validate(account)

    async def refresh(self, account: Account) -> BrowserSessionResult:
        """Refresh session state by validating the current profile."""
        return await self.validate(account)

    async def delete(self, account: Account) -> BrowserSessionResult:
        """Delete the account storage directory."""
        return await self._delete(account)

    async def close_session(self, active_session: object) -> None:
        """Close a Reddit Playwright context and stop Playwright."""
        await self._close_session(active_session)

    async def open_persistent_context(self, account: Account, *, headless: bool) -> object:
        """Open the Reddit account's persistent Chromium profile."""
        return await self._open_persistent_context(account, headless=headless)

    async def logout(self, account: Account) -> BrowserSessionResult:
        """Clear Reddit cookies and remove storage state."""
        return await self._logout(account)

    async def open_browser(self, account: Account) -> BrowserSessionResult:
        """Open a blank Reddit profile browser window."""
        return await self.open_url(account, "about:blank")

    async def open_url(self, account: Account, url: str) -> BrowserSessionResult:
        """Open a URL in the Reddit account's persistent browser profile."""
        return await self._open_url(account, url)

    async def open_home(self, account: Account) -> BrowserSessionResult:
        """Open Reddit home in the account's persistent browser profile."""
        return await self.open_url(account, self.home_url)

    async def _create_session(self, account: Account) -> BrowserSessionResult:
        storage_directory = self.ensure_storage_directories(account)
        profile_directory = self.get_profile_directory(account)

        logger.info("Creating storage directory: %s", storage_directory)
        logger.info("Launching persistent profile: %s", profile_directory)
        active_session = await self._open_persistent_context(account, headless=not account.launch_visible_browser)
        context = active_session.context
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto(self.login_url, wait_until="domcontentloaded")
        logger.info("Waiting for manual login...")

        return self._result(
            account,
            session_status=LOGIN_REQUIRED_STATUS,
            active_session=active_session,
        )

    async def finish_session(self, account: Account, active_session: object | None = None) -> BrowserSessionResult:
        """Persist storage state from the active manual login browser context."""
        return await self._finish_session(account, active_session)

    async def _finish_session(self, account: Account, active_session: object | None = None) -> BrowserSessionResult:
        logger.info("Finish Session received.")
        if active_session is None:
            logger.info("No running browser context found. Validating existing profile.")
            return await self._validate(account)

        state_path = self.get_state_path(account)
        try:
            context = active_session.context
            logger.info("Saving storage state...")
            logger.info("%s", state_path)
            await context.storage_state(path=str(state_path))
            file_size = self._verify_storage_state_written(state_path)
            logger.info("Storage state written successfully.")
            logger.info("File exists: %s", state_path.exists())
            logger.info("File size: %s KB", max(1, file_size // 1024))
            cookies = await context.cookies(self.home_url)
            is_valid = self._has_authenticated_cookie(cookies)
        finally:
            logger.info("Closing browser.")
            await active_session.context.close()
            await active_session.playwright.stop()

        logger.info("Updating database.")
        if is_valid:
            logger.info("Session complete.")

        return self._result(
            account,
            session_path=str(state_path) if is_valid else None,
            session_status=VALID_STATUS if is_valid else INVALID_STATUS,
            last_login_changed=is_valid,
            last_validation_changed=True,
        )

    async def _validate(self, account: Account) -> BrowserSessionResult:
        state_path = Path(account.session_path) if account.session_path else self.get_state_path(account)
        profile_directory = self.get_profile_directory(account)

        if not profile_directory.exists():
            return self._result(
                account,
                session_path=None,
                session_status=MISSING_STATUS,
                last_validation_changed=True,
            )

        active_session = await self._open_persistent_context(account, headless=True)
        try:
            context = active_session.context
            page = context.pages[0] if context.pages else await context.new_page()
            await page.goto(self.home_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(1500)
            cookies = await context.cookies(self.home_url)
            await context.storage_state(path=str(state_path))
        finally:
            await self._close_session(active_session)

        return self._result(
            account,
            session_path=str(state_path),
            session_status=VALID_STATUS if self._has_authenticated_cookie(cookies) else INVALID_STATUS,
            last_validation_changed=True,
        )

    async def _delete(self, account: Account) -> BrowserSessionResult:
        storage_directory = self.get_storage_directory(account)

        if storage_directory.exists():
            shutil.rmtree(storage_directory)

        return BrowserSessionResult(
            session_path=None,
            storage_directory=None,
            browser_profile_path=None,
            session_status=MISSING_STATUS,
        )

    async def _logout(self, account: Account) -> BrowserSessionResult:
        state_path = self.get_state_path(account)

        active_session = await self._open_persistent_context(account, headless=True)
        try:
            context = active_session.context
            await context.clear_cookies()
        finally:
            await self._close_session(active_session)

        if state_path.exists():
            state_path.unlink()

        return self._result(
            account,
            session_path=None,
            session_status=MISSING_STATUS,
            last_validation_changed=True,
        )

    async def _open_url(self, account: Account, url: str) -> BrowserSessionResult:
        active_session = await self._open_persistent_context(account, headless=False)
        try:
            context = active_session.context
            page = context.pages[0] if context.pages else await context.new_page()
            if url != "about:blank":
                await page.goto(url, wait_until="domcontentloaded")
            while any(not item.is_closed() for item in context.pages):
                await page.wait_for_timeout(1000)
            await context.storage_state(path=str(self.get_state_path(account)))
        finally:
            await self._close_session(active_session)

        return self._result(account, session_status=account.session_status)

    def ensure_storage_directories(self, account: Account) -> Path:
        """Create the account-owned storage directory layout."""
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
        active_session: object | None = None,
    ) -> BrowserSessionResult:
        storage_directory = self.get_storage_directory(account)
        return BrowserSessionResult(
            session_path=session_path,
            storage_directory=str(storage_directory),
            browser_profile_path=str(self.get_profile_directory(account)),
            session_status=session_status,
            last_login_changed=last_login_changed,
            last_validation_changed=last_validation_changed,
            active_session=active_session,
        )

    @staticmethod
    async def _close_session(active_session: object) -> None:
        await active_session.context.close()
        await active_session.playwright.stop()

    async def _open_persistent_context(self, account: Account, *, headless: bool) -> ActiveBrowserSession:
        from playwright.async_api import async_playwright

        storage_directory = self.ensure_storage_directories(account)
        profile_directory = self.get_profile_directory(account)
        playwright = await async_playwright().start()
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_directory),
            headless=headless,
            accept_downloads=True,
            downloads_path=str(storage_directory / "downloads"),
        )
        return ActiveBrowserSession(playwright=playwright, context=context)

    def _resolve_storage_path(self, path: Path) -> Path:
        if path.is_absolute():
            return path
        return PROJECT_ROOT / path

    @staticmethod
    def _verify_storage_state_written(path: Path) -> int:
        if not path.exists():
            raise RuntimeError(f"Storage state was not written: {path}")
        file_size = path.stat().st_size
        if file_size <= 0:
            raise RuntimeError(f"Storage state is empty: {path}")
        return file_size

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
