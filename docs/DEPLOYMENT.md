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

The final verification uses a clean `postgres:16` container, upgrades both migrations, seeds twice, builds the backend image, starts the API, and exercises every documented route family.

## Frontend integration

The frontend API client reads `VITE_API_BASE_URL` and strips a trailing slash. Set:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_API_MODE=api
VITE_DEMO_USER_ID=89d4a21e-b315-515f-8ff3-80b56e85ed6c
```

Use `VITE_API_MODE=mock` to keep deterministic local data without a backend. The default mode is API.

The centralized frontend services select the API or mock adapter at startup. Components should continue calling the services rather than `fetch` directly:

1. `profileService.getProfile()` -> `GET /profile/{userId}`.
2. `profileService.updateInterests()` -> `PUT /profile/{userId}` with `{ interests }`.
3. Recommendation submit -> `POST /recommendations` with `{ user_id, interest_text, limit }`.
4. Group/event lists and details -> `/groups` and `/events` endpoints.
5. Icebreaker dialog -> `POST /icebreakers` using the recommendation target type/ID and selected style.
6. Feedback buttons -> `POST /feedback` using the persisted recommendation `id` and one allowed feedback type.
7. Analysis-only UI -> `POST /interests/analyze` with `{ text }`.

The frontend accepts the live direct response bodies and also contains compatibility handling for an optional envelope. On failure display a generic message and preserve the returned HTTP status for retry/duplicate handling. Keep the UUID user ID in application state; there is no authentication endpoint in this submission.

## Checks run

Frontend `npm run lint`, `npm run typecheck`, and `npm run build` passed in the current workspace. The backend test command could not be run in the current `.venv` because `pytest` is not installed there. No committed artifact verifies an exact historical backend count, Docker build result, or coverage result.

## Limitations

In-memory rate limits are process-local and reset on restart. Synchronous SQLAlchemy sessions are used from async handlers. Embeddings are stored as optional JSON and are not used for baseline retrieval; structured matching is the required MVP path. External AI availability affects provider-backed generation, but configured deterministic fallbacks cover analysis and embeddings.
