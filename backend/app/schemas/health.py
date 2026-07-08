from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import HealthStatus, RiskLevel


class AccountHealthRead(BaseModel):
    id: UUID
    account_id: UUID
    health_score: int
    health_status: HealthStatus
    risk_level: RiskLevel
    signals: dict[str, Any]
    last_evaluated_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
