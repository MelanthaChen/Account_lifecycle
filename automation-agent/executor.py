from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from uuid import UUID

from config import AgentConfig
from providers.manager import provider_manager
from runtime_types import WorkflowActionType


class WorkflowExecutor:
    """Executes one queued workflow job with local provider runtime."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config

    async def execute_job(self, job: dict[str, Any]) -> dict[str, Any]:
        campaign = job["campaign"]
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
        storage_directory = account.get("storage_directory")
        browser_profile_path = account.get("browser_profile_path")
        if not storage_directory:
            storage_directory = str(self.config.profile_root / account["platform"] / account["username"])
        if not browser_profile_path:
            browser_profile_path = str(
                self.config.profile_root / account["platform"] / account["username"] / "profile"
            )
        return SimpleNamespace(
            **account,
            id=UUID(account["id"]),
            storage_directory=storage_directory,
            browser_profile_path=browser_profile_path,
            launch_visible_browser=not self.config.headless,
        )

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
