from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.enums import ActivityStatus, ActivityType


class ActivityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(
        self,
        *,
        account_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
        activity_type: ActivityType | None = None,
        status: ActivityStatus | None = None,
    ) -> list[Activity]:
        query: Select[tuple[Activity]] = select(Activity).order_by(Activity.created_at.desc())
        if account_id is not None:
            query = query.where(Activity.account_id == account_id)
        if activity_type is not None:
            query = query.where(Activity.activity_type == activity_type)
        if status is not None:
            query = query.where(Activity.status == status)
        query = query.limit(limit).offset(offset)
        return list((await self.session.scalars(query)).all())

    async def get(self, activity_id: UUID) -> Activity | None:
        return await self.session.get(Activity, activity_id)

    async def create(self, activity: Activity) -> Activity:
        self.session.add(activity)
        await self.session.flush()
        return activity

    async def delete(self, activity: Activity) -> None:
        await self.session.delete(activity)
