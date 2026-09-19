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
