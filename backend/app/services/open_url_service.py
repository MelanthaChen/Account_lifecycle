from __future__ import annotations

from dataclasses import dataclass

from app.models.account import Account


@dataclass
class OpenUrlResult:
    account: str
    success: bool
    reason: str | None = None


class OpenUrlService:
    """Backend guard for URL opening now owned by the Automation Agent."""

    async def open_url(self, account: Account, target_url: str) -> OpenUrlResult:
        """Reject backend URL opening because provider runtime lives in the agent."""
        return OpenUrlResult(account=account.nickname, success=False, reason="automation_agent_required")
