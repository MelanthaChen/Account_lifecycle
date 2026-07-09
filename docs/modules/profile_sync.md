# Profile Sync Module

## Purpose

Synchronizes currently visible Reddit profile data into account records.

## Responsibilities

- Open the Reddit profile page through the persistent browser profile.
- Extract best-effort profile fields.
- Persist available fields without failing when optional fields are missing.
- Record sync activity.

## Inputs

- Account UUID.
- Existing account session/profile.

## Outputs

- Updated `AccountRead`.
- Activity record with type `SYNC_PROFILE`.

## Related APIs

- `POST /api/v1/accounts/{account_id}/sync-profile`

## Related Database Tables

- `accounts`
- `activities`

## Related Services

- `AccountService`
- `RedditSyncService`
- `BrowserManager`
- `ActivityService`

## Sequence Diagram

```text
Frontend
  -> POST /accounts/{id}/sync-profile
  -> AccountService
  -> ActivityService RUNNING
  -> RedditSyncService
  -> BrowserManager.open_persistent_context
  -> scrape profile page
  -> update account profile fields
  -> ActivityService SUCCESS/FAILED
```

## Extension Guide

- Add provider-specific sync services.
- Normalize provider profile fields into account columns only when those fields are shared or intentionally provider-specific.
- Keep scraping logic out of routers.

