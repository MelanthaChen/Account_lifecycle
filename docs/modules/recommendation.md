# Recommendation Module

## Purpose

Generates read-only rule-based next-best actions for accounts.

## Responsibilities

- Reuse HealthService.
- Generate active recommendation records.
- Preserve dismissed recommendation types during re-evaluation.
- Link recommendations to built-in behavior templates when available.

## Inputs

- Account UUID.
- Health signals.
- Behavior templates.

## Outputs

- `AccountRecommendationRead`

## Related APIs

- `GET /api/v1/recommendations`
- `GET /api/v1/accounts/{account_id}/recommendations`
- `POST /api/v1/recommendations/evaluate-all`
- `POST /api/v1/accounts/{account_id}/recommendations/evaluate`
- `POST /api/v1/recommendations/{recommendation_id}/dismiss`

## Related Database Tables

- `account_recommendations`
- `account_health`
- `behavior_templates`

## Related Services

- `RecommendationService`
- `RecommendationRepository`
- `HealthService`
- `BehaviorTemplateRepository`

## Sequence Diagram

```text
Evaluate Recommendations
  -> RecommendationService
  -> HealthService.evaluate
  -> delete current ACTIVE recommendations
  -> generate candidates
  -> skip dismissed types
  -> insert ACTIVE recommendations
```

## Extension Guide

- Add new recommendation types through enums and migrations.
- Add rules in `_candidates`.
- Do not create campaigns or execute browser automation from recommendations.

