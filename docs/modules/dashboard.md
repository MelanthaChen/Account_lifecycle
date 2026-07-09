# Dashboard Module

## Purpose

Provides the central frontend control center.

## Responsibilities

- Summarize health, campaigns, workflow runs, activities, recommendations, and average health.
- Show account health table.
- Show recommended actions.
- Show recent campaigns.
- Show activity timeline.
- Provide quick navigation/actions using existing APIs.

## Inputs

- Accounts API data.
- Health API data.
- Recommendation API data.
- Campaign API data.
- Activity API data.
- Behavior Template API data.

## Outputs

- React dashboard UI.

## Related APIs

- `GET /accounts`
- `GET /health`
- `GET /recommendations`
- `GET /campaigns`
- `GET /activities`
- `GET /behavior-templates`
- `POST /health/evaluate-all`
- `POST /recommendations/evaluate-all`

## Related Database Tables

Dashboard reads through APIs rather than directly from tables.

## Related Services

- Frontend hooks under `frontend/src/hooks`.
- Dashboard components under `frontend/src/components/dashboard`.

## Sequence Diagram

```text
DashboardPage
  -> useAccounts / useHealth / useRecommendations
  -> useCampaigns / useActivities / useBehaviorTemplates
  -> Dashboard components
  -> user clicks quick action
  -> existing route or existing evaluation endpoint
```

## Extension Guide

- Add widgets as small components.
- Prefer existing APIs.
- Include loading, error, and empty states.

