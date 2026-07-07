from __future__ import annotations

from dataclasses import dataclass

from app.models.account import Account
from app.services.browser_manager import browser_manager


@dataclass
class OpenUrlResult:
    account: str
    success: bool
    reason: str | None = None


class OpenUrlService:
    def __init__(self) -> None:
        self.browser_manager = browser_manager

    async def open_url(self, account: Account, target_url: str) -> OpenUrlResult:
        active_session = await self.browser_manager.open_persistent_context(
            account,
            headless=not account.launch_visible_browser,
        )
        try:
            context = active_session.context
            page = await context.new_page()
            try:
                await page.goto(target_url, wait_until="domcontentloaded", timeout=60_000)
                try:
                    await page.wait_for_load_state("networkidle", timeout=15_000)
                except Exception:
                    pass
            except Exception:
                return OpenUrlResult(account=account.nickname, success=False, reason="navigation_failed")
            return OpenUrlResult(account=account.nickname, success=True)
        finally:
            await self.browser_manager.close_session(account, active_session)
