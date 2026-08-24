from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.enums import AutomationJobStatus
from app.core.config import get_settings
from app.schemas.automation_job import (
    AutomationJobCreate,
    AutomationJobFail,
    AutomationJobFinish,
    AutomationJobPayload,
    AutomationJobRead,
    AutomationJobStart,
    WorkerHeartbeatSummary,
    WorkerHeartbeatUpdate,
)
from app.services.automation_job_service import AutomationJobService

router = APIRouter(tags=["automation-jobs"])


def service(session: AsyncSession = Depends(get_session)) -> AutomationJobService:
    return AutomationJobService(session)


def authenticate_agent(
    x_agent_secret: str | None = Header(default=None),
    x_agent_name: str | None = Header(default=None),
    x_worker_id: str | None = Header(default=None),
    x_worker_secret: str | None = Header(default=None),
) -> str:
    settings = get_settings()
    supplied_secret = x_agent_secret or x_worker_secret
    if not supplied_secret:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Automation Agent credentials are required")
    expected_secret = settings.automation_agent_secret
    if not expected_secret and settings.automation_workers:
        expected_secret = next(iter(settings.automation_workers.values()))
    if not expected_secret or supplied_secret != expected_secret:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid Automation Agent secret")
    # TODO: this is intentionally a single-agent identity. A distributed runtime can add routing later.
    return x_agent_name or settings.automation_agent_name or x_worker_id or "automation-agent"


@router.get("/jobs", response_model=list[AutomationJobRead])
async def list_jobs(
    limit: int = Query(default=50, ge=1, le=200),
    status: AutomationJobStatus | None = None,
    jobs: AutomationJobService = Depends(service),
) -> list[AutomationJobRead]:
    return await jobs.list_jobs(limit=limit, status_filter=status)


@router.post("/jobs", response_model=AutomationJobRead)
async def create_job(
    payload: AutomationJobCreate,
    jobs: AutomationJobService = Depends(service),
) -> AutomationJobRead:
    return await jobs.create_job(payload)


@router.get("/jobs/next", response_model=AutomationJobPayload | None)
async def get_next_job(
    response: Response,
    jobs: AutomationJobService = Depends(service),
    agent_name: str = Depends(authenticate_agent),
) -> AutomationJobPayload | None:
    job = await jobs.next_job(agent_name=agent_name)
    if job is None:
        response.status_code = status.HTTP_204_NO_CONTENT
    return job


@router.get("/jobs/{job_id}", response_model=AutomationJobRead)
async def get_job(
    job_id: UUID,
    jobs: AutomationJobService = Depends(service),
) -> AutomationJobRead:
    return await jobs.get_job(job_id)


@router.post("/jobs/{job_id}/start", response_model=AutomationJobRead)
async def start_job(
    job_id: UUID,
    payload: AutomationJobStart,
    jobs: AutomationJobService = Depends(service),
    agent_name: str = Depends(authenticate_agent),
) -> AutomationJobRead:
    return await jobs.start_job(job_id, payload, agent_name=agent_name)


@router.post("/jobs/{job_id}/finish", response_model=AutomationJobRead)
async def finish_job(
    job_id: UUID,
    payload: AutomationJobFinish,
    jobs: AutomationJobService = Depends(service),
    agent_name: str = Depends(authenticate_agent),
) -> AutomationJobRead:
    return await jobs.finish_job(job_id, payload, agent_name=agent_name)


@router.post("/jobs/{job_id}/fail", response_model=AutomationJobRead)
async def fail_job(
    job_id: UUID,
    payload: AutomationJobFail,
    jobs: AutomationJobService = Depends(service),
    agent_name: str = Depends(authenticate_agent),
) -> AutomationJobRead:
    return await jobs.fail_job(job_id, payload, agent_name=agent_name)


@router.post("/agent/heartbeat", response_model=WorkerHeartbeatSummary)
async def post_agent_heartbeat(
    payload: WorkerHeartbeatUpdate,
    jobs: AutomationJobService = Depends(service),
    agent_name: str = Depends(authenticate_agent),
) -> WorkerHeartbeatSummary:
    return await jobs.record_heartbeat(agent_name, payload)


@router.get("/agent/heartbeat", response_model=WorkerHeartbeatSummary)
async def agent_heartbeat(
    jobs: AutomationJobService = Depends(service),
) -> WorkerHeartbeatSummary:
    return await jobs.heartbeat()
