from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.enums import Platform


class AccountRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self, *, search: str | None = None) -> list[Account]:
        query: Select[tuple[Account]] = select(Account).order_by(Account.updated_at.desc())
        if search:
            term = f"%{search.lower()}%"
            query = query.where(
                func.lower(Account.nickname).like(term)
                | func.lower(Account.username).like(term)
            )
        return list((await self.session.scalars(query)).all())

    async def get(self, account_id: UUID) -> Account | None:
        return await self.session.get(Account, account_id)

    async def get_by_platform_username(self, platform: Platform, username: str) -> Account | None:
        query = select(Account).where(
            Account.platform == platform,
            func.lower(Account.username) == username.lower(),
        )
        return await self.session.scalar(query)

    async def create(self, account: Account) -> Account:
        self.session.add(account)
        await self.session.flush()
        return account

    async def delete(self, account: Account) -> None:
        await self.session.delete(account)
