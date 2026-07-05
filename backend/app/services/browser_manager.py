from __future__ import annotations

from pathlib import Path

from app.models.account import Account
from app.services.browser_sessions import browser_session_provider_registry
from app.services.browser_sessions.base import BrowserSessionResult


class BrowserManager:
    def __init__(self) -> None:
        self._active_sessions: dict[str, object] = {}

    def locate_storage(self, account: Account) -> Path:
        provider = browser_session_provider_registry.get(account.platform)
        return provider.get_storage_directory(account)

    def locate_profile(self, account: Account) -> Path:
        provider = browser_session_provider_registry.get(account.platform)
        return provider.get_profile_directory(account)

    async def create_session(self, account: Account) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        active_session = self._active_sessions.pop(str(account.id), None)
        if active_session is not None:
            await provider.close_session(active_session)
        result = await provider.create_session(account)
        if result.active_session is not None:
            self._active_sessions[str(account.id)] = result.active_session
        return result

    async def finish_session(self, account: Account) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        active_session = self._active_sessions.pop(str(account.id), None)
        return await provider.finish_session(account, active_session)

    async def validate_session(self, account: Account) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        return await provider.validate(account)

    async def refresh_session(self, account: Account) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        return await provider.refresh(account)

    async def logout(self, account: Account) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        return await provider.logout(account)

    async def delete_session(self, account: Account) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        active_session = self._active_sessions.pop(str(account.id), None)
        if active_session is not None:
            await provider.close_session(active_session)
        return await provider.delete(account)

    async def open_browser(self, account: Account) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        return await provider.open_browser(account)

    async def open_url(self, account: Account, url: str) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        return await provider.open_url(account, url)

    async def open_home(self, account: Account) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        return await provider.open_home(account)

    async def restart_browser(self, account: Account) -> BrowserSessionResult:
        await self.logout(account)
        return await self.open_browser(account)


browser_manager = BrowserManager()
