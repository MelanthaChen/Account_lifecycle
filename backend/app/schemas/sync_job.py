from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import SyncJobStatus


class SyncJobRead(BaseModel):
    id: UUID
    account_id: UUID
    status: SyncJobStatus
    started_at: datetime | None
    finished_at: datetime | None
    error: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
