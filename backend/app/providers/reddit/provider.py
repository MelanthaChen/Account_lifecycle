from __future__ import annotations

from pathlib import Path
from typing import Any

from app.models.account import Account
from app.models.enums import Platform, WorkflowActionType
from app.providers.base import ProviderActionResult, ProviderProfileData
from app.providers.reddit.actions import RedditActions
from app.providers.reddit.browser import BehaviorSession, RedditBrowser
from app.providers.reddit.profile import RedditProfileService
from app.providers.reddit.session import RedditSessionProvider
from app.services.browser_sessions.base import BrowserSessionResult


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

    def get_storage_directory(self, account: Account) -> Path:
        """Return the account storage directory."""
        return self.session.get_storage_directory(account)

    def get_profile_directory(self, account: Account) -> Path:
        """Return the persistent browser profile directory."""
        return self.session.get_profile_directory(account)

    async def create_session(self, account: Account) -> BrowserSessionResult:
        """Start a manual Reddit login session."""
        return await self.session.create_session(account)

    async def finish_session(
        self,
        account: Account,
        active_session: object | None = None,
    ) -> BrowserSessionResult:
        """Persist storage state from the active manual login browser."""
        return await self.session.finish_session(account, active_session)

    async def validate_session(self, account: Account) -> BrowserSessionResult:
        """Validate the Reddit browser session."""
        return await self.session.validate(account)

    async def refresh_session(self, account: Account) -> BrowserSessionResult:
        """Refresh the Reddit browser session."""
        return await self.session.refresh(account)

    async def delete_session(self, account: Account) -> BrowserSessionResult:
        """Delete Reddit session storage."""
        return await self.session.delete(account)

    async def logout(self, account: Account) -> BrowserSessionResult:
        """Clear Reddit cookies and storage state."""
        return await self.session.logout(account)

    async def close_session(self, active_session: object) -> None:
        """Close a Reddit browser session."""
        await self.session.close_session(active_session)

    async def open_persistent_context(self, account: Account, *, headless: bool) -> object:
        """Open a Reddit persistent Chromium context."""
        return await self.session.open_persistent_context(account, headless=headless)

    async def open_browser(self, account: Account) -> BrowserSessionResult:
        """Open the account browser profile."""
        return await self.session.open_browser(account)

    async def open_home(self, account: Account) -> BrowserSessionResult:
        """Open Reddit home."""
        return await self.session.open_home(account)

    async def open_url(self, account: Account, url: str) -> BrowserSessionResult:
        """Open a URL in the Reddit browser profile."""
        return await self.session.open_url(account, url)

    async def sync_profile(self, account: Account) -> ProviderProfileData:
        """Scrape the Reddit profile."""
        return await self.profile.sync_profile(account)

    async def health_check(self, account: Account) -> dict[str, Any]:
        """Return provider-specific health signals derived from stored account data."""
        return {
            "profile_username": bool(account.reddit_username),
            "post_karma": account.karma_post,
            "comment_karma": account.karma_comment,
            "email_verified": account.verified_email is True,
        }

    async def start_behavior_session(self, account: Account) -> BehaviorSession:
        """Open a reusable browser session for workflow behavior steps."""
        return await self.browser.start(account)

    async def close_behavior_session(self, session: BehaviorSession | None) -> None:
        """Close a reusable workflow browser session."""
        await self.browser.close(session)

    async def execute_action(
        self,
        account: Account,
        action_type: WorkflowActionType,
        *,
        target_url: str | None = None,
        config: dict[str, Any] | None = None,
        session: Any | None = None,
    ) -> ProviderActionResult:
        """Execute one supported Reddit action."""
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
