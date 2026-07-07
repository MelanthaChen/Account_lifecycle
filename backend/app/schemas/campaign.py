from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.models.enums import CampaignActionType, CampaignStatus, Platform


class CampaignBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    platform: Platform = Platform.REDDIT
    action_type: CampaignActionType = CampaignActionType.UPVOTE
    target_url: HttpUrl

    @field_validator("target_url")
    @classmethod
    def validate_reddit_url(cls, value: HttpUrl) -> HttpUrl:
        host = (value.host or "").lower()
        if host not in {"reddit.com", "www.reddit.com", "old.reddit.com"}:
            raise ValueError("target_url must be a Reddit URL")
        return value


class CampaignCreate(CampaignBase):
    account_ids: list[UUID] = Field(min_length=1)


class CampaignRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    platform: Platform
    action_type: CampaignActionType
    target_url: str
    status: CampaignStatus
    account_ids: list[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CampaignRunResult(BaseModel):
    account: str
    opened: bool
    clicked: bool
    verified: bool
    reason: str | None = None


class CampaignRunResponse(BaseModel):
    campaign: CampaignRead
    success: bool
    results: list[CampaignRunResult]
