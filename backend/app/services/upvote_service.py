from __future__ import annotations

from dataclasses import dataclass
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.enums import WorkflowActionType
from app.providers.manager import provider_manager
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
    """Orchestrates sequential UPVOTE actions through account providers."""

    def __init__(self, session: AsyncSession) -> None:
        self.accounts = AccountRepository(session)

    async def open_target_for_accounts(
        self,
        *,
        account_ids: list[UUID],
        target_url: str,
    ) -> list[UpvoteExecutionResult]:
        """Run an upvote attempt for each selected account sequentially."""
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

            try:
                results.append(await self._execute_for_account(account, target_url))
            except Exception:
                logger.exception("Upvote execution failed for account %s.", account.nickname)
                results.append(
                    UpvoteExecutionResult(
                        account=account.nickname,
                        opened=False,
                        clicked=False,
                        verified=False,
                        reason="navigation_failed",
                    )
                )
        return results

    async def _execute_for_account(self, account: Account, target_url: str) -> UpvoteExecutionResult:
        provider = provider_manager.get_provider(account.platform)
        result = await provider.execute_action(
            account,
            WorkflowActionType.UPVOTE,
            target_url=target_url,
        )
        return UpvoteExecutionResult(
            account=result.account,
            opened=result.opened,
            clicked=result.clicked,
            verified=result.verified,
            reason=result.reason,
        )
