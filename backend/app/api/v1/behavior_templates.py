from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.behavior_template import (
    ApplyBehaviorTemplateRequest,
    BehaviorTemplateCreate,
    BehaviorTemplateRead,
)
from app.schemas.workflow import WorkflowRead
from app.services.behavior_template_service import BehaviorTemplateService

router = APIRouter(tags=["behavior-templates"])


def service(session: AsyncSession = Depends(get_session)) -> BehaviorTemplateService:
    return BehaviorTemplateService(session)


@router.get("/behavior-templates", response_model=list[BehaviorTemplateRead])
async def list_behavior_templates(
    template_service: BehaviorTemplateService = Depends(service),
) -> list[BehaviorTemplateRead]:
    return await template_service.list_templates()


@router.get("/behavior-templates/{template_id}", response_model=BehaviorTemplateRead)
async def get_behavior_template(
    template_id: UUID,
    template_service: BehaviorTemplateService = Depends(service),
) -> BehaviorTemplateRead:
    return await template_service.get_template(template_id)


@router.post("/behavior-templates", response_model=BehaviorTemplateRead, status_code=status.HTTP_201_CREATED)
async def create_behavior_template(
    payload: BehaviorTemplateCreate,
    template_service: BehaviorTemplateService = Depends(service),
) -> BehaviorTemplateRead:
    return await template_service.create_template(payload)


@router.delete("/behavior-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_behavior_template(
    template_id: UUID,
    template_service: BehaviorTemplateService = Depends(service),
) -> Response:
    await template_service.delete_template(template_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/campaigns/{campaign_id}/apply-template", response_model=WorkflowRead)
async def apply_behavior_template(
    campaign_id: UUID,
    payload: ApplyBehaviorTemplateRequest,
    template_service: BehaviorTemplateService = Depends(service),
) -> WorkflowRead:
    return await template_service.apply_template(campaign_id, payload.template_id)
