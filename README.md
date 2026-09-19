# Aatmoday Connect

Backend foundation for the Aatmoday hobby-community and event discovery API.

## Directory structure

`backend/app` contains the FastAPI application, versioned routers, Pydantic schemas, SQLAlchemy models, and service interfaces. `backend/migrations` contains Alembic configuration and the initial PostgreSQL/pgvector migration. `backend/tests` contains API contract tests.

## API contract

The API is rooted at `/api/v1` and documents itself at `/docs` and `/redoc`.

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/interests/analyze` | Analyze natural-language interests |
| POST | `/recommendations` | Return group/event recommendations |
| GET | `/groups` | List groups |
| GET | `/groups/{group_id}` | Get one group |
| GET | `/events` | List events |
| GET | `/events/{event_id}` | Get one event |
| POST | `/icebreakers` | Generate icebreakers |
| POST | `/feedback` | Submit feedback |
| GET/PUT | `/profile/{user_id}` | Read or update a profile |
| GET | `/health` | Check API and database health |

Successful and handled error responses use `{ "data": ..., "meta": ..., "error": ... }`. Recommendation, AI, matching, and persistence behavior is intentionally stubbed in this foundation release.

## Environment variables

Copy `backend/.env.example` to `backend/.env` and set `DATABASE_URL`, `AI_API_KEY`, `AI_MODEL`, `EMBEDDING_MODEL`, and `CORS_ORIGINS`. `CORS_ORIGINS` is a comma-separated list, for example `http://localhost:3000`.

## Run locally

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` for the interactive contract.

## Docker

```powershell
cd backend
Copy-Item .env.example .env
docker compose up --build
```

The compose file runs PostgreSQL with pgvector, applies migrations, and starts the API on port 8000.

## Tests and implementation phases

Run `pytest` from `backend`. The next phases are: implement PostgreSQL repositories and seed data; connect AI and embedding providers; implement semantic matching and recommendation ranking; add profile and feedback persistence; then expand integration and database tests.
