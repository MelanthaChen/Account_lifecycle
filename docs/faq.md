# FAQ

## Is Reddit The Only Supported Platform?

Yes. Reddit is the only implemented provider. The provider abstraction is in place for future platforms.

## Does The App Store Reddit Passwords?

No. The user logs into Reddit manually in a Playwright Chromium window. The app persists browser profile state and `storage_state.json`.

## Where Are Sessions Stored?

```text
storage/reddit/<username>/
```

This directory contains the persistent Chromium profile and storage state.

## Does The App Use The Reddit API?

No. Current profile sync and workflow execution use Playwright browser automation.

## Does The Scheduler Use Celery Or Redis?

No. Scheduler Engine v1 uses in-process APScheduler. Only run one active backend scheduler instance unless distributed locking is added later.

## Can I Use Docker For Everything?

You can use Docker Compose for PostgreSQL immediately. Full browser automation from a container may require additional Playwright OS dependencies and display handling. Local backend execution is the recommended development path.

## What Is The First Workflow I Should Try?

1. Create an account.
2. Create and finish a session.
3. Validate the session.
4. Create a campaign.
5. Apply the Quick Upvote template.
6. Run the workflow.

## Are Demo Accounts Included?

No. Create your own Reddit account records locally. Do not commit real account storage.
