from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.enums import ActivityType
from app.core.platforms import provider_home_url
from app.repositories.account_repository import AccountRepository
from app.services.activity_service import ActivityService


class BrowserSessionService:
    """Preserves session API contracts after runtime extraction."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.accounts = AccountRepository(session)
        self.activity_service = ActivityService(session)

    async def create(self, account_id: UUID) -> Account:
        """Reject direct browser launch from the backend runtime."""
        account = await self._get_account(account_id)
        activity = await self.activity_service.record_start(
            account=account,
            activity_type=ActivityType.LOGIN,
            target_url=f"{provider_home_url(account.platform).rstrip('/')}/login/",
            title="Create browser session",
        )
        return await self._runtime_moved(activity)

    async def finish(self, account_id: UUID) -> Account:
        """Reject direct browser session persistence from the backend runtime."""
        account = await self._get_account(account_id)
        activity = await self.activity_service.record_start(
            account=account,
            activity_type=ActivityType.LOGIN,
            target_url=f"{provider_home_url(account.platform).rstrip('/')}/login/",
            title="Finish browser session",
        )
        return await self._runtime_moved(activity)

    async def validate(self, account_id: UUID) -> Account:
        """Reject direct browser validation from the backend runtime."""
        account = await self._get_account(account_id)
        activity = await self.activity_service.record_start(
            account=account,
            activity_type=ActivityType.VALIDATE_SESSION,
            title="Validate browser session",
        )
        return await self._runtime_moved(activity)

    async def refresh(self, account_id: UUID) -> Account:
        """Reject direct browser refresh from the backend runtime."""
        account = await self._get_account(account_id)
        activity = await self.activity_service.record_start(
            account=account,
            activity_type=ActivityType.REFRESH_SESSION,
            title="Refresh browser session",
        )
        return await self._runtime_moved(activity)

    async def delete(self, account_id: UUID) -> Account:
        """Reject direct browser session deletion from the backend runtime."""
        account = await self._get_account(account_id)
        activity = await self.activity_service.record_start(
            account=account,
            activity_type=ActivityType.DELETE_SESSION,
            title="Delete browser session",
        )
        return await self._runtime_moved(activity)

    async def open_browser(self, account_id: UUID) -> Account:
        """Reject direct browser launch from the backend runtime."""
        account = await self._get_account(account_id)
        activity = await self.activity_service.record_start(
            account=account,
            activity_type=ActivityType.OPEN_BROWSER,
            title="Open browser profile",
        )
        return await self._runtime_moved(activity)

    async def open_home(self, account_id: UUID) -> Account:
        """Reject direct provider home launch from the backend runtime."""
        account = await self._get_account(account_id)
        activity = await self.activity_service.record_start(
            account=account,
            activity_type=ActivityType.OPEN_HOME,
            target_url=provider_home_url(account.platform),
            title="Open provider home",
        )
        return await self._runtime_moved(activity)

    async def _get_account(self, account_id: UUID) -> Account:
        account = await self.accounts.get(account_id)
        if account is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found")
        return account

    async def _runtime_moved(self, activity):
        error = RuntimeError("Browser runtime is owned by the automation agent")
        await self.activity_service.record_failure(activity, error)
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, str(error))
