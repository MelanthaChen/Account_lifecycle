from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import RecommendationStatus, RecommendationType
from app.models.recommendation import AccountRecommendation


class RecommendationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self) -> list[AccountRecommendation]:
        query: Select[tuple[AccountRecommendation]] = select(AccountRecommendation).order_by(
            AccountRecommendation.created_at.desc()
        )
        return list((await self.session.scalars(query)).all())

    async def list_for_account(self, account_id: UUID) -> list[AccountRecommendation]:
        query: Select[tuple[AccountRecommendation]] = (
            select(AccountRecommendation)
            .where(AccountRecommendation.account_id == account_id)
            .order_by(AccountRecommendation.created_at.desc())
        )
        return list((await self.session.scalars(query)).all())

    async def get(self, recommendation_id: UUID) -> AccountRecommendation | None:
        return await self.session.get(AccountRecommendation, recommendation_id)

    async def dismissed_types_for_account(self, account_id: UUID) -> set[RecommendationType]:
        query = select(AccountRecommendation.recommendation_type).where(
            AccountRecommendation.account_id == account_id,
            AccountRecommendation.status == RecommendationStatus.DISMISSED,
        )
        return set((await self.session.scalars(query)).all())

    async def delete_active_for_account(self, account_id: UUID) -> None:
        await self.session.execute(
            delete(AccountRecommendation).where(
                AccountRecommendation.account_id == account_id,
                AccountRecommendation.status == RecommendationStatus.ACTIVE,
            )
        )

    async def create(self, recommendation: AccountRecommendation) -> AccountRecommendation:
        self.session.add(recommendation)
        await self.session.flush()
        return recommendation
