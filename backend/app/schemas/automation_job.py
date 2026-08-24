from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AutomationJobStatus
from app.schemas.account import AccountRead
from app.schemas.campaign import CampaignRead
from app.schemas.workflow import WorkflowStepRead


class AutomationJobCreate(BaseModel):
    campaign_id: UUID
    account_id: UUID
    workflow_id: UUID | None = None


class AutomationJobRead(BaseModel):
    id: UUID
    campaign_id: UUID
    account_id: UUID
    workflow_id: UUID | None = None
    status: AutomationJobStatus
    queued_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    worker_id: str | None = None
    result_json: dict[str, Any] | None = None
    error: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AutomationJobPayload(AutomationJobRead):
    campaign: CampaignRead
    account: AccountRead
    workflow_steps: list[WorkflowStepRead]


class AutomationJobStart(BaseModel):
    worker_id: str | None = Field(default=None, max_length=120)


class AutomationJobFinish(BaseModel):
    worker_id: str | None = Field(default=None, max_length=120)
    result_json: dict[str, Any] = Field(default_factory=dict)


class AutomationJobFail(BaseModel):
    worker_id: str | None = Field(default=None, max_length=120)
    error: str
    result_json: dict[str, Any] | None = None


class WorkerHeartbeatUpdate(BaseModel):
    hostname: str | None = Field(default=None, max_length=255)
    status: str = Field(default="IDLE", max_length=40)
    running_job: UUID | None = None


class WorkerRead(BaseModel):
    worker_id: str
    hostname: str | None = None
    last_seen: datetime
    status: str
    online_status: str
    running_job: UUID | None = None


class WorkerHeartbeatSummary(BaseModel):
    active_workers: int
    workers: list[WorkerRead]
    queued_jobs: int
    running_jobs: int
