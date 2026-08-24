from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.models.account import Account

BehaviorSession = Any


@dataclass
class BehaviorResult:
    success: bool
    reason: str | None = None
    detail: str | None = None


class BehaviorService:
    """Legacy placeholder after browser runtime extraction."""

    async def start(self, account: Account) -> BehaviorSession:
        """Reject backend behavior execution."""
        raise RuntimeError("Behavior runtime is owned by the automation agent")

    async def close(self, session: BehaviorSession | None) -> None:
        """No-op because backend does not own behavior sessions."""
        return None

    async def open_url(self, session: BehaviorSession, target_url: str) -> BehaviorResult:
        """Reject backend behavior execution."""
        raise RuntimeError("Behavior runtime is owned by the automation agent")

    async def wait(self, config: dict[str, Any]) -> BehaviorResult:
        """Reject backend behavior execution."""
        raise RuntimeError("Behavior runtime is owned by the automation agent")

    async def scroll(self, session: BehaviorSession, config: dict[str, Any]) -> BehaviorResult:
        """Reject backend behavior execution."""
        raise RuntimeError("Behavior runtime is owned by the automation agent")

    async def open_post(self, session: BehaviorSession) -> BehaviorResult:
        """Reject backend behavior execution."""
        raise RuntimeError("Behavior runtime is owned by the automation agent")

    async def back(self, session: BehaviorSession) -> BehaviorResult:
        """Reject backend behavior execution."""
        raise RuntimeError("Behavior runtime is owned by the automation agent")
