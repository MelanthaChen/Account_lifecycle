from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import RecommendationPriority, RecommendationStatus, RecommendationType


class AccountRecommendationRead(BaseModel):
    id: UUID
    account_id: UUID
    recommendation_type: RecommendationType
    priority: RecommendationPriority
    title: str
    description: str
    recommended_template_id: UUID | None
    status: RecommendationStatus
    reason: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
