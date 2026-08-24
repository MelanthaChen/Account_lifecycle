from __future__ import annotations

import asyncio
import contextlib
import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import UUID

from browser.browser_manager import browser_manager
from browser_sessions.base import BrowserSessionResult
from config import AgentConfig
from providers.manager import provider_manager
from runtime_types import WorkflowActionType

VALID_SESSION_STATUS = "valid"
REDDIT_AUTH_COOKIE = "reddit_session"
logger = logging.getLogger("automation-agent")


class WorkflowExecutor:
    """Executes one queued workflow job with local provider runtime."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config

    async def execute_job(self, job: dict[str, Any]) -> dict[str, Any]:
        job_type = str(job.get("job_type") or "WORKFLOW")
        if job_type != "WORKFLOW":
            return await self._execute_runtime_job(job, job_type)

        campaign = job["campaign"]
        if campaign is None:
            return {
                "success": False,
                "account_id": job["account_id"],
                "reason": "campaign_required",
            }
        account = self._account_object(job["account"])
        provider = provider_manager.get_provider(account.platform)
        behavior_session: Any | None = None
        step_results: list[dict[str, Any]] = []
        target_url = campaign["target_url"]

        try:
            for step in job["workflow_steps"]:
                action_type = WorkflowActionType(step["action_type"])
                config = dict(step.get("config") or {})
                if self._uses_behavior_session(action_type) and behavior_session is None:
                    behavior_session = await provider.start_behavior_session(account)
                if action_type == WorkflowActionType.UPVOTE and behavior_session is not None:
                    await provider.close_behavior_session(behavior_session)
                    behavior_session = None

                result = await self._execute_step(
                    provider=provider,
                    account=account,
                    campaign=campaign,
                    action_type=action_type,
                    config=config,
                    target_url=str(config.get("target_url") or target_url),
                    behavior_session=behavior_session,
                )
                step_results.append(result)
                if not result["success"]:
                    break
        finally:
            if behavior_session is not None:
                await provider.close_behavior_session(behavior_session)

        return {
            "success": all(step["success"] for step in step_results),
            "campaign_id": job["campaign_id"],
            "account_id": job["account_id"],
            "target_url": target_url,
            "steps": step_results,
        }

    async def _execute_runtime_job(self, job: dict[str, Any], job_type: str) -> dict[str, Any]:
        account = self._account_object(job["account"])
        if job_type == "UPVOTE":
            return await self._standalone_upvote(job, account)
        if job_type == "SESSION_LOGIN":
            return await self._session_login(job, account)
        if job_type == "SESSION_VALIDATE":
            result = await browser_manager.validate_session(account)
            return self._session_job_result(job, result, success=result.session_status == VALID_SESSION_STATUS)
        if job_type == "SESSION_REFRESH":
            result = await browser_manager.refresh_session(account)
            return self._session_job_result(job, result, success=result.session_status == VALID_SESSION_STATUS)
        if job_type == "SESSION_DELETE":
            result = await browser_manager.delete_session(account)
            return self._session_job_result(job, result, success=True)
        if job_type == "OPEN_BROWSER":
            result = await browser_manager.open_browser(account)
            return self._session_job_result(job, result, success=True)
        if job_type == "OPEN_HOME":
            result = await browser_manager.open_home(account)
            return self._session_job_result(job, result, success=True)
        if job_type == "PROFILE_SYNC":
            provider = provider_manager.get_provider(account.platform)
            profile = await provider.sync_profile(account)
            return {
                "success": True,
                "account_id": job["account_id"],
                "job_type": job_type,
                "profile": {
                    "display_name": profile.display_name,
                    "reddit_username": profile.provider_username,
                    "avatar_url": profile.avatar_url,
                    "karma_post": profile.karma_post,
                    "karma_comment": profile.karma_comment,
                    "cake_day": profile.cake_day,
                    "verified_email": profile.verified_email,
                    "is_nsfw": profile.is_nsfw,
                    "is_moderator": profile.is_moderator,
                    "is_gold": profile.is_gold,
                },
            }
        return {
            "success": False,
            "account_id": job["account_id"],
            "job_type": job_type,
            "reason": "unsupported_job_type",
        }

    async def _standalone_upvote(self, job: dict[str, Any], account: Any) -> dict[str, Any]:
        payload = job.get("result_json") if isinstance(job.get("result_json"), dict) else {}
        target_url = str(payload.get("target_url") or "").strip()
        logs = [{"message": f"Starting upvote job for {account.nickname}.", "level": "info"}]
        if not target_url:
            logs.append({"message": "Target URL is missing.", "level": "error"})
            return {
                "success": False,
                "account_id": job["account_id"],
                "job_type": "UPVOTE",
                "target_url": target_url,
                "logs": logs,
                "result": {
                    "account": account.nickname,
                    "opened": False,
                    "clicked": False,
                    "verified": False,
                    "reason": "target_url_required",
                },
            }

        provider = provider_manager.get_provider(account.platform)
        logs.extend(
            [
                {"message": f"Opening browser for {account.nickname}.", "level": "info"},
                {"message": "Opening Reddit URL.", "level": "info"},
                {"message": "Finding Upvote button.", "level": "info"},
                {"message": "Clicking.", "level": "info"},
                {"message": "Verifying.", "level": "info"},
            ]
        )
        result = await provider.execute_action(account, WorkflowActionType.UPVOTE, target_url=target_url)
        logs.append({"message": "Closing browser.", "level": "info"})
        if result.opened and result.clicked:
            logs.append(
                {
                    "message": "Upvote completed." if result.verified else "Upvote clicked; verification inconclusive.",
                    "level": "success" if result.success else "warning",
                }
            )
        else:
            logs.append({"message": result.reason or "Upvote failed.", "level": "error"})

        return {
            "success": result.success,
            "account_id": job["account_id"],
            "job_type": "UPVOTE",
            "target_url": target_url,
            "logs": logs,
            "result": {
                "account": result.account,
                "opened": result.opened,
                "clicked": result.clicked,
                "verified": result.verified,
                "reason": result.reason,
                "detail": result.detail,
                "metadata": result.metadata,
            },
        }

    async def _session_login(self, job: dict[str, Any], account: Any) -> dict[str, Any]:
        result = await browser_manager.create_session(account)
        active_session = result.active_session
        if active_session is None:
            return self._session_job_result(job, result, success=False, reason="browser_unavailable")

        authenticated = await self._wait_for_login(active_session)
        if not authenticated:
            cancel_result = await browser_manager.cancel_session(account)
            return self._session_job_result(
                job,
                cancel_result,
                success=False,
                reason="login_timeout_or_cancelled",
            )
        finish_result = await browser_manager.finish_session(account)
        success = authenticated and finish_result.session_status == VALID_SESSION_STATUS
        return self._session_job_result(
            job,
            finish_result,
            success=success,
            reason=None if success else "login_required",
        )

    async def _wait_for_login(self, active_session: Any) -> bool:
        context = active_session.context
        page = context.pages[0] if context.pages else await context.new_page()
        timeout_seconds = self.config.manual_login_timeout_seconds
        deadline = asyncio.get_running_loop().time() + timeout_seconds
        initial_cookie = await self._reddit_session_cookie_value(context)
        if initial_cookie:
            logger.info("Existing Reddit session cookie found; waiting for a refreshed manual login signal.")
        logger.info("Waiting up to %.0f seconds for Reddit manual login.", timeout_seconds)
        while asyncio.get_running_loop().time() < deadline:
            current_cookie = await self._reddit_session_cookie_value(context)
            if current_cookie and current_cookie != initial_cookie:
                logger.info("Detected authenticated Reddit session.")
                return True
            if all(item.is_closed() for item in context.pages):
                logger.info("Manual login browser was closed before authentication.")
                return False
            page = next((item for item in context.pages if not item.is_closed()), page)
            await self._wait_for_browser_login_event(page, max(0.1, min(10.0, deadline - asyncio.get_running_loop().time())))
        logger.info("Manual login timed out.")
        return False

    @staticmethod
    async def _reddit_session_cookie_value(context: Any) -> str | None:
        cookies = await context.cookies("https://www.reddit.com/")
        for cookie in cookies:
            if cookie.get("name") == REDDIT_AUTH_COOKIE and cookie.get("value"):
                return str(cookie["value"])
        return None

    @staticmethod
    async def _wait_for_browser_login_event(page: Any, timeout_seconds: float) -> None:
        tasks = [
            asyncio.create_task(page.wait_for_event("framenavigated", timeout=timeout_seconds * 1000)),
            asyncio.create_task(page.wait_for_event("load", timeout=timeout_seconds * 1000)),
            asyncio.create_task(page.wait_for_event("domcontentloaded", timeout=timeout_seconds * 1000)),
        ]
        try:
            done, pending = await asyncio.wait(tasks, timeout=timeout_seconds, return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
            for task in done:
                with contextlib.suppress(Exception):
                    await task
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()

    @staticmethod
    def _session_job_result(
        job: dict[str, Any],
        result: BrowserSessionResult,
        *,
        success: bool,
        reason: str | None = None,
    ) -> dict[str, Any]:
        return {
            "success": success,
            "account_id": job["account_id"],
            "job_type": job.get("job_type"),
            "reason": reason,
            "session": {
                "session_path": result.session_path,
                "storage_directory": result.storage_directory,
                "browser_profile_path": result.browser_profile_path,
                "session_status": result.session_status,
                "last_login_changed": result.last_login_changed,
                "last_validation_changed": result.last_validation_changed,
            },
        }

    async def _execute_step(
        self,
        *,
        provider: Any,
        account: Any,
        campaign: dict[str, Any],
        action_type: WorkflowActionType,
        config: dict[str, Any],
        target_url: str,
        behavior_session: Any | None,
    ) -> dict[str, Any]:
        if action_type == WorkflowActionType.COMMENT:
            comment_text = str(config.get("comment_text") or campaign.get("comment_text") or "").strip()
            if not comment_text:
                return self._step_result(action_type, success=False, reason="comment_text_required")
            result = await provider.execute_action(
                account,
                action_type,
                target_url=target_url,
                config={"comment_text": comment_text},
                session=behavior_session,
            )
        elif action_type == WorkflowActionType.UPVOTE:
            result = await provider.execute_action(account, action_type, target_url=target_url)
        else:
            result = await provider.execute_action(
                account,
                action_type,
                target_url=target_url,
                config=config,
                session=behavior_session,
            )
        return self._step_result(
            action_type,
            success=result.success,
            reason=result.reason,
            detail=result.detail,
            verified=result.verified,
        )

    def _account_object(self, account: dict[str, Any]) -> Any:
        default_storage = self.config.profile_root / account["platform"] / account["username"]
        storage_directory = self._local_path_or_default(account.get("storage_directory"), default_storage)
        browser_profile_path = self._local_path_or_default(
            account.get("browser_profile_path"),
            storage_directory / "profile",
        )
        values = dict(account)
        values.update(
            id=UUID(account["id"]),
            storage_directory=str(storage_directory),
            browser_profile_path=str(browser_profile_path),
            launch_visible_browser=not self.config.headless,
        )
        return SimpleNamespace(**values)

    def _local_path_or_default(self, value: str | None, default: Path) -> Path:
        if not value:
            return default
        candidate = Path(value)
        if not candidate.is_absolute():
            return self.config.profile_root / candidate
        try:
            candidate.resolve().relative_to(self.config.profile_root)
        except ValueError:
            return default
        return candidate

    @staticmethod
    def _uses_behavior_session(action_type: WorkflowActionType) -> bool:
        return action_type in {
            WorkflowActionType.OPEN_URL,
            WorkflowActionType.SCROLL,
            WorkflowActionType.OPEN_POST,
            WorkflowActionType.BACK,
            WorkflowActionType.COMMENT,
        }

    @staticmethod
    def _step_result(
        action_type: WorkflowActionType,
        *,
        success: bool,
        reason: str | None = None,
        detail: str | None = None,
        verified: bool | None = None,
    ) -> dict[str, Any]:
        return {
            "action_type": action_type.value,
            "success": success,
            "reason": reason,
            "detail": detail,
            "verified": verified,
        }
