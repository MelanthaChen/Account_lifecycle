from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health import AccountHealth


class HealthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self) -> list[AccountHealth]:
        query: Select[tuple[AccountHealth]] = select(AccountHealth).order_by(
            AccountHealth.updated_at.desc()
        )
        return list((await self.session.scalars(query)).all())

    async def get_by_account(self, account_id: UUID) -> AccountHealth | None:
        query = select(AccountHealth).where(AccountHealth.account_id == account_id)
        return await self.session.scalar(query)

    async def save(self, health: AccountHealth) -> AccountHealth:
        self.session.add(health)
        await self.session.flush()
        return health
