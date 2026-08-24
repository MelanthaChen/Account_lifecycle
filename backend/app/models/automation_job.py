from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import AutomationJobStatus, AutomationJobType


class AutomationJob(Base):
    __tablename__ = "automation_jobs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    job_type: Mapped[AutomationJobType] = mapped_column(
        Enum(
            AutomationJobType,
            name="automation_job_type",
            values_callable=lambda enum: [item.value for item in enum],
            validate_strings=True,
        ),
        default=AutomationJobType.WORKFLOW,
        nullable=False,
        index=True,
    )
    campaign_id: Mapped[UUID | None] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), index=True)
    account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    workflow_id: Mapped[UUID | None] = mapped_column(ForeignKey("workflow_steps.id", ondelete="SET NULL"))
    status: Mapped[AutomationJobStatus] = mapped_column(
        Enum(
            AutomationJobStatus,
            name="automation_job_status",
            values_callable=lambda enum: [item.value for item in enum],
            validate_strings=True,
        ),
        default=AutomationJobStatus.QUEUED,
        nullable=False,
        index=True,
    )
    queued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    worker_id: Mapped[str | None] = mapped_column(String(120), index=True)
    result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    error: Mapped[str | None] = mapped_column(Text)


class AutomationWorker(Base):
    __tablename__ = "automation_workers"

    worker_id: Mapped[str] = mapped_column(String(120), primary_key=True)
    hostname: Mapped[str | None] = mapped_column(String(255))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    running_job: Mapped[UUID | None] = mapped_column(ForeignKey("automation_jobs.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
