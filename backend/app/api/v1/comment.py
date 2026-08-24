from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, HttpUrl, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.enums import AutomationJobStatus
from app.services.comment_service import CommentService

router = APIRouter(prefix="/comment", tags=["comment"])


class CommentPayload(BaseModel):
    url: HttpUrl
    text: str = Field(min_length=1, max_length=10_000)


class CommentRequest(BaseModel):
    type: str = "COMMENT"
    payload: CommentPayload
    account_ids: list[UUID] = Field(min_length=1)

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        if value != "COMMENT":
            raise ValueError("type must be COMMENT")
        return value

    @field_validator("payload")
    @classmethod
    def validate_reddit_url(cls, value: CommentPayload) -> CommentPayload:
        host = (value.url.host or "").lower()
        if host not in {"reddit.com", "www.reddit.com", "old.reddit.com"}:
            raise ValueError("url must be a Reddit URL")
        if not value.text.strip():
            raise ValueError("text is required")
        value.text = value.text.strip()
        return value


class CommentJob(BaseModel):
    id: UUID
    account_id: UUID
    account: str
    status: AutomationJobStatus


class CommentResponse(BaseModel):
    success: bool
    type: str
    payload: CommentPayload
    jobs: list[CommentJob]


def service(session: AsyncSession = Depends(get_session)) -> CommentService:
    return CommentService(session)


@router.post("", response_model=CommentResponse)
async def create_comment_request(
    payload: CommentRequest,
    comment_service: CommentService = Depends(service),
) -> CommentResponse:
    jobs = await comment_service.enqueue(
        account_ids=payload.account_ids,
        target_url=str(payload.payload.url),
        comment_text=payload.payload.text,
    )
    return CommentResponse(
        success=True,
        type=payload.type,
        payload=payload.payload,
        jobs=[
            CommentJob(
                id=job.id,
                account_id=job.account_id,
                account=str(job.result_json.get("account") or job.account_id) if job.result_json else str(job.account_id),
                status=job.status,
            )
            for job in jobs
        ],
    )
