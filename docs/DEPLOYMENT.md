# Deployment

## Required environment

Create `backend/.env` with explicit values:

```env
DATABASE_URL=postgresql+psycopg://aatmoday:aatmoday@db:5432/aatmoday
AI_API_KEY=replace-with-provider-key
AI_MODEL=your-chat-model
EMBEDDING_MODEL=text-embedding-3-small
CORS_ORIGINS=http://localhost:5173
```

Use a secret manager for production credentials. Never commit `.env` or place provider credentials in frontend variables.

## Docker Compose

From `backend/`:

```powershell
docker compose up -d db
docker compose run --rm api alembic upgrade head
docker compose run --rm api python -m app.seed
docker compose up api
```

The normal API service command runs `alembic upgrade head` before Uvicorn. The API listens on port 8000 and the database on port 5432.

## Verification

- Health: `GET http://localhost:8000/api/v1/health`
- OpenAPI: `GET http://localhost:8000/openapi.json`
- Docs UI: `http://localhost:8000/docs`
- Database migration head: `alembic current`

The final verification used a clean `pgvector/pgvector:pg16` container, upgraded both migrations, seeded twice, built the backend image, started the API, and exercised every documented route family.

## Frontend integration

The frontend API client reads `VITE_API_BASE_URL` and strips a trailing slash. Set:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

The current frontend service modules still contain mock/local-storage implementations. To connect the UI, replace those service implementations with calls through `apiClient`:

1. `profileService.getProfile()` -> `GET /profile/{userId}`.
2. `profileService.updateInterests()` -> `PUT /profile/{userId}` with `{ name, bio, interests, goals }`.
3. Recommendation submit -> `POST /recommendations` with `{ user_id, interest_text, limit }`.
4. Group/event lists and details -> `/groups` and `/events` endpoints.
5. Icebreaker dialog -> `POST /icebreakers` using the recommendation target type/ID and selected style.
6. Feedback buttons -> `POST /feedback` using the persisted recommendation `id` and one allowed feedback type.
7. Analysis-only UI -> `POST /interests/analyze` with `{ text }`.

Every call must unwrap `payload.data`; on failure display a generic message and preserve the returned HTTP status for retry/duplicate handling. Keep the UUID user ID in application state; there is no authentication endpoint in this submission.

## Checks run

Backend: `pytest` completed with 41 passed and 12 PostgreSQL-gated skips in the local test environment. Frontend `npm run lint`, `npm run typecheck`, and `npm run build` passed. Backend Docker image build passed. Coverage was not available because `pytest-cov` is not installed.

## Limitations

In-memory rate limits are process-local and reset on restart. Synchronous SQLAlchemy sessions are used from async handlers. PostgreSQL is required for vector retrieval and full catalog/end-to-end tests. External AI availability affects provider-backed generation, but configured deterministic fallbacks cover analysis and embeddings.
