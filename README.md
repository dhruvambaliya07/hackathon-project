# hobby-matchmaker
AI-powered hobby matchmaker for Aatmoday. Students describe their interests and get relevant group/event recommendations with explanations + personalized icebreakers.

## Database

The backend uses PostgreSQL 16 with the `pgvector` extension. The initial Alembic migration creates:

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

The seed creates or updates 30 interests, 20 communities, 40 future events, 5 demo users, 100 group-interest links, 160 event-interest links, and 25 user-interest links. IDs are stable UUID5 values, so running the command repeatedly does not create duplicates. No external API or embedding service is used; embedding columns remain nullable until the recommendation pipeline generates embeddings.
