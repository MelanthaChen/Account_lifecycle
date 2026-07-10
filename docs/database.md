# Database Documentation

## Entity Relationship Diagram

```text
accounts
  | 1
  |----* activities
  |----1 account_health
  |----* account_recommendations
  |----* campaign_accounts *----1 campaigns
                               | 1
                               |----* workflow_steps
                               |----1 campaign_schedules

behavior_templates
  | 1
  |----* account_recommendations.recommended_template_id
```

## accounts

Purpose: stores managed account identity, status, session metadata, and synced Reddit profile fields.

Columns:

- `id` UUID primary key
- `nickname` string
- `username` string
- `status` enum: `active`, `paused`, `error`, `archived`
- `platform` enum: `reddit`
- `created_at`, `updated_at`
- `last_sync`
- `notes`
- `is_active`
- `session_path`
- `session_status`
- `last_login`
- `last_validation`
- `browser_profile`
- `provider`
- `browser_profile_path`
- `storage_directory`
- `launch_visible_browser`
- `display_name`
- `reddit_username`
- `avatar_url`
- `karma_post`
- `karma_comment`
- `cake_day`
- `verified_email`
- `is_nsfw`
- `is_moderator`
- `is_gold`
- `last_profile_sync`

Constraints:

- Unique `(platform, username)`

## activities

Purpose: audit log for account operations.

Columns:

- `id` UUID primary key
- `account_id` FK to `accounts.id`
- `platform`
- `activity_type`
- `status`
- `target_url`
- `title`
- `metadata`
- `started_at`
- `finished_at`
- `duration_ms`
- `created_at`, `updated_at`

Foreign keys:

- `account_id -> accounts.id ON DELETE CASCADE`

## campaigns

Purpose: reusable execution plan metadata.

Columns:

- `id` UUID primary key
- `name`
- `description`
- `platform`
- `action_type`: currently `UPVOTE`
- `target_url`
- `status`: `Draft`, `Ready`, `Running`, `Completed`, `Failed`
- `created_at`, `updated_at`

## campaign_accounts

Purpose: ordered campaign account assignment.

Columns:

- `campaign_id` FK to `campaigns.id`
- `account_id` FK to `accounts.id`
- `execution_order`

Constraints:

- Primary key `(campaign_id, account_id)`
- Unique `(campaign_id, account_id)`
- Unique `(campaign_id, execution_order)`

## workflow_steps

Purpose: ordered workflow actions for campaigns.

Columns:

- `id` UUID primary key
- `campaign_id` FK to `campaigns.id`
- `step_order`
- `action_type`: `OPEN_URL`, `WAIT`, `SCROLL`, `OPEN_POST`, `BACK`, `UPVOTE`
- `config` JSON
- `created_at`, `updated_at`

Constraints:

- Unique `(campaign_id, step_order)`

## campaign_schedules

Purpose: stores APScheduler-backed campaign run schedules.

Columns:

- `id` UUID primary key
- `campaign_id` FK to `campaigns.id`, unique
- `enabled` boolean
- `schedule_type`: `ONCE`, `DAILY`, `WEEKLY`, `CUSTOM_CRON`
- `cron_expression`
- `timezone`
- `next_run_at`
- `last_run_at`
- `last_status`
- `created_at`, `updated_at`

Foreign keys:

- `campaign_id -> campaigns.id ON DELETE CASCADE`

## behavior_templates

Purpose: reusable workflow definitions.

Columns:

- `id` UUID primary key
- `name`
- `description`
- `platform`
- `category`
- `workflow_json` JSON array
- `is_builtin`
- `created_at`, `updated_at`

Built-ins inserted by migration:

- Warm Up
- Quick Upvote
- Casual Reader
- Deep Reader

## account_health

Purpose: latest rule-based health assessment per account.

Columns:

- `id` UUID primary key
- `account_id` FK to `accounts.id`, unique
- `health_score`
- `health_status`: `HEALTHY`, `WARNING`, `CRITICAL`
- `risk_level`: `LOW`, `MEDIUM`, `HIGH`
- `signals` JSON
- `last_evaluated_at`
- `created_at`, `updated_at`

## account_recommendations

Purpose: read-only next-best action recommendations.

Columns:

- `id` UUID primary key
- `account_id` FK to `accounts.id`
- `recommendation_type`
- `priority`
- `title`
- `description`
- `recommended_template_id` nullable FK to `behavior_templates.id`
- `status`: `ACTIVE`, `DISMISSED`, `COMPLETED`
- `reason` JSON
- `created_at`, `updated_at`
