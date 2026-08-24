from __future__ import annotations

import json
import logging
from pathlib import Path
from time import time
from typing import Any

from browser_sessions.base import BrowserSessionResult
from providers.base import ProviderActionResult, ProviderProfileData
from providers.reddit.actions import RedditActions
from providers.reddit.browser import BehaviorSession, RedditBrowser
from providers.reddit.profile import RedditProfileService
from providers.reddit.session import RedditSessionProvider
from runtime_types import AccountLike, Platform, WorkflowActionType

logger = logging.getLogger(__name__)

COMMENT_EDITOR_SELECTORS = [
    'textarea[name="comment"]',
    'textarea[placeholder*="comment" i]',
    'textarea[aria-label*="comment" i]',
    'textarea[data-testid*="comment" i]',
    '[data-testid*="comment" i] textarea',
    'div[contenteditable="true"][role="textbox"]',
    'div[role="textbox"][contenteditable="true"]',
    'div[contenteditable="true"][aria-label*="comment" i]',
    'div[data-testid*="comment" i][contenteditable="true"]',
    '[data-testid*="comment" i] div[contenteditable="true"]',
    '.ProseMirror[contenteditable="true"]',
    '.DraftEditor-editorContainer div[contenteditable="true"]',
    '.public-DraftEditor-content[contenteditable="true"]',
    'shreddit-composer div[contenteditable="true"]',
    'shreddit-comment-composer div[contenteditable="true"]',
    'comment-composer-host div[contenteditable="true"]',
    'faceplate-form div[contenteditable="true"]',
    '[slot="comment"] div[contenteditable="true"]',
    '[role="textbox"][contenteditable="true"]',
    '[contenteditable="true"]',
]

COMMENT_ENTRYPOINT_SELECTORS = [
    'button:has-text("Add a comment")',
    '[role="button"]:has-text("Add a comment")',
    'button:has-text("Join the conversation")',
    '[role="button"]:has-text("Join the conversation")',
    'button[aria-label*="comment" i]',
    'button[data-testid*="comment" i]',
    '[data-testid*="comment" i]:has-text("Add a comment")',
    '[aria-label*="Add a comment" i]',
    '[placeholder*="Add a comment" i]',
    'shreddit-comment-composer',
    'comment-composer-host',
    'shreddit-composer',
]

COMMENT_SUBMIT_SELECTORS = [
    'button[type="submit"]:has-text("Comment")',
    'button[type="submit"]:has-text("Reply")',
    'button:has-text("Comment")',
    'button:has-text("Reply")',
    'shreddit-composer button[type="submit"]',
    'shreddit-comment-composer button[type="submit"]',
    'comment-composer-host button[type="submit"]',
    'faceplate-form button[type="submit"]',
    '[slot="submit-button"] button',
    'button[aria-label*="comment" i]',
    'button[aria-label*="reply" i]',
]


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
        diagnostics: list[dict[str, Any]] = []
        await self._wait_for_comment_page(page)
        editor = await self._find_comment_editor_with_retries(page, diagnostics)
        if editor is None:
            await self._open_collapsed_comment_editor(page, diagnostics)
            editor = await self._find_comment_editor_with_retries(page, diagnostics)
        if editor is None:
            diagnostics_path = await self._save_comment_diagnostics(
                page,
                account=account,
                reason="comment_editor_not_found",
                diagnostics=diagnostics,
            )
            return ProviderActionResult(
                account=account.nickname,
                opened=True,
                clicked=False,
                success=False,
                reason="comment_editor_not_found",
                detail=f"Diagnostics saved to {diagnostics_path}",
                metadata={"diagnostics_path": str(diagnostics_path), "selector_diagnostics": diagnostics},
            )

        logger.info("Filling Reddit comment editor for %s...", account.nickname)
        try:
            await editor.scroll_into_view_if_needed(timeout=5_000)
            await editor.wait_for(state="visible", timeout=5_000)
            await editor.click(timeout=5_000)
            await self._fill_comment_editor(page, editor, comment_text)
            if not await self._verify_editor_contains_text(page, editor, comment_text):
                raise RuntimeError("comment text was not inserted into the editor")
        except Exception:
            logger.exception("Comment editor fill failed for account %s.", account.nickname)
            diagnostics_path = await self._save_comment_diagnostics(
                page,
                account=account,
                reason="comment_editor_failed",
                diagnostics=diagnostics,
            )
            return ProviderActionResult(
                account=account.nickname,
                opened=True,
                clicked=False,
                success=False,
                reason="comment_editor_failed",
                detail=f"Diagnostics saved to {diagnostics_path}",
                metadata={"diagnostics_path": str(diagnostics_path), "selector_diagnostics": diagnostics},
            )

        logger.info("Finding Reddit comment submit button for %s...", account.nickname)
        submit_button = await self._find_comment_submit_button(page, diagnostics)
        if submit_button is None:
            diagnostics_path = await self._save_comment_diagnostics(
                page,
                account=account,
                reason="submit_button_not_found",
                diagnostics=diagnostics,
            )
            return ProviderActionResult(
                account=account.nickname,
                opened=True,
                clicked=False,
                success=False,
                reason="submit_button_not_found",
                detail=f"Diagnostics saved to {diagnostics_path}",
                metadata={"diagnostics_path": str(diagnostics_path), "selector_diagnostics": diagnostics},
            )

        logger.info("Submitting Reddit comment for %s...", account.nickname)
        try:
            await submit_button.scroll_into_view_if_needed(timeout=5_000)
            await submit_button.wait_for(state="visible", timeout=5_000)
            await submit_button.click(timeout=5_000)
        except Exception:
            logger.exception("Comment submit failed for account %s.", account.nickname)
            diagnostics_path = await self._save_comment_diagnostics(
                page,
                account=account,
                reason="submit_failed",
                diagnostics=diagnostics,
            )
            return ProviderActionResult(
                account=account.nickname,
                opened=True,
                clicked=False,
                success=False,
                reason="submit_failed",
                detail=f"Diagnostics saved to {diagnostics_path}",
                metadata={"diagnostics_path": str(diagnostics_path), "selector_diagnostics": diagnostics},
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

    async def _wait_for_comment_page(self, page: Any) -> None:
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=15_000)
        except Exception:
            logger.info("Comment page domcontentloaded wait timed out; continuing.")
        for selector in ["shreddit-post", 'a[href*="/comments/"]', "article", '[data-testid*="post" i]']:
            try:
                await page.locator(selector).first.wait_for(state="attached", timeout=5_000)
                return
            except Exception:
                logger.info("Post readiness selector not found yet: %s", selector)

    async def _find_comment_editor_with_retries(
        self,
        page: Any,
        diagnostics: list[dict[str, Any]],
    ) -> Any | None:
        for attempt in range(1, 5):
            logger.info("Comment editor discovery attempt %s.", attempt)
            editor = await self._find_comment_editor(page, diagnostics, attempt=attempt)
            if editor is not None:
                return editor
            await self._wait_for_comment_candidate(page)
        return None

    async def _find_comment_editor(
        self,
        page: Any,
        diagnostics: list[dict[str, Any]],
        *,
        attempt: int,
    ) -> Any | None:
        for selector in COMMENT_EDITOR_SELECTORS:
            result = await self._selector_state(page, selector, attempt=attempt)
            diagnostics.append({"kind": "editor", **result})
            logger.info(
                "Comment editor selector attempt=%s selector=%s count=%s visible=%s enabled=%s editable=%s",
                attempt,
                selector,
                result["count"],
                result["visible"],
                result["enabled"],
                result["editable"],
            )
            if result["count"] == 0:
                continue
            locator = page.locator(selector).first
            if await self._is_editable(locator):
                return locator
        return None

    async def _open_collapsed_comment_editor(self, page: Any, diagnostics: list[dict[str, Any]]) -> None:
        logger.info("Looking for collapsed Reddit comment entrypoint.")
        for selector in COMMENT_ENTRYPOINT_SELECTORS:
            result = await self._selector_state(page, selector, attempt=1)
            diagnostics.append({"kind": "entrypoint", **result})
            logger.info(
                "Comment entrypoint selector=%s count=%s visible=%s enabled=%s editable=%s",
                selector,
                result["count"],
                result["visible"],
                result["enabled"],
                result["editable"],
            )
            if result["count"] == 0:
                continue
            locator = page.locator(selector).first
            try:
                if await self._is_clickable(locator):
                    await locator.scroll_into_view_if_needed(timeout=5_000)
                    await locator.click(timeout=5_000)
                    await self._wait_for_comment_candidate(page)
                    return
            except Exception:
                logger.info("Collapsed comment entrypoint click failed for selector: %s", selector)

    async def _find_comment_submit_button(self, page: Any, diagnostics: list[dict[str, Any]]) -> Any | None:
        for selector in COMMENT_SUBMIT_SELECTORS:
            result = await self._selector_state(page, selector, attempt=1)
            diagnostics.append({"kind": "submit", **result})
            logger.info(
                "Comment submit selector=%s count=%s visible=%s enabled=%s editable=%s",
                selector,
                result["count"],
                result["visible"],
                result["enabled"],
                result["editable"],
            )
            if result["count"] == 0:
                continue
            locator = page.locator(selector).first
            if await self._is_clickable(locator):
                return locator
        return None

    @staticmethod
    async def _fill_comment_editor(page: Any, editor: Any, comment_text: str) -> None:
        tag_name = await editor.evaluate("(element) => element.tagName.toLowerCase()")
        if tag_name in {"textarea", "input"}:
            await editor.fill(comment_text)
            return
        await editor.evaluate(
            """(element) => {
                element.focus();
                if (element.textContent) {
                    element.textContent = "";
                }
            }"""
        )
        await page.keyboard.insert_text(comment_text)

    @staticmethod
    async def _verify_editor_contains_text(page: Any, editor: Any, comment_text: str) -> bool:
        expected = " ".join(comment_text.split())
        if not expected:
            return False
        try:
            value = await editor.evaluate(
                """(element) => {
                    if ("value" in element) {
                        return element.value || "";
                    }
                    return element.innerText || element.textContent || "";
                }"""
            )
            if expected in " ".join(str(value).split()):
                return True
        except Exception:
            logger.info("Direct editor text verification failed; falling back to page text.")
        try:
            await page.get_by_text(expected[:80], exact=False).first.wait_for(state="visible", timeout=3_000)
            return True
        except Exception:
            return False

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
    async def _wait_for_comment_candidate(page: Any) -> None:
        for selector in [*COMMENT_EDITOR_SELECTORS, *COMMENT_ENTRYPOINT_SELECTORS]:
            try:
                await page.locator(selector).first.wait_for(state="attached", timeout=1_000)
                return
            except Exception as exc:
                logger.debug("Comment candidate wait skipped selector=%s error=%s", selector, exc)
                continue
        try:
            await page.wait_for_load_state("networkidle", timeout=1_000)
        except Exception:
            logger.info("No comment candidate appeared during retry wait.")

    async def _selector_state(self, page: Any, selector: str, *, attempt: int) -> dict[str, Any]:
        locator = page.locator(selector)
        state: dict[str, Any] = {
            "attempt": attempt,
            "selector": selector,
            "count": 0,
            "visible": False,
            "enabled": False,
            "editable": False,
        }
        try:
            state["count"] = await locator.count()
        except Exception as exc:
            state["error"] = str(exc)
            return state

        if state["count"] == 0:
            return state

        first = locator.first
        try:
            state["visible"] = await first.is_visible(timeout=750)
        except Exception as exc:
            state["visible_error"] = str(exc)
        try:
            state["enabled"] = await first.is_enabled(timeout=750)
        except Exception as exc:
            state["enabled_error"] = str(exc)
        state["editable"] = await self._is_editable(first)
        return state

    @staticmethod
    async def _is_editable(locator: Any) -> bool:
        try:
            if not await locator.is_visible(timeout=750):
                return False
        except Exception:
            return False

        try:
            if await locator.is_editable(timeout=750):
                return True
        except Exception:
            logger.info("Playwright editability probe failed; checking DOM attributes.")

        try:
            return bool(
                await locator.evaluate(
                    """(element) => {
                        const editable = element.getAttribute("contenteditable");
                        const role = element.getAttribute("role");
                        const tagName = element.tagName.toLowerCase();
                        if (element.disabled || element.readOnly) {
                            return false;
                        }
                        return editable === "true" || role === "textbox" || tagName === "textarea" || tagName === "input";
                    }"""
                )
            )
        except Exception:
            return False

    async def _save_comment_diagnostics(
        self,
        page: Any,
        *,
        account: AccountLike,
        reason: str,
        diagnostics: list[dict[str, Any]],
    ) -> Path:
        diagnostics_root = self.session.get_storage_directory(account) / "diagnostics" / "comment_failure"
        diagnostics_path = diagnostics_root / f"{int(time())}_{reason}"
        diagnostics_path.mkdir(parents=True, exist_ok=True)

        screenshot_path = diagnostics_path / "page.png"
        html_path = diagnostics_path / "page.html"
        url_path = diagnostics_path / "url.txt"
        selectors_path = diagnostics_path / "selectors.json"

        try:
            await page.screenshot(path=str(screenshot_path), full_page=True)
        except Exception:
            logger.exception("Failed to save comment failure screenshot.")
        try:
            html_path.write_text(await page.content(), encoding="utf-8")
        except Exception:
            logger.exception("Failed to save comment failure HTML.")
        try:
            url_path.write_text(page.url, encoding="utf-8")
        except Exception:
            logger.exception("Failed to save comment failure URL.")
        selectors_path.write_text(json.dumps(diagnostics, indent=2, default=str), encoding="utf-8")

        logger.info("Saved Reddit comment diagnostics to %s", diagnostics_path)
        return diagnostics_path

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
