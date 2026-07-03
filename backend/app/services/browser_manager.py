from __future__ import annotations

import asyncio
from pathlib import Path

from app.models.account import Account
from app.services.browser_sessions import browser_session_provider_registry
from app.services.browser_sessions.base import BrowserSessionResult


class BrowserManager:
    def locate_storage(self, account: Account) -> Path:
        provider = browser_session_provider_registry.get(account.platform)
        return provider.get_storage_directory(account)

    def locate_profile(self, account: Account) -> Path:
        provider = browser_session_provider_registry.get(account.platform)
        return provider.get_profile_directory(account)

    async def create_session(self, account: Account) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        return await asyncio.to_thread(provider.create_session, account)

    async def finish_session(self, account: Account) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        return await asyncio.to_thread(provider.finish_session, account)

    async def validate_session(self, account: Account) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        return await asyncio.to_thread(provider.validate, account)

    async def refresh_session(self, account: Account) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        return await asyncio.to_thread(provider.refresh, account)

    async def logout(self, account: Account) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        return await asyncio.to_thread(provider.logout, account)

    async def delete_session(self, account: Account) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        return await asyncio.to_thread(provider.delete, account)

    async def open_browser(self, account: Account) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        return await asyncio.to_thread(provider.open_browser, account)

    async def open_url(self, account: Account, url: str) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        return await asyncio.to_thread(provider.open_url, account, url)

    async def open_home(self, account: Account) -> BrowserSessionResult:
        provider = browser_session_provider_registry.get(account.platform)
        return await asyncio.to_thread(provider.open_home, account)

    async def restart_browser(self, account: Account) -> BrowserSessionResult:
        await self.logout(account)
        return await self.open_browser(account)
