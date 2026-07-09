# API Documentation

Base path: `/api/v1`

## Accounts

### GET /accounts

Lists accounts. Optional query: `search`.

Response:

```json
[
  {
    "id": "uuid",
    "nickname": "Michael",
    "platform": "reddit",
    "username": "Michael-Geo",
    "status": "active"
  }
]
```

### POST /accounts

Creates an account.

```json
{
  "nickname": "Michael",
  "username": "Michael-Geo",
  "platform": "reddit",
  "status": "active",
  "notes": "Primary account"
}
```

### GET /accounts/{account_id}

Returns one account.

### PATCH /accounts/{account_id}

Partially updates an account.

### DELETE /accounts/{account_id}

Deletes an account.

### POST /accounts/{account_id}/sync-profile

Runs Reddit profile sync through the existing browser profile and returns the updated account.

## Browser Sessions

### POST /accounts/{account_id}/session/create

Creates storage directories, launches the persistent browser profile, and opens Reddit login.

### POST /accounts/{account_id}/session/finish

Persists Playwright storage state from the active manual login session.

### POST /accounts/{account_id}/session/validate

Validates the persistent session.

### POST /accounts/{account_id}/session/refresh

Refreshes session status by validation.

### DELETE /accounts/{account_id}/session

Deletes account session storage.

### POST /accounts/{account_id}/browser/open

Opens the persistent profile.

### POST /accounts/{account_id}/browser/open-home

Opens Reddit home in the persistent profile.

## Activities

### GET /activities

Query parameters: `limit`, `offset`, `activity_type`, `status`.

### GET /accounts/{account_id}/activities

Lists activity for one account.

### GET /activities/{activity_id}

Returns one activity.

### DELETE /activities/{activity_id}

Deletes one activity.

### POST /activities/test

Creates a synthetic test activity.

### POST /accounts/{account_id}/activities/test

Creates a synthetic test activity for one account.

## Upvote

### POST /upvote

Sequentially opens the target URL for selected accounts and attempts one Reddit upvote.

```json
{
  "account_ids": ["uuid"],
  "target_url": "https://www.reddit.com/r/test/comments/..."
}
```

Response:

```json
{
  "success": true,
  "results": [
    {
      "account": "Michael",
      "opened": true,
      "clicked": true,
      "verified": false,
      "reason": "verification_failed"
    }
  ]
}
```

## Campaigns

### GET /campaigns

Lists campaigns.

### POST /campaigns

Creates an UPVOTE campaign with account assignments and default workflow.

```json
{
  "name": "Warmup Upvote",
  "platform": "reddit",
  "action_type": "UPVOTE",
  "target_url": "https://www.reddit.com/r/test/",
  "account_ids": ["uuid"]
}
```

### GET /campaigns/{campaign_id}

Returns one campaign.

### DELETE /campaigns/{campaign_id}

Deletes one campaign.

### POST /campaigns/{campaign_id}/run

Runs the campaign through the Workflow Engine.

## Workflow

### GET /campaigns/{campaign_id}/workflow

Returns ordered workflow steps.

### POST /campaigns/{campaign_id}/workflow

Creates workflow steps by replacing existing steps.

### PUT /campaigns/{campaign_id}/workflow

Replaces workflow steps.

```json
{
  "steps": [
    {"action_type": "OPEN_URL", "config": {}},
    {"action_type": "WAIT", "config": {"min_seconds": 5, "max_seconds": 12}},
    {"action_type": "UPVOTE", "config": {}}
  ]
}
```

### POST /campaigns/{campaign_id}/workflow/run

Runs the workflow.

## Behavior Templates

### GET /behavior-templates

Lists templates.

### GET /behavior-templates/{template_id}

Returns one template.

### POST /behavior-templates

Creates a custom template.

### DELETE /behavior-templates/{template_id}

Deletes a custom template. Built-in templates are read-only.

### POST /campaigns/{campaign_id}/apply-template

Applies a template to a campaign workflow.

```json
{"template_id": "uuid"}
```

## Health

### GET /health

Lists health records.

### GET /accounts/{account_id}/health

Returns health for one account, evaluating if absent.

### POST /accounts/{account_id}/health/evaluate

Evaluates one account.

### POST /health/evaluate-all

Evaluates all accounts.

## Recommendations

### GET /recommendations

Lists recommendation records.

### GET /accounts/{account_id}/recommendations

Lists recommendation records for one account.

### POST /recommendations/evaluate-all

Evaluates recommendations for all accounts.

### POST /accounts/{account_id}/recommendations/evaluate

Evaluates recommendations for one account.

### POST /recommendations/{recommendation_id}/dismiss

Marks a recommendation as dismissed.

