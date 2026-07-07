from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.repositories.account_repository import AccountRepository
from app.services.browser_manager import browser_manager

logger = logging.getLogger(__name__)


class UpvoteExecutionResult:
    def __init__(self, *, account: str, opened: bool) -> None:
        self.account = account
        self.opened = opened


class UpvoteService:
    def __init__(self, session: AsyncSession) -> None:
        self.accounts = AccountRepository(session)
        self.browser_manager = browser_manager

    async def open_target_for_accounts(
        self,
        *,
        account_ids: list[UUID],
        target_url: str,
    ) -> list[UpvoteExecutionResult]:
        results: list[UpvoteExecutionResult] = []
        for account_id in account_ids:
            account = await self._get_account(account_id)
            logger.info("Opening browser for %s...", account.nickname)
            await self._open_target_for_account(account, target_url)
            logger.info("Opened Reddit URL successfully.")
            results.append(UpvoteExecutionResult(account=account.nickname, opened=True))
        return results

    async def _open_target_for_account(self, account: Account, target_url: str) -> None:
        state_path = self._get_state_path(account)
        if not state_path.exists():
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Missing storage_state.json for account {account.nickname}",
            )

        active_session = await self.browser_manager.open_persistent_context(account, headless=True)
        try:
            context = active_session.context
            await self._restore_storage_state(context, state_path)
            page = context.pages[0] if context.pages else await context.new_page()
            logger.info("Opening Reddit URL...")
            await page.goto(target_url, wait_until="networkidle")
        finally:
            logger.info("Closing browser...")
            await self.browser_manager.close_session(account, active_session)

    async def _get_account(self, account_id: UUID) -> Account:
        account = await self.accounts.get(account_id)
        if account is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found")
        return account

    def _get_state_path(self, account: Account) -> Path:
        if account.session_path:
            return Path(account.session_path)
        return self.browser_manager.locate_storage(account) / "storage_state.json"

    @staticmethod
    async def _restore_storage_state(context: Any, state_path: Path) -> None:
        with state_path.open() as state_file:
            state = json.load(state_file)
        cookies = state.get("cookies") or []
        if cookies:
            await context.add_cookies(cookies)
