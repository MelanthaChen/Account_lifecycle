# System Architecture

## Overall Architecture

Account Lifecycle Platform follows a layered architecture:

```text
frontend/src/pages
  -> frontend/src/hooks
  -> frontend/src/api
  -> backend/app/api/v1 routers
  -> backend/app/services
  -> backend/app/repositories
  -> backend/app/models
  -> PostgreSQL
```

Browser automation is isolated behind `BrowserManager` and provider implementations under `backend/app/services/browser_sessions/`.

## Major Modules

```text
Accounts            Account records and profile metadata
Sessions            Manual login and persisted browser state
Browser             Provider registry and Playwright persistent contexts
Profile Sync        Reddit profile scraping
Activity            Audit log for account operations
Upvote              Sequential Reddit upvote attempts
Campaign            Reusable execution plans
Workflow            Ordered executable campaign steps
Behavior            WAIT, SCROLL, OPEN_POST, BACK behavior actions
Behavior Library    Reusable workflow templates
Health              Rule-based account scoring
Recommendation      Rule-based next-best actions
Dashboard           Frontend control center
```

## Responsibilities

```text
Routers
  - Parse HTTP input
  - Inject database sessions
  - Call services
  - Return schemas

Services
  - Enforce business rules
  - Coordinate repositories and providers
  - Own transactions

Repositories
  - Encapsulate SQLAlchemy queries
  - Return ORM models

Providers
  - Implement platform-specific browser/session behavior
  - Keep platform strings out of routers/services where possible
```

## Dependency Graph

```text
React UI
  -> FastAPI API
    -> AccountService
    -> BrowserSessionService -> BrowserManager -> ProviderRegistry -> RedditSessionProvider
    -> CampaignService -> WorkflowService -> BehaviorService / UpvoteService
    -> HealthService -> AccountRepository / Activity / Campaigns
    -> RecommendationService -> HealthService / BehaviorTemplateRepository
    -> ActivityService -> ActivityRepository
```

## Request Lifecycle

```text
HTTP request
  -> FastAPI router
  -> service dependency
  -> service method
  -> repository/provider calls
  -> commit when state changes
  -> Pydantic response
```

## Workflow Lifecycle

```text
Campaign workflow run
  -> load campaign
  -> load ordered account IDs
  -> load ordered workflow steps
  -> for each account
       -> for each step
            OPEN_URL/SCROLL/OPEN_POST/BACK -> BehaviorService -> BrowserManager
            WAIT                         -> asyncio.sleep
            UPVOTE                       -> UpvoteService
       -> stop at first failed step for that account
  -> mark campaign Completed or Failed
```

## Campaign Lifecycle

```text
POST /campaigns
  -> validate account IDs
  -> create Campaign
  -> create CampaignAccount rows with execution_order
  -> create default workflow: OPEN_URL, UPVOTE

POST /campaigns/{id}/run
  -> delegate to WorkflowService
```

## Browser Session Lifecycle

```text
Create Session
  -> BrowserSessionService
  -> BrowserManager
  -> RedditSessionProvider
  -> create storage/reddit/<account> directories
  -> launch persistent context
  -> open Reddit login
  -> keep active context in memory

Finish Session
  -> retrieve same active context
  -> write storage_state.json
  -> verify file exists and has size
  -> close context
  -> update account session fields
```

## Frontend Architecture

```text
pages/
  route-level screens
components/
  reusable UI and feature panels
hooks/
  TanStack Query wrappers
api/
  Axios request functions
types/
  frontend DTO contracts
store/
  lightweight Zustand state
```

