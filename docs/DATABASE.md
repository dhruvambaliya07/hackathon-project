# Database

## Engine and storage

The application uses PostgreSQL 16 through SQLAlchemy 2 and Psycopg 3. Alembic manages schema changes. The embedding dimension is fixed at 1536.

There is no pgvector extension, vector column, or vector index. Group and event embeddings are nullable JSON arrays. Recommendation ranking runs in application code.

## Tables and important fields

- `users`: UUID, name, unique email, avatar URL, bio, JSON goals and traits, timestamps.
- `interests`: UUID, unique canonical name, category, timestamp.
- `user_interests`: composite user/interest key, weight, source, timestamp.
- `groups`: UUID, name, description, category, location, meeting frequency, member count, optional JSON embedding, timestamps.
- `group_interests`: composite group/interest key and bounded weight.
- `events`: UUID, group ID, name, description, start/end times, location, capacity, optional JSON embedding, timestamps.
- `event_interests`: composite event/interest key and bounded weight.
- `recommendations`: UUID, user ID, target type/ID, score from 0 to 1, JSON reason, timestamp.
- `feedback`: UUID, user ID, nullable recommendation ID, target type/ID, feedback type, timestamp.

## Relationships

- A user has many `user_interests`, recommendations, and feedback records.
- An interest can be linked to users, groups, and events.
- A group has many group-interest links and events.
- An event belongs to one group and has many event-interest links.
- A recommendation belongs to a user. Its `target_type` and `target_id` are an application-level pair; there is no polymorphic foreign key to groups/events.
- Feedback belongs to a user and optionally references a recommendation. Deleting a recommendation sets that reference to `NULL`.
- User, group, event, and interest links cascade on parent deletion.

## Constraints and indexes

Important constraints include unique user email, unique interest name, composite link keys, bounded weights, recommendation score range, nonnegative group member counts and event capacities, valid event end times, and unique `(user_id, recommendation_id, feedback_type)` feedback.

Indexes include:

- `users.email`
- `interests.name` and `interests.category`
- `groups.name` and `groups.category`
- `events.group_id`, `events.name`, and `events.start_time`
- `recommendations.user_id` and `(target_type, target_id)`
- `feedback.user_id` and `feedback.recommendation_id`
- interest IDs in relationship tables

UUID primary keys support detail lookups.

## Migrations

The current Alembic head is `0002_profile_feedback_state`.

- `0001_initial`: creates the base tables, relationships, constraints, indexes, and JSON embedding columns.
- `0002_profile_feedback_state`: adds JSON `users.goals` and `users.traits`, then prevents duplicate feedback for the same user, recommendation, and feedback type.

Apply migrations from `backend/` with `alembic upgrade head`.

## Seed data

Run:

```powershell
python -m app.seed
```

The deterministic seed creates or updates:

- 34 interests
- 20 groups
- 40 future events
- 5 users
- 100 group-interest links
- 160 event-interest links
- 25 user-interest links

It uses stable UUID5 identifiers and upsert behavior, so repeated runs are intended to be idempotent. The seeded event schedule starts at `2026-10-05`. Group goal metadata used in matching is held in Python (`GROUP_GOALS`), not in a separate database table.

## Local PostgreSQL

Docker Compose starts PostgreSQL with:

```text
Database: aatmoday
User: aatmoday
Password: aatmoday
Port: 5432
URL: postgresql+psycopg://aatmoday:aatmoday@localhost:5432/aatmoday
```

These are local development credentials only. Do not reuse them for production.
