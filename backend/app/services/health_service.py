from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.activity import Activity
from app.models.campaign import Campaign, CampaignAccount
from app.models.enums import ActivityStatus, CampaignStatus, HealthStatus, RiskLevel
from app.models.health import AccountHealth
from app.repositories.account_repository import AccountRepository
from app.repositories.health_repository import HealthRepository


class HealthService:
    """Calculates rule-based account health from existing account and activity data."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.accounts = AccountRepository(session)
        self.health = HealthRepository(session)

    async def list_health(self) -> list[AccountHealth]:
        """Return all stored account health records."""
        return await self.health.list()

    async def get_health(self, account_id: UUID) -> AccountHealth:
        """Return account health, evaluating the account if no record exists yet."""
        record = await self.health.get_by_account(account_id)
        if record is None:
            account = await self._get_account(account_id)
            return await self.evaluate(account)
        return record

    async def evaluate_account(self, account_id: UUID) -> AccountHealth:
        """Evaluate and persist health for one account."""
        account = await self._get_account(account_id)
        return await self.evaluate(account)

    async def evaluate_all(self) -> list[AccountHealth]:
        """Evaluate and persist health for every account."""
        records: list[AccountHealth] = []
        for account in await self.accounts.list():
            records.append(await self.evaluate(account))
        return records

    async def evaluate(self, account: Account) -> AccountHealth:
        """Compute health signals, score, status, and risk for an account."""
        signals = await self._signals(account)
        score = self._score(signals)
        now = datetime.now(UTC)
        record = await self.health.get_by_account(account.id)
        if record is None:
            record = AccountHealth(
                account_id=account.id,
                health_score=score,
                health_status=self._status(score),
                risk_level=self._risk(score),
                signals=signals,
                last_evaluated_at=now,
            )
        else:
            record.health_score = score
            record.health_status = self._status(score)
            record.risk_level = self._risk(score)
            record.signals = signals
            record.last_evaluated_at = now
        await self.health.save(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def _get_account(self, account_id: UUID) -> Account:
        account = await self.accounts.get(account_id)
        if account is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found")
        return account

    async def _signals(self, account: Account) -> dict:
        last_activity_at = await self._last_activity_at(account.id)
        workflow_success_rate = await self._workflow_success_rate(account.id)
        now = datetime.now(UTC)
        last_activity_hours = (
            (now - last_activity_at).total_seconds() / 3600 if last_activity_at else None
        )
        account_age_days = (now - account.created_at).days if account.created_at else None
        return {
            "session_valid": account.session_status == "valid",
            "profile_synced": account.last_profile_sync is not None,
            "email_verified": account.verified_email is True,
            "reddit_username": bool(account.reddit_username),
            "account_age_days": account_age_days,
            "post_karma": account.karma_post,
            "comment_karma": account.karma_comment,
            "last_activity_hours": last_activity_hours,
            "workflow_success_rate": workflow_success_rate,
        }

    async def _last_activity_at(self, account_id: UUID) -> datetime | None:
        query = select(func.max(Activity.created_at)).where(
            Activity.account_id == account_id,
            Activity.status == ActivityStatus.SUCCESS,
        )
        return await self.session.scalar(query)

    async def _workflow_success_rate(self, account_id: UUID) -> float | None:
        query = (
            select(Campaign.status)
            .join(CampaignAccount, CampaignAccount.campaign_id == Campaign.id)
            .where(
                CampaignAccount.account_id == account_id,
                Campaign.status.in_([CampaignStatus.COMPLETED, CampaignStatus.FAILED]),
            )
        )
        statuses = list((await self.session.scalars(query)).all())
        if not statuses:
            return None
        completed = sum(1 for item in statuses if item == CampaignStatus.COMPLETED)
        return completed / len(statuses)

    @staticmethod
    def _score(signals: dict) -> int:
        score = 100
        if not signals["session_valid"]:
            score -= 40
        if not signals["profile_synced"]:
            score -= 20
        if not signals["email_verified"]:
            score -= 10
        if not signals["reddit_username"]:
            score -= 20
        if (signals["post_karma"] or 0) == 0:
            score -= 5
        if (signals["comment_karma"] or 0) == 0:
            score -= 5
        last_activity_hours = signals["last_activity_hours"]
        if last_activity_hours is None or last_activity_hours > 30 * 24:
            score -= 10
        workflow_success_rate = signals["workflow_success_rate"]
        if workflow_success_rate is not None and workflow_success_rate < 0.8:
            score -= 10
        return max(0, min(100, score))

    @staticmethod
    def _status(score: int) -> HealthStatus:
        if score >= 80:
            return HealthStatus.HEALTHY
        if score >= 50:
            return HealthStatus.WARNING
        return HealthStatus.CRITICAL

    @staticmethod
    def _risk(score: int) -> RiskLevel:
        if score >= 90:
            return RiskLevel.LOW
        if score >= 60:
            return RiskLevel.MEDIUM
        return RiskLevel.HIGH
