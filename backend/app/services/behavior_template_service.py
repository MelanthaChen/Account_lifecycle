from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.behavior_template import BehaviorTemplate
from app.models.enums import WorkflowActionType
from app.repositories.behavior_template_repository import BehaviorTemplateRepository
from app.schemas.behavior_template import BehaviorTemplateCreate
from app.schemas.workflow import WorkflowRead, WorkflowStepInput, WorkflowWrite
from app.services.workflow_service import WorkflowService


class BehaviorTemplateService:
    """Manages reusable workflow step templates and applies them to campaigns."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.templates = BehaviorTemplateRepository(session)
        self.workflows = WorkflowService(session)

    async def list_templates(self) -> list[BehaviorTemplate]:
        """Return behavior templates with built-ins first."""
        return await self.templates.list()

    async def get_template(self, template_id: UUID) -> BehaviorTemplate:
        """Return one behavior template or raise 404 when missing."""
        template = await self.templates.get(template_id)
        if template is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Behavior template not found")
        return template

    async def create_template(self, payload: BehaviorTemplateCreate) -> BehaviorTemplate:
        """Validate and create a custom behavior template."""
        steps = self._template_to_steps(payload.workflow_json)
        template = BehaviorTemplate(
            name=payload.name,
            description=payload.description,
            platform=payload.platform,
            category=payload.category,
            workflow_json=[self._step_to_template_item(step) for step in steps],
            is_builtin=False,
        )
        await self.templates.create(template)
        await self.session.commit()
        await self.session.refresh(template)
        return template

    async def delete_template(self, template_id: UUID) -> None:
        """Delete a custom template; built-in templates are read-only."""
        template = await self.get_template(template_id)
        if template.is_builtin:
            raise HTTPException(status.HTTP_409_CONFLICT, "Built-in templates are read-only")
        await self.templates.delete(template)
        await self.session.commit()

    async def apply_template(self, campaign_id: UUID, template_id: UUID) -> WorkflowRead:
        """Replace a campaign workflow with steps generated from a template."""
        template = await self.get_template(template_id)
        steps = self._template_to_steps(template.workflow_json)
        return await self.workflows.replace_workflow(campaign_id, WorkflowWrite(steps=steps))

    def _template_to_steps(self, workflow_json: list[dict[str, Any]]) -> list[WorkflowStepInput]:
        steps: list[WorkflowStepInput] = []
        for item in workflow_json:
            action = item.get("action") or item.get("action_type")
            if not isinstance(action, str):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Template step is missing action")
            try:
                action_type = WorkflowActionType(action)
            except ValueError as exc:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unsupported workflow action: {action}") from exc
            config = item.get("config") or {}
            if not isinstance(config, dict):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Template step config must be an object")
            steps.append(WorkflowStepInput(action_type=action_type, config=config))
        return steps

    @staticmethod
    def _step_to_template_item(step: WorkflowStepInput) -> dict[str, Any]:
        item: dict[str, Any] = {"action": step.action_type.value}
        if step.config:
            item["config"] = step.config
        return item
