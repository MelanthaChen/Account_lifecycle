from __future__ import annotations

import asyncio
from dataclasses import dataclass
import random
from typing import Any

from app.models.account import Account
from app.providers.base import ProviderActionResult
from app.providers.reddit.session import RedditSessionProvider


@dataclass
class BehaviorSession:
    account: Account
    active_session: Any
    page: Any


@dataclass
class BehaviorResult:
    success: bool
    reason: str | None = None
    detail: str | None = None


class RedditBrowser:
    """Executes Reddit browser behavior actions inside a persistent session."""

    def __init__(self, session_provider: RedditSessionProvider) -> None:
        self.session_provider = session_provider

    async def start(self, account: Account) -> BehaviorSession:
        """Open a persistent browser context for behavior workflow steps."""
        active_session = await self.session_provider.open_persistent_context(
            account,
            headless=not account.launch_visible_browser,
        )
        context = active_session.context
        page = await context.new_page()
        return BehaviorSession(account=account, active_session=active_session, page=page)

    async def close(self, session: BehaviorSession | None) -> None:
        """Close an active behavior session if one exists."""
        if session is None:
            return
        await self.session_provider.close_session(session.active_session)

    async def execute(
        self,
        action_type: str,
        *,
        session: BehaviorSession,
        target_url: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> ProviderActionResult:
        """Execute a behavior action and normalize it to a provider action result."""
        config = config or {}
        if action_type == "OPEN_URL":
            result = await self.open_url(session, target_url or "")
        elif action_type == "WAIT":
            result = await self.wait(config)
        elif action_type == "SCROLL":
            result = await self.scroll(session, config)
        elif action_type == "OPEN_POST":
            result = await self.open_post(session)
        elif action_type == "BACK":
            result = await self.back(session)
        else:
            return ProviderActionResult(
                account=session.account.nickname,
                success=False,
                reason="unsupported_action",
            )
        return ProviderActionResult(
            account=session.account.nickname,
            opened=result.success,
            success=result.success,
            reason=result.reason,
            detail=result.detail,
        )

    async def open_url(self, session: BehaviorSession, target_url: str) -> BehaviorResult:
        """Navigate the active browser page to a target URL."""
        try:
            await session.page.goto(target_url, wait_until="domcontentloaded", timeout=60_000)
            await self._wait_for_networkidle(session.page)
        except Exception:
            return BehaviorResult(success=False, reason="navigation_failed")
        return BehaviorResult(success=True)

    async def wait(self, config: dict[str, Any]) -> BehaviorResult:
        """Pause for a random duration configured by min_seconds and max_seconds."""
        min_seconds = float(config.get("min_seconds", 5))
        max_seconds = float(config.get("max_seconds", 12))
        if max_seconds < min_seconds:
            max_seconds = min_seconds
        duration = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(duration)
        return BehaviorResult(success=True, detail=f"{duration:.1f} sec")

    async def scroll(self, session: BehaviorSession, config: dict[str, Any]) -> BehaviorResult:
        """Perform random scroll operations on the active page."""
        count = int(config.get("count", 3))
        count = max(1, count)
        for _ in range(count):
            distance = random.randint(300, 900)
            wait_ms = random.randint(500, 2_000)
            await session.page.mouse.wheel(0, distance)
            await session.page.wait_for_timeout(wait_ms)
        return BehaviorResult(success=True, detail=f"{count} operations")

    async def open_post(self, session: BehaviorSession) -> BehaviorResult:
        """Open one visible non-promoted Reddit post from the current page."""
        links = await session.page.locator('a[href*="/comments/"]').evaluate_all(
            """(elements) => {
                const seen = new Set();
                return elements
                    .filter((element) => {
                        const rect = element.getBoundingClientRect();
                        const href = element.href || "";
                        const text = element.innerText || element.getAttribute("aria-label") || "";
                        const container = element.closest("article, shreddit-post, div");
                        const blob = [
                            href,
                            text,
                            container?.innerText || "",
                            container?.getAttribute("aria-label") || "",
                            container?.className?.toString() || ""
                        ].join(" ").toLowerCase();
                        return rect.width > 0 &&
                            rect.height > 0 &&
                            rect.bottom > 0 &&
                            rect.top < window.innerHeight &&
                            href.includes("/comments/") &&
                            !blob.includes("promoted") &&
                            !blob.includes("advertise") &&
                            !blob.includes("ad ");
                    })
                    .map((element) => ({
                        href: element.href,
                        title: (element.innerText || element.getAttribute("aria-label") || element.href).trim()
                    }))
                    .filter((item) => {
                        if (seen.has(item.href)) return false;
                        seen.add(item.href);
                        return true;
                    });
            }"""
        )
        if not links:
            return BehaviorResult(success=False, reason="post_not_found")
        choice = random.choice(links)
        try:
            await session.page.goto(choice["href"], wait_until="domcontentloaded", timeout=60_000)
            await self._wait_for_networkidle(session.page)
        except Exception:
            return BehaviorResult(success=False, reason="navigation_failed")
        title = choice.get("title") or choice["href"]
        return BehaviorResult(success=True, detail=f"Opened: {title[:120]}")

    async def back(self, session: BehaviorSession) -> BehaviorResult:
        """Navigate the active page back once."""
        try:
            await session.page.go_back(wait_until="domcontentloaded", timeout=60_000)
            await self._wait_for_networkidle(session.page)
        except Exception:
            return BehaviorResult(success=False, reason="navigation_failed")
        return BehaviorResult(success=True)

    @staticmethod
    async def _wait_for_networkidle(page: Any) -> None:
        try:
            await page.wait_for_load_state("networkidle", timeout=15_000)
        except Exception:
            pass
