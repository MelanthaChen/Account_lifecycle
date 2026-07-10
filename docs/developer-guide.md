# Developer Guide

## How To Add A Provider

1. Add provider enum values in `backend/app/models/enums.py`.
2. Create a provider package under `backend/app/providers/<provider_name>/`.
3. Implement the `Provider` protocol from `backend/app/providers/base.py`.
4. Register the provider in `ProviderManager`.
5. Keep routers unchanged where possible; services should resolve providers by `account.platform`.
6. Put platform-specific selectors, cookies, scraping, actions, and browser behavior inside the provider.
7. Extend frontend platform options and labels.

## How To Add A Workflow Action

1. Add the value to `WorkflowActionType`.
2. Add an Alembic migration for the PostgreSQL enum.
3. Add UI controls in `CampaignDetailPage`.
4. Add execution delegation in `WorkflowService._execute_step`.
5. Put browser-specific behavior in a service such as `BehaviorService`, not in routers.
6. Add frontend type support in `frontend/src/types/campaign.ts`.

## How To Add A Behavior Template

1. Use `POST /behavior-templates` for custom templates.
2. For built-ins, add rows through an Alembic migration.
3. Use JSON items shaped as:

```json
{"action": "WAIT", "config": {"min_seconds": 5, "max_seconds": 12}}
```

4. Keep built-ins read-only.

## How To Add A Campaign Type

1. Extend `CampaignActionType`.
2. Add a migration for the enum.
3. Update `CampaignService.create_campaign` validation.
4. Define the default workflow for the action type.
5. Add frontend form support.
6. Ensure `WorkflowService` delegates execution to an existing or new service.

## How To Add Dashboard Widgets

1. Add or reuse a React Query hook.
2. Build a small component under `frontend/src/components/dashboard/`.
3. Compose it in `DashboardPage`.
4. Avoid new backend endpoints unless existing APIs cannot answer the question.
5. Include loading, error, and empty states.

## How To Add Recommendation Rules

1. Update `RecommendationType` if a new type is needed.
2. Add a migration for the enum when needed.
3. Add a candidate in `RecommendationService._candidates`.
4. Reuse `HealthService` signals or existing repositories.
5. Do not execute campaigns or browser actions from the Recommendation Engine.

## Coding Rules

- Routers stay thin.
- Services own business rules.
- Repositories own database access.
- Provider-specific browser behavior stays behind provider classes.
- Frontend API calls live in `frontend/src/api`.
- TanStack Query hooks live in `frontend/src/hooks`.
