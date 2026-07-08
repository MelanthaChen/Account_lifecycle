from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.behavior_template import BehaviorTemplate


class BehaviorTemplateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self) -> list[BehaviorTemplate]:
        query: Select[tuple[BehaviorTemplate]] = select(BehaviorTemplate).order_by(
            BehaviorTemplate.is_builtin.desc(),
            BehaviorTemplate.name.asc(),
        )
        return list((await self.session.scalars(query)).all())

    async def get(self, template_id: UUID) -> BehaviorTemplate | None:
        return await self.session.get(BehaviorTemplate, template_id)

    async def create(self, template: BehaviorTemplate) -> BehaviorTemplate:
        self.session.add(template)
        await self.session.flush()
        return template

    async def delete(self, template: BehaviorTemplate) -> None:
        await self.session.delete(template)
