from __future__ import annotations

from dataclasses import dataclass
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.account_repository import AccountRepository

logger = logging.getLogger(__name__)


@dataclass
class UpvoteExecutionResult:
    account: str
    opened: bool
    clicked: bool
    verified: bool
    reason: str | None = None


class UpvoteService:
    """Preserves the upvote API contract without launching backend browser automation."""

    def __init__(self, session: AsyncSession) -> None:
        self.accounts = AccountRepository(session)

    async def open_target_for_accounts(
        self,
        *,
        account_ids: list[UUID],
        target_url: str,
    ) -> list[UpvoteExecutionResult]:
        """Return non-executed results because provider actions run in the automation agent."""
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
            logger.info("Upvote request accepted for agent-owned runtime: %s", target_url)
            results.append(
                UpvoteExecutionResult(
                    account=account.nickname,
                    opened=False,
                    clicked=False,
                    verified=False,
                    reason="automation_agent_required",
                )
            )
        return results
