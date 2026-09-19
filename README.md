# hobby-matchmaker
AI-powered hobby matchmaker for Aatmoday. Students describe their interests and get relevant group/event recommendations with explanations + personalized icebreakers.

## Database

The backend uses standard PostgreSQL 16. Embeddings are optional JSON data in the MVP; structured interest matching is the required baseline. The initial Alembic migration creates:

`users`, `interests`, `groups`, `group_interests`, `events`, `event_interests`, `user_interests`, `recommendations`, and `feedback`.

Groups and events include nullable 1536-dimensional embeddings for OpenAI `text-embedding-3-small`. The dimension is intentionally fixed in the ORM and migration; selecting a different embedding model requires a coordinated schema migration.

From `backend/`, configure `.env` from `.env.example`, then run:

```bash
docker compose up -d db
alembic upgrade head
pytest
alembic downgrade base
alembic upgrade head
```

## Deterministic seed data

After applying migrations, run the local seed command from `backend/`:

```bash
python -m app.seed
```

The seed creates or updates 30 interests, 20 communities, 40 future events, 5 demo users, 100 group-interest links, 160 event-interest links, and 25 user-interest links. IDs are stable UUID5 values, so running the command repeatedly does not create duplicates. It also writes stable local 1536-dimensional vectors for groups and events; production embedding providers can replace these during a coordinated indexing process.

## Personalized icebreakers

`POST /api/v1/icebreakers` accepts `user_id`, `target_type` (`group` or `event`), `target_id`, and `style` (`casual`, `friendly`, or `professional`). The response contains one short icebreaker. The backend uses only the user's interest names and public target details; provider failures use a deterministic template.

## Profiles and recommendation feedback

`GET /api/v1/profile/{user_id}` returns the public profile, weighted interests, goals, derived traits, groups marked `interested`, and events marked `interested`. `PUT` accepts `name`, `bio`, `interests`, and `goals`.

`POST /api/v1/feedback` accepts a user-owned `recommendation_id` and one of `interested`, `not_interested`, `already_joined`, or `wrong_match`. Duplicate feedback of the same type is rejected. `interested` and `wrong_match` adjust matching interest weights by a bounded deterministic amount; the other feedback types record state without changing weights.

## Integrated recommendation flow

The recommendation endpoint validates the user, analyzes free-form interest text, persists recognized interests, generates an embedding with a deterministic fallback, retrieves groups and events, calculates hybrid scores, persists recommendation records, and returns evidence-based reasons. Those recommendation IDs feed the icebreaker and feedback endpoints, so interested feedback is reflected in the next profile response. Provider failures return safe API errors or use local deterministic fallbacks; private provider details are never returned.

## Security and performance controls

`CORS_ORIGINS` must contain explicit origins; wildcard credentialed CORS is rejected. Provider-backed endpoints use lightweight per-process request limits, bounded request fields, UUID validation, safe generic errors, and prompt delimiters that mark user text as untrusted data. Recommendations make one analysis call and one embedding call per request, then use bounded vector retrieval and local hybrid scoring; no per-recommendation AI loop is used. Health responses expose only `ok`/`unavailable` database status and the application version.

## Backend tests

Run `pytest` from `backend/`. The suite uses deterministic mocked AI and embedding providers, creates a local SQLite schema automatically, and exercises API behavior, validation, fallback paths, ranking, profile/feedback state, security controls, and seed idempotency. Catalog, lifecycle, and end-to-end database tests are PostgreSQL-gated. Coverage reporting requires the optional `pytest-cov` package.
