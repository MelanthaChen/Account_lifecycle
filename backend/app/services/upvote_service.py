from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.repositories.account_repository import AccountRepository
from app.services.browser_manager import browser_manager

logger = logging.getLogger(__name__)


@dataclass
class UpvoteExecutionResult:
    account: str
    opened: bool
    clicked: bool
    verified: bool
    reason: str | None = None


class UpvoteService:
    """Executes sequential Reddit upvote attempts through existing persistent sessions."""

    def __init__(self, session: AsyncSession) -> None:
        self.accounts = AccountRepository(session)
        self.browser_manager = browser_manager

    async def open_target_for_accounts(
        self,
        *,
        account_ids: list[UUID],
        target_url: str,
    ) -> list[UpvoteExecutionResult]:
        """Run an upvote attempt for each selected account sequentially."""
        results: list[UpvoteExecutionResult] = []
        for account_id in account_ids:
            account = await self.accounts.get(account_id)
            if account is None:
                results.append(
                    UpvoteExecutionResult(
                        account=str(account_id),
                        opened=False,
                        clicked=False,
                        verified=False,
                        reason="account_not_found",
                    )
                )
                continue

            try:
                results.append(await self._execute_for_account(account, target_url))
            except Exception:
                logger.exception("Upvote execution failed for account %s.", account.nickname)
                results.append(
                    UpvoteExecutionResult(
                        account=account.nickname,
                        opened=False,
                        clicked=False,
                        verified=False,
                        reason="navigation_failed",
                    )
                )
        return results

    async def _execute_for_account(self, account: Account, target_url: str) -> UpvoteExecutionResult:
        state_path = self._get_state_path(account)
        if not state_path.exists():
            return UpvoteExecutionResult(
                account=account.nickname,
                opened=False,
                clicked=False,
                verified=False,
                reason="login_required",
            )

        logger.info("Opening browser for %s...", account.nickname)
        active_session = await self.browser_manager.open_persistent_context(
            account,
            headless=not account.launch_visible_browser,
        )
        try:
            context = active_session.context
            await self._restore_storage_state(context, state_path)
            page = await context.new_page()
            logger.info("Opening Reddit URL...")
            try:
                await page.goto(target_url, wait_until="domcontentloaded", timeout=60_000)
                try:
                    await page.wait_for_load_state("networkidle", timeout=15_000)
                except Exception:
                    logger.info("Reddit page did not reach networkidle before timeout; continuing after DOM load.")
            except Exception:
                logger.exception("Navigation failed for account %s.", account.nickname)
                return UpvoteExecutionResult(
                    account=account.nickname,
                    opened=False,
                    clicked=False,
                    verified=False,
                    reason="navigation_failed",
                )

            if await self._login_required(page, context):
                return UpvoteExecutionResult(
                    account=account.nickname,
                    opened=False,
                    clicked=False,
                    verified=False,
                    reason="login_required",
                )

            logger.info("Finding Upvote button...")
            button = await self._find_upvote_button(page)
            if button is None:
                return UpvoteExecutionResult(
                    account=account.nickname,
                    opened=True,
                    clicked=False,
                    verified=False,
                    reason="button_not_found",
                )

            logger.info("Clicking Upvote button...")
            try:
                pre_click_active = await self._is_vote_active(button)
                await button.scroll_into_view_if_needed(timeout=5_000)
                await button.wait_for(state="visible", timeout=5_000)
                await button.click(timeout=5_000)
            except Exception:
                logger.exception("Upvote click failed for account %s.", account.nickname)
                return UpvoteExecutionResult(
                    account=account.nickname,
                    opened=True,
                    clicked=False,
                    verified=False,
                    reason="click_failed",
                )

            logger.info("Verifying Upvote action...")
            await page.wait_for_timeout(500)
            verified = await self._verify_clicked(button, pre_click_active)
            return UpvoteExecutionResult(
                account=account.nickname,
                opened=True,
                clicked=True,
                verified=verified,
                reason=None if verified else "verification_failed",
            )
        finally:
            logger.info("Closing browser...")
            await self.browser_manager.close_session(account, active_session)

    async def _get_account(self, account_id: UUID) -> Account:
        account = await self.accounts.get(account_id)
        if account is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found")
        return account

    def _get_state_path(self, account: Account) -> Path:
        if account.session_path:
            return Path(account.session_path)
        return self.browser_manager.locate_storage(account) / "storage_state.json"

    @staticmethod
    async def _restore_storage_state(context: Any, state_path: Path) -> None:
        with state_path.open() as state_file:
            state = json.load(state_file)
        cookies = state.get("cookies") or []
        if cookies:
            await context.add_cookies(cookies)

    @staticmethod
    async def _login_required(page: Any, context: Any) -> bool:
        current_url = page.url.lower()
        if "/login" in current_url or "login.reddit.com" in current_url:
            return True
        cookies = await context.cookies("https://www.reddit.com/")
        return not any(cookie.get("name") in {"reddit_session", "token_v2"} for cookie in cookies)

    async def _find_upvote_button(self, page: Any) -> Any | None:
        selectors = [
            'button[aria-label*="upvote" i]',
            'button[aria-label*="up vote" i]',
            'button[aria-pressed][aria-label*="up" i]',
            'button[aria-checked][aria-label*="up" i]',
            'shreddit-post button[aria-label*="upvote" i]',
            'shreddit-post button[aria-pressed][aria-label*="up" i]',
            'button:has([icon-name*="upvote" i])',
            'button:has(svg[icon-name*="upvote" i])',
            '[role="button"][aria-label*="upvote" i]',
            '[data-testid*="upvote" i]',
            'faceplate-number button[aria-label*="up" i]',
        ]
        for selector in selectors:
            locator = page.locator(selector)
            count = await locator.count()
            for index in range(count):
                candidate = locator.nth(index)
                if await self._is_clickable(candidate):
                    return candidate
        return None

    @staticmethod
    async def _is_clickable(locator: Any) -> bool:
        try:
            return await locator.is_visible(timeout=750) and await locator.is_enabled(timeout=750)
        except Exception:
            return False

    async def _verify_clicked(self, locator: Any, pre_click_active: bool | None) -> bool:
        post_click_active = await self._is_vote_active(locator)
        if pre_click_active is False and post_click_active is True:
            return True
        return post_click_active is True

    @staticmethod
    async def _is_vote_active(locator: Any) -> bool | None:
        try:
            return await locator.evaluate(
                """(element) => {
                    const explicitState =
                        element.getAttribute("aria-pressed") ??
                        element.getAttribute("aria-checked") ??
                        element.getAttribute("active") ??
                        element.getAttribute("data-pressed") ??
                        element.getAttribute("data-state");
                    if (explicitState) {
                        const normalized = explicitState.toLowerCase();
                        if (["true", "on", "active", "checked", "selected"].includes(normalized)) {
                            return true;
                        }
                        if (["false", "off", "inactive", "unchecked"].includes(normalized)) {
                            return false;
                        }
                    }

                    const text = [
                        element.className?.toString() ?? "",
                        ...Array.from(element.querySelectorAll("*")).map((node) =>
                            node.className?.toString() ?? ""
                        ),
                        ...Array.from(element.querySelectorAll("*")).map((node) =>
                            Array.from(node.attributes ?? []).map((attribute) => attribute.value).join(" ")
                        ),
                    ].join(" ").toLowerCase();

                    if (/upvoted|upvote-active|selected|pressed|text-brand|text-orange|text-red/.test(text)) {
                        return true;
                    }
                    return null;
                }"""
            )
        except Exception:
            return None
