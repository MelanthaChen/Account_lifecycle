# Health Module

## Purpose

Calculates rule-based account health on demand.

## Responsibilities

- Build health signals from existing account, activity, and campaign data.
- Score accounts from 0 to 100.
- Assign health status and risk level.
- Persist the latest health record per account.

## Inputs

- Account UUID.
- Existing account/session/profile/activity/campaign data.

## Outputs

- `AccountHealthRead`

## Related APIs

- `GET /api/v1/health`
- `GET /api/v1/accounts/{account_id}/health`
- `POST /api/v1/accounts/{account_id}/health/evaluate`
- `POST /api/v1/health/evaluate-all`

## Related Database Tables

- `account_health`
- `accounts`
- `activities`
- `campaigns`
- `campaign_accounts`

## Related Services

- `HealthService`
- `HealthRepository`
- `AccountRepository`

## Sequence Diagram

```text
Evaluate Health
  -> HealthService
  -> load account
  -> collect signals
  -> apply scoring rules
  -> upsert account_health
```

## Extension Guide

- Add new signals in `_signals`.
- Update `_score` with explicit rule deductions.
- Keep health evaluation read-only with respect to browser automation.

