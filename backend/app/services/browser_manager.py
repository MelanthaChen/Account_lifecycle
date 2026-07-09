from __future__ import annotations

from pathlib import Path

from app.models.account import Account
from app.providers.manager import provider_manager
from app.services.browser_sessions.base import BrowserSessionResult


class BrowserManager:
    """Routes browser session operations to the provider registered for an account platform."""

    def __init__(self) -> None:
        self._active_sessions: dict[str, object] = {}

    def locate_storage(self, account: Account) -> Path:
        """Return the account storage directory for its platform provider."""
        provider = provider_manager.get_provider(account.platform)
        return provider.get_storage_directory(account)

    def locate_profile(self, account: Account) -> Path:
        """Return the persistent browser profile directory for an account."""
        provider = provider_manager.get_provider(account.platform)
        return provider.get_profile_directory(account)

    async def create_session(self, account: Account) -> BrowserSessionResult:
        """Start a manual login session and keep the provider context alive."""
        provider = provider_manager.get_provider(account.platform)
        active_session = self._active_sessions.pop(str(account.id), None)
        if active_session is not None:
            await provider.close_session(active_session)
        result = await provider.create_session(account)
        if result.active_session is not None:
            self._active_sessions[str(account.id)] = result.active_session
        return result

    async def finish_session(self, account: Account) -> BrowserSessionResult:
        """Finish a manual login session by reusing the active provider context."""
        provider = provider_manager.get_provider(account.platform)
        active_session = self._active_sessions.pop(str(account.id), None)
        return await provider.finish_session(account, active_session)

    async def open_persistent_context(self, account: Account, *, headless: bool) -> object:
        """Open a provider-owned persistent browser context."""
        provider = provider_manager.get_provider(account.platform)
        return await provider.open_persistent_context(account, headless=headless)

    async def close_session(self, account: Account, active_session: object) -> None:
        """Close a provider-owned active browser session."""
        provider = provider_manager.get_provider(account.platform)
        await provider.close_session(active_session)

    async def validate_session(self, account: Account) -> BrowserSessionResult:
        """Validate the stored session through the account provider."""
        provider = provider_manager.get_provider(account.platform)
        return await provider.validate_session(account)

    async def refresh_session(self, account: Account) -> BrowserSessionResult:
        """Refresh the stored session through the account provider."""
        provider = provider_manager.get_provider(account.platform)
        return await provider.refresh_session(account)

    async def logout(self, account: Account) -> BrowserSessionResult:
        """Clear provider session cookies and persisted storage state."""
        provider = provider_manager.get_provider(account.platform)
        return await provider.logout(account)

    async def delete_session(self, account: Account) -> BrowserSessionResult:
        """Delete provider storage and close any active manual login context."""
        provider = provider_manager.get_provider(account.platform)
        active_session = self._active_sessions.pop(str(account.id), None)
        if active_session is not None:
            await provider.close_session(active_session)
        return await provider.delete(account)

    async def open_browser(self, account: Account) -> BrowserSessionResult:
        """Open the provider browser profile."""
        provider = provider_manager.get_provider(account.platform)
        return await provider.open_browser(account)

    async def open_url(self, account: Account, url: str) -> BrowserSessionResult:
        """Open a URL in the provider browser profile."""
        provider = provider_manager.get_provider(account.platform)
        return await provider.open_url(account, url)

    async def open_home(self, account: Account) -> BrowserSessionResult:
        """Open the provider home page in the browser profile."""
        provider = provider_manager.get_provider(account.platform)
        return await provider.open_home(account)

    async def restart_browser(self, account: Account) -> BrowserSessionResult:
        """Clear session cookies and reopen the provider browser profile."""
        await self.logout(account)
        return await self.open_browser(account)


browser_manager = BrowserManager()
