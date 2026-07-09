# Campaign Module

## Purpose

Represents reusable execution plans across selected accounts.

## Responsibilities

- Create UPVOTE campaigns.
- Assign ordered accounts.
- Create default workflows.
- Delete campaigns.
- Run campaigns through WorkflowService.

## Inputs

- `CampaignCreate`
- `campaign_id`

## Outputs

- `CampaignRead`
- `WorkflowRunResponse`

## Related APIs

- `GET /api/v1/campaigns`
- `POST /api/v1/campaigns`
- `GET /api/v1/campaigns/{campaign_id}`
- `DELETE /api/v1/campaigns/{campaign_id}`
- `POST /api/v1/campaigns/{campaign_id}/run`

## Related Database Tables

- `campaigns`
- `campaign_accounts`
- `workflow_steps`

## Related Services

- `CampaignService`
- `CampaignRepository`
- `WorkflowService`

## Sequence Diagram

```text
Create Campaign
  -> CampaignService
  -> validate accounts
  -> create campaign
  -> create campaign_accounts
  -> create default workflow
```

## Extension Guide

- Add campaign action enum values carefully.
- Define default workflow generation for new action types.
- Keep browser automation delegated to workflow step services.

