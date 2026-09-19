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

The deterministic seed creates 30 interests, 20 groups, 40 events, 5 users, 100 group-interest links, 160 event-interest links, and 25 user-interest links. UUID5 identifiers and upsert behavior make repeated runs idempotent. This was verified by running the seed twice against clean PostgreSQL.

## Frontend rule

Do not expose database credentials or connect directly from the browser. Frontend code must call the API endpoints and use UUIDs returned in API responses.
