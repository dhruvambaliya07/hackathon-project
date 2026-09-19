# Database

## Engine

- PostgreSQL 16
- SQLAlchemy 2.x
- Alembic migrations
- Fixed embedding dimension: 1536

## Tables

- `users`: public profile, persisted goals/traits, timestamps
- `interests`: canonical interest vocabulary
- `user_interests`: user-interest weights and source
- `groups`: community metadata and nullable vector embedding
- `group_interests`: group-interest links and weights
- `events`: event metadata and nullable vector embedding
- `event_interests`: event-interest links and weights
- `recommendations`: user-owned ranked recommendation records
- `feedback`: user feedback and recommendation target state

## Migration lifecycle

Current head: `0002_profile_feedback_state`.

- `0001_initial`: base schema, foreign keys, checks, indexes, and optional JSON embedding columns
- `0002_profile_feedback_state`: user goals/traits and duplicate feedback constraint

Clean verification uses the standard `postgres:16` image; upgrade from an empty database reaches `0002_profile_feedback_state` without requiring a database extension.

## Integrity and indexes

Foreign keys protect user, recommendation, interest, group, and event link ownership. Check constraints bound scores, weights, counts, capacities, and event dates. Unique constraints protect user emails, canonical interests, link pairs, and duplicate feedback.

Verified indexes include:

- user email
- group name/category
- event name/group/start time
- recommendation user and target type/target ID
- feedback user and recommendation
- interest name/category
- group/event/user interest link targets

Primary keys cover UUID lookup for group, event, user, and recommendation detail endpoints.

## Seed

Run from `backend/` after migration:

```powershell
python -m app.seed
```

The deterministic seed creates 34 normalized interests, 20 groups, 40 events, 5 users, 100 group-interest links, 160 event-interest links, and 25 user-interest links. Every group has explicit goal metadata used by recommendation ranking. Event dates begin at the fixed future anchor `2026-10-05` rather than using the current date, so repeated runs produce the same schedule. UUID5 identifiers and upsert behavior make repeated runs idempotent; this was verified by running the seed twice against SQLite.

## Frontend rule

Do not expose database credentials or connect directly from the browser. Frontend code must call the API endpoints and use UUIDs returned in API responses.

## PostgreSQL test setup

Docker Compose provides PostgreSQL 16 with database `aatmoday`, user `aatmoday`, and password `aatmoday` on port `5432`. The local test connection string is:

```text
postgresql+psycopg://aatmoday:aatmoday@localhost:5432/aatmoday
```

Apply migrations before running PostgreSQL integration tests:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://aatmoday:aatmoday@localhost:5432/aatmoday"
alembic upgrade head
pytest tests/test_catalog_api.py tests/test_end_to_end_flow.py tests/test_profile_feedback_api.py -q
```

The repository's current PostgreSQL integration test modules contain nine legacy contract assertions that expect an `{data, meta}` response envelope, while the live routes and frontend use direct response bodies. One assertion also expects the previous 30-interest seed; the deterministic seed now contains 34 interests. These are test-contract mismatches, not PostgreSQL compatibility failures, and were left unchanged per the audit requirement not to alter tests merely to force a pass.
