from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ActivityStatus, ActivityType, Platform


class ActivityRead(BaseModel):
    id: UUID
    account_id: UUID
    platform: Platform
    activity_type: ActivityType
    status: ActivityStatus
    target_url: str | None = None
    title: str | None = None
    metadata_: dict[str, Any] | None = Field(default=None, serialization_alias="metadata")
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_ms: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
