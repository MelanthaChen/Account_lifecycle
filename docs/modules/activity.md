# Activity Module

## Purpose

Provides an audit log for account operations.

## Responsibilities

- Record operation start, success, and failure.
- Store target URL, title, metadata, timing, status, and duration.
- Provide filtered activity lists.
- Support synthetic test activity records for UI checks.

## Inputs

- Account.
- Activity type.
- Status.
- Optional metadata.

## Outputs

- `ActivityRead`
- Lists of activity records.

## Related APIs

- `GET /api/v1/activities`
- `GET /api/v1/accounts/{account_id}/activities`
- `GET /api/v1/activities/{activity_id}`
- `DELETE /api/v1/activities/{activity_id}`
- `POST /api/v1/activities/test`
- `POST /api/v1/accounts/{account_id}/activities/test`

## Related Database Tables

- `activities`
- `accounts`

## Related Services

- `ActivityService`
- `ActivityRepository`

## Sequence Diagram

```text
Service operation
  -> ActivityService.record_start
  -> operation executes
  -> ActivityService.record_success
     or ActivityService.record_failure
  -> activities table
```

## Extension Guide

- Add new `ActivityType` values when new operation families are added.
- Store operation-specific details in `metadata`.
- Keep activity writes close to service operations.

