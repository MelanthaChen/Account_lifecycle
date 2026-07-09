from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import ScheduleType


class CampaignScheduleBase(BaseModel):
    enabled: bool = True
    schedule_type: ScheduleType
    cron_expression: str | None = Field(default=None, max_length=120)
    timezone: str = Field(default="UTC", max_length=80)
    next_run_at: datetime | None = None

    @model_validator(mode="after")
    def validate_trigger(self) -> "CampaignScheduleBase":
        if self.schedule_type == ScheduleType.ONCE and self.next_run_at is None:
            raise ValueError("next_run_at is required for ONCE schedules")
        if self.schedule_type in {ScheduleType.DAILY, ScheduleType.WEEKLY, ScheduleType.CUSTOM_CRON}:
            if not self.cron_expression:
                raise ValueError("cron_expression is required for recurring schedules")
        return self


class CampaignScheduleCreate(CampaignScheduleBase):
    pass


class CampaignScheduleUpdate(CampaignScheduleBase):
    pass


class CampaignScheduleRead(CampaignScheduleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    campaign_id: UUID
    last_run_at: datetime | None
    last_status: str | None
    created_at: datetime
    updated_at: datetime
