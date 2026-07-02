from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.activity_repository import ActivityRepository
from app.services.account_service import AccountService


class ActivityService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.accounts = AccountService(session)
        self.activity = ActivityRepository(session)

    async def list_posts(self, account_id: UUID, limit: int = 50):
        await self.accounts.get_account(account_id)
        return await self.activity.list_posts(account_id, limit)

    async def list_comments(self, account_id: UUID, limit: int = 50):
        await self.accounts.get_account(account_id)
        return await self.activity.list_comments(account_id, limit)
