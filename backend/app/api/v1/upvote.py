from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, HttpUrl, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.enums import AutomationJobStatus
from app.services.upvote_service import UpvoteService

router = APIRouter(prefix="/upvote", tags=["upvote"])


class UpvoteRequest(BaseModel):
    account_ids: list[UUID] = Field(min_length=1)
    target_url: HttpUrl

    @field_validator("target_url")
    @classmethod
    def validate_reddit_url(cls, value: HttpUrl) -> HttpUrl:
        host = (value.host or "").lower()
        if host not in {"reddit.com", "www.reddit.com", "old.reddit.com"}:
            raise ValueError("target_url must be a Reddit URL")
        return value


class UpvoteJob(BaseModel):
    id: UUID
    account_id: UUID
    account: str
    status: AutomationJobStatus


class UpvoteResponse(BaseModel):
    success: bool
    target_url: str
    jobs: list[UpvoteJob]


def service(session: AsyncSession = Depends(get_session)) -> UpvoteService:
    return UpvoteService(session)


@router.post("", response_model=UpvoteResponse)
async def create_upvote_request(
    payload: UpvoteRequest,
    upvote_service: UpvoteService = Depends(service),
) -> UpvoteResponse:
    jobs = await upvote_service.enqueue(
        account_ids=payload.account_ids,
        target_url=str(payload.target_url),
    )
    return UpvoteResponse(
        success=True,
        target_url=str(payload.target_url),
        jobs=[
            UpvoteJob(
                id=job.id,
                account_id=job.account_id,
                account=str(job.result_json.get("account") or job.account_id) if job.result_json else str(job.account_id),
                status=job.status,
            )
            for job in jobs
        ],
    )
