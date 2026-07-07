from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import WorkflowStep
from app.schemas.workflow import WorkflowStepInput


class WorkflowRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_steps(self, campaign_id: UUID) -> list[WorkflowStep]:
        query = (
            select(WorkflowStep)
            .where(WorkflowStep.campaign_id == campaign_id)
            .order_by(WorkflowStep.step_order.asc())
        )
        return list((await self.session.scalars(query)).all())

    async def replace_steps(self, campaign_id: UUID, steps: list[WorkflowStepInput]) -> list[WorkflowStep]:
        await self.session.execute(delete(WorkflowStep).where(WorkflowStep.campaign_id == campaign_id))
        models = [
            WorkflowStep(
                campaign_id=campaign_id,
                step_order=index,
                action_type=step.action_type,
                config=step.config,
            )
            for index, step in enumerate(steps)
        ]
        self.session.add_all(models)
        await self.session.flush()
        return models
