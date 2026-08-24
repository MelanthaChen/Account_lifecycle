from __future__ import annotations

from pathlib import Path

from browser_sessions.base import BrowserSessionResult
from providers.manager import provider_manager
from runtime_types import AccountLike


class BrowserManager:
    """Routes browser session operations to the provider registered for an account platform."""

    def __init__(self) -> None:
        self._active_sessions: dict[str, object] = {}

    def locate_storage(self, account: AccountLike) -> Path:
        """Return the account storage directory for its platform provider."""
        provider = provider_manager.get_provider(account.platform)
        return provider.get_storage_directory(account)

    def locate_profile(self, account: AccountLike) -> Path:
        """Return the persistent browser profile directory for an account."""
        provider = provider_manager.get_provider(account.platform)
        return provider.get_profile_directory(account)

    async def create_session(self, account: AccountLike) -> BrowserSessionResult:
        """Start a manual login session and keep the provider context alive."""
        provider = provider_manager.get_provider(account.platform)
        active_session = self._active_sessions.pop(str(account.id), None)
        if active_session is not None:
            await provider.close_session(active_session)
        result = await provider.create_session(account)
        if result.active_session is not None:
            self._active_sessions[str(account.id)] = result.active_session
        return result

    async def finish_session(self, account: AccountLike) -> BrowserSessionResult:
        """Finish a manual login session by reusing the active provider context."""
        provider = provider_manager.get_provider(account.platform)
        active_session = self._active_sessions.pop(str(account.id), None)
        return await provider.finish_session(account, active_session)

    async def open_persistent_context(self, account: AccountLike, *, headless: bool) -> object:
        """Open a provider-owned persistent browser context."""
        provider = provider_manager.get_provider(account.platform)
        return await provider.open_persistent_context(account, headless=headless)

    async def close_session(self, account: AccountLike, active_session: object) -> None:
        """Close a provider-owned active browser session."""
        provider = provider_manager.get_provider(account.platform)
        await provider.close_session(active_session)

    async def validate_session(self, account: AccountLike) -> BrowserSessionResult:
        """Validate the stored session through the account provider."""
        provider = provider_manager.get_provider(account.platform)
        return await provider.validate_session(account)

    async def refresh_session(self, account: AccountLike) -> BrowserSessionResult:
        """Refresh the stored session through the account provider."""
        provider = provider_manager.get_provider(account.platform)
        return await provider.refresh_session(account)

    async def logout(self, account: AccountLike) -> BrowserSessionResult:
        """Clear provider session cookies and persisted storage state."""
        provider = provider_manager.get_provider(account.platform)
        return await provider.logout(account)

    async def delete_session(self, account: AccountLike) -> BrowserSessionResult:
        """Delete provider storage and close any active manual login context."""
        provider = provider_manager.get_provider(account.platform)
        active_session = self._active_sessions.pop(str(account.id), None)
        if active_session is not None:
            await provider.close_session(active_session)
        return await provider.delete(account)

    async def open_browser(self, account: AccountLike) -> BrowserSessionResult:
        """Open the provider browser profile."""
        provider = provider_manager.get_provider(account.platform)
        return await provider.open_browser(account)

    async def open_url(self, account: AccountLike, url: str) -> BrowserSessionResult:
        """Open a URL in the provider browser profile."""
        provider = provider_manager.get_provider(account.platform)
        return await provider.open_url(account, url)

    async def open_home(self, account: AccountLike) -> BrowserSessionResult:
        """Open the provider home page in the browser profile."""
        provider = provider_manager.get_provider(account.platform)
        return await provider.open_home(account)

    async def restart_browser(self, account: AccountLike) -> BrowserSessionResult:
        """Clear session cookies and reopen the provider browser profile."""
        await self.logout(account)
        return await self.open_browser(account)


browser_manager = BrowserManager()
