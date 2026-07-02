from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.repositories.account_repository import AccountRepository
from app.services.browser_sessions import browser_session_provider_registry
from app.services.browser_sessions.base import BrowserSessionResult


class BrowserSessionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.accounts = AccountRepository(session)

    async def login(self, account_id: UUID) -> Account:
        account = await self._get_account(account_id)
        provider = browser_session_provider_registry.get(account.platform)
        try:
            result = provider.login(account)
        except NotImplementedError as exc:
            raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, str(exc)) from exc
        return await self._apply_result(account, result)

    async def validate(self, account_id: UUID) -> Account:
        account = await self._get_account(account_id)
        provider = browser_session_provider_registry.get(account.platform)
        try:
            result = provider.validate(account)
        except NotImplementedError as exc:
            raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, str(exc)) from exc
        return await self._apply_result(account, result)

    async def refresh(self, account_id: UUID) -> Account:
        account = await self._get_account(account_id)
        provider = browser_session_provider_registry.get(account.platform)
        result = provider.refresh(account)
        return await self._apply_result(account, result)

    async def delete(self, account_id: UUID) -> Account:
        account = await self._get_account(account_id)
        provider = browser_session_provider_registry.get(account.platform)
        result = provider.delete(account)
        return await self._apply_result(account, result)

    async def _get_account(self, account_id: UUID) -> Account:
        account = await self.accounts.get(account_id)
        if account is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found")
        return account

    async def _apply_result(self, account: Account, result: BrowserSessionResult) -> Account:
        now = datetime.now(UTC)
        account.provider = account.provider or account.platform
        account.browser_profile = account.browser_profile or account.username

        if result.session_path is not None:
            account.session_path = result.session_path
        elif result.session_status == "missing":
            account.session_path = None

        if result.session_status is not None:
            account.session_status = result.session_status

        if result.last_login_changed:
            account.last_login = now

        if result.last_validation_changed:
            account.last_validation = now

        await self.session.commit()
        await self.session.refresh(account)
        return account
