from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.repositories.account_repository import AccountRepository
from app.repositories.activity_repository import ActivityRepository
from app.schemas.account import AccountAnalytics, AccountCreate, AccountUpdate


class AccountService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.accounts = AccountRepository(session)
        self.activity = ActivityRepository(session)

    async def list_accounts(self, search: str | None = None) -> list[Account]:
        return await self.accounts.list(search=search)

    async def get_account(self, account_id: UUID) -> Account:
        account = await self.accounts.get(account_id)
        if account is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found")
        return account

    async def create_account(self, payload: AccountCreate) -> Account:
        existing = await self.accounts.get_by_username(payload.reddit_username)
        if existing is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "Reddit username is already managed")
        account = Account(**payload.model_dump())
        await self.accounts.create(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def update_account(self, account_id: UUID, payload: AccountUpdate) -> Account:
        account = await self.get_account(account_id)
        values = payload.model_dump(exclude_unset=True)
        if "reddit_username" in values:
            existing = await self.accounts.get_by_username(values["reddit_username"])
            if existing is not None and existing.id != account_id:
                raise HTTPException(status.HTTP_409_CONFLICT, "Reddit username is already managed")
        for key, value in values.items():
            setattr(account, key, value)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def delete_account(self, account_id: UUID) -> None:
        account = await self.get_account(account_id)
        await self.accounts.delete(account)
        await self.session.commit()

    async def analytics(self, account_id: UUID) -> AccountAnalytics:
        await self.get_account(account_id)
        total_posts, total_comments, total_score = await self.accounts.totals(account_id)
        return AccountAnalytics(
            account_id=account_id,
            total_posts=total_posts,
            total_comments=total_comments,
            total_score=total_score,
            top_subreddits=await self.activity.top_subreddits(account_id),
            activity_by_day=await self.activity.activity_by_day(account_id),
        )
