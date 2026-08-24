from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from browser_sessions.base import BrowserSessionResult
from providers.base import ProviderActionResult, ProviderProfileData
from providers.reddit.actions import RedditActions
from providers.reddit.browser import BehaviorSession, RedditBrowser
from providers.reddit.profile import RedditProfileService
from providers.reddit.session import RedditSessionProvider
from runtime_types import AccountLike, Platform, WorkflowActionType

logger = logging.getLogger(__name__)


class RedditProvider:
    """Provider facade for all Reddit-specific runtime behavior."""

    platform_name = Platform.REDDIT
    display_name = "Reddit"

    def __init__(self) -> None:
        self.session = RedditSessionProvider()
        self.profile = RedditProfileService(self.session)
        self.actions = RedditActions(self.session)
        self.browser = RedditBrowser(self.session)
        self.home_url = self.session.home_url
        self.login_url = self.session.login_url

    def get_storage_directory(self, account: AccountLike) -> Path:
        """Return the account storage directory."""
        return self.session.get_storage_directory(account)

    def get_profile_directory(self, account: AccountLike) -> Path:
        """Return the persistent browser profile directory."""
        return self.session.get_profile_directory(account)

    async def create_session(self, account: AccountLike) -> BrowserSessionResult:
        """Start a manual Reddit login session."""
        return await self.session.create_session(account)

    async def finish_session(
        self,
        account: AccountLike,
        active_session: object | None = None,
    ) -> BrowserSessionResult:
        """Persist storage state from the active manual login browser."""
        return await self.session.finish_session(account, active_session)

    async def validate_session(self, account: AccountLike) -> BrowserSessionResult:
        """Validate the Reddit browser session."""
        return await self.session.validate(account)

    async def refresh_session(self, account: AccountLike) -> BrowserSessionResult:
        """Refresh the Reddit browser session."""
        return await self.session.refresh(account)

    async def delete_session(self, account: AccountLike) -> BrowserSessionResult:
        """Delete Reddit session storage."""
        return await self.session.delete(account)

    async def logout(self, account: AccountLike) -> BrowserSessionResult:
        """Clear Reddit cookies and storage state."""
        return await self.session.logout(account)

    async def close_session(self, active_session: object) -> None:
        """Close a Reddit browser session."""
        await self.session.close_session(active_session)

    async def open_persistent_context(self, account: AccountLike, *, headless: bool) -> object:
        """Open a Reddit persistent Chromium context."""
        return await self.session.open_persistent_context(account, headless=headless)

    async def open_browser(self, account: AccountLike) -> BrowserSessionResult:
        """Open the account browser profile."""
        return await self.session.open_browser(account)

    async def open_home(self, account: AccountLike) -> BrowserSessionResult:
        """Open Reddit home."""
        return await self.session.open_home(account)

    async def open_url(self, account: AccountLike, url: str) -> BrowserSessionResult:
        """Open a URL in the Reddit browser profile."""
        return await self.session.open_url(account, url)

    async def sync_profile(self, account: AccountLike) -> ProviderProfileData:
        """Scrape the Reddit profile."""
        return await self.profile.sync_profile(account)

    async def health_check(self, account: AccountLike) -> dict[str, Any]:
        """Return provider-specific health signals derived from stored account data."""
        return {
            "profile_username": bool(account.reddit_username),
            "post_karma": account.karma_post,
            "comment_karma": account.karma_comment,
            "email_verified": account.verified_email is True,
        }

    async def start_behavior_session(self, account: AccountLike) -> BehaviorSession:
        """Open a reusable browser session for workflow behavior steps."""
        return await self.browser.start(account)

    async def close_behavior_session(self, session: BehaviorSession | None) -> None:
        """Close a reusable workflow browser session."""
        await self.browser.close(session)

    async def execute_action(
        self,
        account: AccountLike,
        action_type: WorkflowActionType,
        *,
        target_url: str | None = None,
        config: dict[str, Any] | None = None,
        session: Any | None = None,
    ) -> ProviderActionResult:
        """Execute one supported Reddit action."""
        if action_type == WorkflowActionType.COMMENT:
            return await self._comment(account, target_url=target_url, config=config, session=session)

        if action_type == WorkflowActionType.UPVOTE:
            if target_url is None:
                return ProviderActionResult(account=account.nickname, reason="target_url_required")
            result = await self.actions.upvote(account, target_url)
            return ProviderActionResult(
                account=result.account,
                opened=result.opened,
                clicked=result.clicked,
                verified=result.verified,
                success=result.opened and result.clicked,
                reason=result.reason,
                detail=result.detail,
                metadata=result.metadata,
            )

        if action_type in self.supported_behaviors():
            if session is None:
                return ProviderActionResult(
                    account=account.nickname,
                    success=False,
                    reason="browser_unavailable",
                )
            return await self.browser.execute(
                action_type.value,
                session=session,
                target_url=target_url,
                config=config,
            )

        return ProviderActionResult(
            account=account.nickname,
            success=False,
            reason="unsupported_action",
        )

    def supported_actions(self) -> set[WorkflowActionType]:
        """Return workflow actions supported by the Reddit provider."""
        return {
            WorkflowActionType.OPEN_URL,
            WorkflowActionType.WAIT,
            WorkflowActionType.SCROLL,
            WorkflowActionType.OPEN_POST,
            WorkflowActionType.BACK,
            WorkflowActionType.COMMENT,
            WorkflowActionType.UPVOTE,
        }

    def supported_behaviors(self) -> set[WorkflowActionType]:
        """Return browser-session workflow actions supported by Reddit."""
        return {
            WorkflowActionType.OPEN_URL,
            WorkflowActionType.WAIT,
            WorkflowActionType.SCROLL,
            WorkflowActionType.OPEN_POST,
            WorkflowActionType.BACK,
        }

    async def _comment(
        self,
        account: AccountLike,
        *,
        target_url: str | None,
        config: dict[str, Any] | None,
        session: Any | None,
    ) -> ProviderActionResult:
        comment_text = str((config or {}).get("comment_text") or "").strip()
        if not comment_text:
            return ProviderActionResult(
                account=account.nickname,
                success=False,
                reason="comment_text_required",
            )

        if session is not None:
            page = session.page
            context = session.active_session.context
            if target_url and page.url == "about:blank":
                opened = await self._navigate_comment_target(page, target_url)
                if not opened:
                    return ProviderActionResult(
                        account=account.nickname,
                        opened=False,
                        success=False,
                        reason="navigation_failed",
                    )
            if await self._login_required(page, context):
                return ProviderActionResult(
                    account=account.nickname,
                    opened=False,
                    success=False,
                    reason="login_required",
                )
            return await self._submit_comment(page, account=account, comment_text=comment_text)

        if target_url is None:
            return ProviderActionResult(
                account=account.nickname,
                success=False,
                reason="target_url_required",
            )
        state_path = self.session.get_state_path(account)
        if not state_path.exists():
            return ProviderActionResult(
                account=account.nickname,
                opened=False,
                success=False,
                reason="login_required",
            )

        logger.info("Opening browser for comment action: %s", account.nickname)
        active_session = await self.session.open_persistent_context(account, headless=not account.launch_visible_browser)
        try:
            context = active_session.context
            await self._restore_storage_state(context, state_path)
            page = context.pages[0] if context.pages else await context.new_page()
            opened = await self._navigate_comment_target(page, target_url)
            if not opened:
                return ProviderActionResult(
                    account=account.nickname,
                    opened=False,
                    success=False,
                    reason="navigation_failed",
                )
            if await self._login_required(page, context):
                return ProviderActionResult(
                    account=account.nickname,
                    opened=False,
                    success=False,
                    reason="login_required",
                )
            return await self._submit_comment(page, account=account, comment_text=comment_text)
        finally:
            await self.session.close_session(active_session)

    @staticmethod
    async def _navigate_comment_target(page: Any, target_url: str) -> bool:
        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60_000)
            try:
                await page.wait_for_load_state("networkidle", timeout=15_000)
            except Exception:
                logger.info("Reddit page did not reach networkidle before timeout; continuing after DOM load.")
        except Exception:
            logger.exception("Comment navigation failed.")
            return False
        return True

    async def _submit_comment(self, page: Any, *, account: AccountLike, comment_text: str) -> ProviderActionResult:
        logger.info("Finding Reddit comment editor for %s...", account.nickname)
        editor = await self._find_comment_editor(page)
        if editor is None:
            return ProviderActionResult(
                account=account.nickname,
                opened=True,
                clicked=False,
                success=False,
                reason="comment_editor_not_found",
            )

        logger.info("Filling Reddit comment editor for %s...", account.nickname)
        try:
            await editor.scroll_into_view_if_needed(timeout=5_000)
            await editor.wait_for(state="visible", timeout=5_000)
            await editor.click(timeout=5_000)
            await self._fill_comment_editor(page, editor, comment_text)
        except Exception:
            logger.exception("Comment editor fill failed for account %s.", account.nickname)
            return ProviderActionResult(
                account=account.nickname,
                opened=True,
                clicked=False,
                success=False,
                reason="comment_editor_failed",
            )

        logger.info("Finding Reddit comment submit button for %s...", account.nickname)
        submit_button = await self._find_comment_submit_button(page)
        if submit_button is None:
            return ProviderActionResult(
                account=account.nickname,
                opened=True,
                clicked=False,
                success=False,
                reason="submit_button_not_found",
            )

        logger.info("Submitting Reddit comment for %s...", account.nickname)
        try:
            await submit_button.scroll_into_view_if_needed(timeout=5_000)
            await submit_button.wait_for(state="visible", timeout=5_000)
            await submit_button.click(timeout=5_000)
        except Exception:
            logger.exception("Comment submit failed for account %s.", account.nickname)
            return ProviderActionResult(
                account=account.nickname,
                opened=True,
                clicked=False,
                success=False,
                reason="submit_failed",
            )

        await page.wait_for_timeout(1_500)
        verified = await self._verify_comment_posted(page, comment_text)
        return ProviderActionResult(
            account=account.nickname,
            opened=True,
            clicked=True,
            verified=verified,
            success=verified,
            reason=None if verified else "verification_failed",
            detail="Submitted and verified" if verified else "Submitted; verification failed",
            metadata={"comment_length": len(comment_text)},
        )

    async def _find_comment_editor(self, page: Any) -> Any | None:
        selectors = [
            'textarea[name="comment"]',
            'textarea[placeholder*="comment" i]',
            'textarea[aria-label*="comment" i]',
            'div[contenteditable="true"][role="textbox"]',
            'div[contenteditable="true"][aria-label*="comment" i]',
            'shreddit-composer div[contenteditable="true"]',
            'faceplate-form div[contenteditable="true"]',
            'comment-composer-host div[contenteditable="true"]',
            '[slot="comment"] div[contenteditable="true"]',
            '[role="textbox"][contenteditable="true"]',
        ]
        for selector in selectors:
            locator = page.locator(selector)
            count = await locator.count()
            for index in range(count):
                candidate = locator.nth(index)
                if await self._is_clickable(candidate):
                    return candidate
        return None

    async def _find_comment_submit_button(self, page: Any) -> Any | None:
        selectors = [
            'button[type="submit"]:has-text("Comment")',
            'button[type="submit"]:has-text("Reply")',
            'button:has-text("Comment")',
            'button:has-text("Reply")',
            'shreddit-composer button[type="submit"]',
            'faceplate-form button[type="submit"]',
            '[slot="submit-button"] button',
            'button[aria-label*="comment" i]',
            'button[aria-label*="reply" i]',
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
    async def _fill_comment_editor(page: Any, editor: Any, comment_text: str) -> None:
        tag_name = await editor.evaluate("(element) => element.tagName.toLowerCase()")
        if tag_name in {"textarea", "input"}:
            await editor.fill(comment_text)
            return
        await page.keyboard.insert_text(comment_text)

    @staticmethod
    async def _verify_comment_posted(page: Any, comment_text: str) -> bool:
        snippet = " ".join(comment_text.split())[:80]
        if not snippet:
            return False
        try:
            locator = page.get_by_text(snippet, exact=False)
            count = await locator.count()
            for index in range(count):
                if await locator.nth(index).is_visible(timeout=750):
                    return True
        except Exception:
            return False
        return False

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
        return not any(cookie.get("name") == "reddit_session" and cookie.get("value") for cookie in cookies)

    @staticmethod
    async def _is_clickable(locator: Any) -> bool:
        try:
            return await locator.is_visible(timeout=750) and await locator.is_enabled(timeout=750)
        except Exception:
            return False
