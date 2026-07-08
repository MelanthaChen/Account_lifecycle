from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Platform


class BehaviorTemplateBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    platform: Platform = Platform.REDDIT
    category: str = Field(min_length=1, max_length=80)
    workflow_json: list[dict[str, Any]] = Field(min_length=1)


class BehaviorTemplateCreate(BehaviorTemplateBase):
    pass


class BehaviorTemplateRead(BehaviorTemplateBase):
    id: UUID
    is_builtin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplyBehaviorTemplateRequest(BaseModel):
    template_id: UUID
