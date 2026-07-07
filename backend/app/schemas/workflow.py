from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import WorkflowActionType


class WorkflowStepInput(BaseModel):
    action_type: WorkflowActionType
    config: dict[str, Any] = Field(default_factory=dict)


class WorkflowStepRead(BaseModel):
    id: UUID
    campaign_id: UUID
    step_order: int
    action_type: WorkflowActionType
    config: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkflowRead(BaseModel):
    campaign_id: UUID
    steps: list[WorkflowStepRead]


class WorkflowWrite(BaseModel):
    steps: list[WorkflowStepInput] = Field(min_length=1)


class WorkflowStepResult(BaseModel):
    action_type: WorkflowActionType
    success: bool
    reason: str | None = None


class WorkflowAccountResult(BaseModel):
    account: str
    steps: list[WorkflowStepResult]


class WorkflowRunResponse(BaseModel):
    campaign_id: UUID
    success: bool
    results: list[WorkflowAccountResult]
