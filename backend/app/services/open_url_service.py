from __future__ import annotations

from dataclasses import dataclass

from app.models.account import Account


@dataclass
class OpenUrlResult:
    account: str
    success: bool
    reason: str | None = None


class OpenUrlService:
    """Legacy placeholder after browser runtime extraction."""

    async def open_url(self, account: Account, target_url: str) -> OpenUrlResult:
        """Reject backend URL opening because provider runtime lives in the agent."""
        return OpenUrlResult(account=account.nickname, success=False, reason="automation_agent_required")
