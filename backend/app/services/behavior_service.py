from __future__ import annotations

import asyncio
from dataclasses import dataclass
import random
from typing import Any

from app.models.account import Account
from app.models.enums import WorkflowActionType
from app.providers.manager import provider_manager

BehaviorSession = Any


@dataclass
class BehaviorResult:
    success: bool
    reason: str | None = None
    detail: str | None = None


class BehaviorService:
    """Delegates behavior workflow actions to account providers."""

    async def start(self, account: Account) -> BehaviorSession:
        """Open a provider-owned persistent browser context for workflow steps."""
        provider = provider_manager.get_provider(account.platform)
        return await provider.start_behavior_session(account)

    async def close(self, session: BehaviorSession | None) -> None:
        """Close an active provider behavior session if one exists."""
        if session is None:
            return
        provider = provider_manager.get_provider(session.account.platform)
        await provider.close_behavior_session(session)

    async def open_url(self, session: BehaviorSession, target_url: str) -> BehaviorResult:
        """Navigate the active provider page to a target URL."""
        return await self._execute(session, WorkflowActionType.OPEN_URL, target_url=target_url)

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
        """Perform provider-defined scroll behavior."""
        return await self._execute(session, WorkflowActionType.SCROLL, config=config)

    async def open_post(self, session: BehaviorSession) -> BehaviorResult:
        """Open one provider-defined visible post/content item."""
        return await self._execute(session, WorkflowActionType.OPEN_POST)

    async def back(self, session: BehaviorSession) -> BehaviorResult:
        """Navigate the active provider page back once."""
        return await self._execute(session, WorkflowActionType.BACK)

    async def _execute(
        self,
        session: BehaviorSession,
        action_type: WorkflowActionType,
        *,
        target_url: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> BehaviorResult:
        provider = provider_manager.get_provider(session.account.platform)
        result = await provider.execute_action(
            session.account,
            action_type,
            target_url=target_url,
            config=config,
            session=session,
        )
        return BehaviorResult(
            success=result.success,
            reason=result.reason,
            detail=result.detail,
        )
