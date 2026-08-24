from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.enums import AutomationJobType
from app.repositories.account_repository import AccountRepository
from app.schemas.automation_job import AutomationJobCreate
from app.services.automation_job_service import AutomationJobService


class BrowserSessionService:
    """Queues browser session work for the standalone automation agent."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.accounts = AccountRepository(session)
        self.jobs = AutomationJobService(session)

    async def create(self, account_id: UUID) -> Account:
        return await self._enqueue(account_id, AutomationJobType.SESSION_LOGIN, "login_queued")

    async def finish(self, account_id: UUID) -> Account:
        return await self._enqueue(account_id, AutomationJobType.SESSION_VALIDATE, "validation_queued")

    async def validate(self, account_id: UUID) -> Account:
        return await self._enqueue(account_id, AutomationJobType.SESSION_VALIDATE, "validation_queued")

    async def refresh(self, account_id: UUID) -> Account:
        return await self._enqueue(account_id, AutomationJobType.SESSION_REFRESH, "refresh_queued")

    async def delete(self, account_id: UUID) -> Account:
        return await self._enqueue(account_id, AutomationJobType.SESSION_DELETE, "delete_queued")

    async def open_browser(self, account_id: UUID) -> Account:
        return await self._enqueue(account_id, AutomationJobType.OPEN_BROWSER, "open_browser_queued")

    async def open_home(self, account_id: UUID) -> Account:
        return await self._enqueue(account_id, AutomationJobType.OPEN_HOME, "open_home_queued")

    async def _enqueue(
        self,
        account_id: UUID,
        job_type: AutomationJobType,
        queued_status: str,
    ) -> Account:
        account = await self._get_account(account_id)
        account.session_status = queued_status
        await self.jobs.create_job(
            AutomationJobCreate(
                account_id=account.id,
                job_type=job_type,
            )
        )
        await self.session.refresh(account)
        return account

    async def _get_account(self, account_id: UUID) -> Account:
        account = await self.accounts.get(account_id)
        if account is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found")
        return account
