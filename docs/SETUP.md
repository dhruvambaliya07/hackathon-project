# Windows Setup

These steps describe the current local development setup. Run PowerShell commands from `D:\hackathon-project` unless noted.

## Prerequisites

- Python 3.12.
- Node.js/npm compatible with the frontend lockfile.
- Docker Desktop with Docker Compose and the PostgreSQL 16 image available.

## Backend environment

```powershell
cd backend
Copy-Item .env.example .env
```

Edit `backend/.env` and keep credentials as placeholders or local-only values:

```env
DATABASE_URL=postgresql+psycopg://aatmoday:aatmoday@localhost:5432/aatmoday
AI_API_KEY=replace-with-provider-key
AI_MODEL=replace-with-provider-model
EMBEDDING_MODEL=text-embedding-3-small
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Other supported backend variables are `AI_API_URL`, `AI_TIMEOUT_SECONDS`, `EMBEDDING_API_URL`, `EMBEDDING_TIMEOUT_SECONDS`, `EMBEDDING_DIMENSION`, the four scoring weights, `ENVIRONMENT`, and `SQL_ECHO`. See `backend/.env.example` and `app/config.py` for defaults.

For deterministic interest and icebreaker fallback, use the placeholder key `replace-me` or `test-key`. Embeddings still attempt the provider and then use the deterministic embedding fallback.

## Python environment

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation for the current process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

## PostgreSQL with Docker

From `backend/`:

```powershell
docker compose up -d db
alembic upgrade head
python -m app.seed
```

The Compose database is exposed on port `5432` and uses the local credentials documented in `DATABASE.md`.

To run the API container instead of a local Python process:

```powershell
docker compose up --build
```

The API container runs `alembic upgrade head` before Uvicorn and listens on port `8000`.

## Start the backend directly

From `backend/`, after PostgreSQL and migration/seed setup:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Verify with `http://localhost:8000/api/v1/health`. OpenAPI is at `http://localhost:8000/docs`.

## Frontend setup

From `frontend/`:

```powershell
npm ci
Copy-Item .env.example .env
```

Set the API connection in `frontend/.env`:

```env
VITE_API_MODE=api
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_DEMO_USER_ID=89d4a21e-b315-515f-8ff3-80b56e85ed6c
```

Start Vite:

```powershell
npm run dev -- --host localhost --port 5173
```

Open `http://localhost:5173`. Set `VITE_API_MODE=mock` only for the bundled deterministic frontend mock mode.

## Troubleshooting

- **Database connection refused:** run `docker compose up -d db`, confirm Docker Desktop is running, and check that port `5432` is free.
- **Missing table errors:** from `backend/`, run `alembic upgrade head`, then `python -m app.seed`.
- **CORS errors:** set `CORS_ORIGINS` to the exact frontend origins, usually `http://localhost:5173,http://127.0.0.1:5173`; wildcard origins are rejected.
- **API unavailable in the browser:** confirm the backend is on port `8000` or update `VITE_API_BASE_URL`, then restart Vite after changing `.env`.
- **Provider errors:** use a valid provider key/model, or use `replace-me`/`test-key` to exercise deterministic analysis and icebreaker fallback. Embedding fallback remains available.
- **Port already in use:** change the Uvicorn or Vite port and update `DATABASE_URL`/`CORS_ORIGINS`/`VITE_API_BASE_URL` as applicable. The database port is controlled by `docker-compose.yml`.
- **PowerShell activation error:** use the process-scoped execution policy command above; do not change the machine-wide policy for this project.
