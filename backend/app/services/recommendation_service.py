from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.behavior_template import BehaviorTemplate
from app.models.enums import (
    HealthStatus,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
)
from app.models.recommendation import AccountRecommendation
from app.repositories.behavior_template_repository import BehaviorTemplateRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.services.account_service import AccountService
from app.services.health_service import HealthService


@dataclass(frozen=True)
class RecommendationCandidate:
    recommendation_type: RecommendationType
    priority: RecommendationPriority
    title: str
    description: str
    template_name: str | None
    reason: dict


class RecommendationService:
    """Generates read-only rule-based recommendations from health and template data."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.accounts = AccountService(session)
        self.health = HealthService(session)
        self.recommendations = RecommendationRepository(session)
        self.templates = BehaviorTemplateRepository(session)

    async def list_recommendations(self) -> list[AccountRecommendation]:
        """Return all recommendation records."""
        return await self.recommendations.list()

    async def list_for_account(self, account_id: UUID) -> list[AccountRecommendation]:
        """Return recommendation records for one account."""
        await self.accounts.get_account(account_id)
        return await self.recommendations.list_for_account(account_id)

    async def evaluate_account(self, account_id: UUID) -> list[AccountRecommendation]:
        """Evaluate recommendations for one account."""
        account = await self.accounts.get_account(account_id)
        return await self.evaluate(account)

    async def evaluate_all(self) -> list[AccountRecommendation]:
        """Evaluate recommendations for every account."""
        results: list[AccountRecommendation] = []
        for account in await self.accounts.list_accounts():
            results.extend(await self.evaluate(account))
        return results

    async def evaluate(self, account: Account) -> list[AccountRecommendation]:
        """Refresh active recommendations for an account while preserving dismissed rows."""
        health = await self.health.evaluate(account)
        dismissed_types = await self.recommendations.dismissed_types_for_account(account.id)
        await self.recommendations.delete_active_for_account(account.id)

        templates_by_name = await self._templates_by_name()
        candidates = self._candidates(health.health_status, health.health_score, health.signals)
        created: list[AccountRecommendation] = []
        for candidate in candidates:
            if candidate.recommendation_type in dismissed_types:
                continue
            recommendation = AccountRecommendation(
                account_id=account.id,
                recommendation_type=candidate.recommendation_type,
                priority=candidate.priority,
                title=candidate.title,
                description=candidate.description,
                recommended_template_id=self._template_id(candidate.template_name, templates_by_name),
                status=RecommendationStatus.ACTIVE,
                reason=candidate.reason,
            )
            created.append(await self.recommendations.create(recommendation))

        await self.session.commit()
        for recommendation in created:
            await self.session.refresh(recommendation)
        return await self.recommendations.list_for_account(account.id)

    async def dismiss(self, recommendation_id: UUID) -> AccountRecommendation:
        """Mark a recommendation as dismissed."""
        recommendation = await self.recommendations.get(recommendation_id)
        if recommendation is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Recommendation not found")
        recommendation.status = RecommendationStatus.DISMISSED
        await self.session.commit()
        await self.session.refresh(recommendation)
        return recommendation

    async def _templates_by_name(self) -> dict[str, BehaviorTemplate]:
        templates = await self.templates.list()
        return {template.name.lower(): template for template in templates}

    @staticmethod
    def _template_id(template_name: str | None, templates_by_name: dict[str, BehaviorTemplate]) -> UUID | None:
        if template_name is None:
            return None
        template = templates_by_name.get(template_name.lower())
        return template.id if template else None

    def _candidates(
        self,
        health_status: HealthStatus,
        health_score: int,
        signals: dict,
    ) -> list[RecommendationCandidate]:
        candidates: list[RecommendationCandidate] = []
        base_reason = {
            "health_status": health_status.value,
            "health_score": health_score,
            "signals": signals,
        }

        if health_status == HealthStatus.CRITICAL:
            candidates.append(
                RecommendationCandidate(
                    recommendation_type=RecommendationType.REFRESH_SESSION,
                    priority=RecommendationPriority.HIGH,
                    title="Refresh session",
                    description="This account is critical. Refresh the session before running more workflows.",
                    template_name=None,
                    reason=base_reason | {"rule": "health_critical"},
                )
            )
        elif health_status == HealthStatus.WARNING:
            candidates.append(
                RecommendationCandidate(
                    recommendation_type=RecommendationType.RUN_WARM_UP,
                    priority=RecommendationPriority.HIGH,
                    title="Run warm up",
                    description="This account is in warning state. Run a warm-up behavior before stronger actions.",
                    template_name="Warm Up",
                    reason=base_reason | {"rule": "health_warning"},
                )
            )
        elif health_status == HealthStatus.HEALTHY:
            candidates.append(
                RecommendationCandidate(
                    recommendation_type=RecommendationType.RUN_QUICK_UPVOTE,
                    priority=RecommendationPriority.MEDIUM,
                    title="Run quick upvote",
                    description="This account is healthy and can run a light upvote workflow.",
                    template_name="Quick Upvote",
                    reason=base_reason | {"rule": "health_healthy"},
                )
            )

        if not signals.get("profile_synced"):
            candidates.append(
                RecommendationCandidate(
                    recommendation_type=RecommendationType.SYNC_PROFILE,
                    priority=RecommendationPriority.HIGH,
                    title="Sync profile",
                    description="The account profile has not been synced yet.",
                    template_name=None,
                    reason=base_reason | {"rule": "profile_not_synced"},
                )
            )

        if (signals.get("post_karma") or 0) == 0:
            candidates.append(
                RecommendationCandidate(
                    recommendation_type=RecommendationType.RUN_CASUAL_READER,
                    priority=RecommendationPriority.MEDIUM,
                    title="Run casual reader",
                    description="Post karma is zero. A casual reader workflow can add lower-risk account activity.",
                    template_name="Casual Reader",
                    reason=base_reason | {"rule": "post_karma_zero"},
                )
            )

        if (signals.get("comment_karma") or 0) == 0:
            candidates.append(
                RecommendationCandidate(
                    recommendation_type=RecommendationType.RUN_DEEP_READER,
                    priority=RecommendationPriority.MEDIUM,
                    title="Run deep reader",
                    description="Comment karma is zero. A deeper reading workflow can prepare the account for future use.",
                    template_name="Deep Reader",
                    reason=base_reason | {"rule": "comment_karma_zero"},
                )
            )

        if not candidates:
            candidates.append(
                RecommendationCandidate(
                    recommendation_type=RecommendationType.NO_ACTION,
                    priority=RecommendationPriority.LOW,
                    title="No action needed",
                    description="No recommendation rules matched for this account.",
                    template_name=None,
                    reason=base_reason | {"rule": "no_rule_matched"},
                )
            )
        return self._deduplicate(candidates)

    @staticmethod
    def _deduplicate(candidates: list[RecommendationCandidate]) -> list[RecommendationCandidate]:
        seen: set[RecommendationType] = set()
        unique: list[RecommendationCandidate] = []
        for candidate in candidates:
            if candidate.recommendation_type in seen:
                continue
            seen.add(candidate.recommendation_type)
            unique.append(candidate)
        return unique
