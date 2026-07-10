# Scheduler Module

## Purpose

Runs campaigns automatically according to stored schedules.

## Responsibilities

- Store one schedule per campaign.
- Start APScheduler during FastAPI startup.
- Reload enabled schedules on startup.
- Register and remove APScheduler jobs.
- Run campaigns through `CampaignService.run()`.
- Record last run time and last status.

## Inputs

- Campaign UUIDs.
- Schedule type: `ONCE`, `DAILY`, `WEEKLY`, `CUSTOM_CRON`.
- Cron expression or one-time `next_run_at`.
- Timezone.

## Outputs

- `CampaignScheduleRead`.
- `WorkflowRunResponse` for Run Now.
- Updated `campaign_schedules.last_run_at` and `last_status`.
- Activity records for scheduled runs.

## Related APIs

- `GET /api/v1/schedules`
- `GET /api/v1/campaigns/{campaign_id}/schedule`
- `POST /api/v1/campaigns/{campaign_id}/schedule`
- `PUT /api/v1/campaigns/{campaign_id}/schedule`
- `DELETE /api/v1/campaigns/{campaign_id}/schedule`
- `POST /api/v1/campaigns/{campaign_id}/schedule/run-now`

## Related Database Tables

- `campaign_schedules`
- `campaigns`
- `campaign_accounts`
- `activities`

## Related Services

- `SchedulerService`
- `SchedulerRuntime`
- `CampaignService`
- `WorkflowService`
- `ActivityService`

## Sequence Diagram

```text
FastAPI startup
  -> scheduler_lifespan
  -> SchedulerRuntime.start
  -> ScheduleRepository.list_enabled
  -> APScheduler.add_job

Job fires
  -> SchedulerRuntime.run_schedule
  -> SchedulerService.execute_schedule
  -> CampaignService.run
  -> WorkflowService.run_workflow
  -> update campaign_schedules
  -> ActivityService.record
```

## Extension Guide

- Keep scheduler execution delegated to CampaignService.
- Do not add browser automation inside SchedulerService.
- Do not run multiple active scheduler instances without distributed locking.
