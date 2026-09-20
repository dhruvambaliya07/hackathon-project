# Aatmoday Connect Live Demo Backup Plan

This runbook is for the frozen hackathon build. It uses the real frontend, backend APIs, PostgreSQL seed data, and the implemented deterministic fallback. It does not use a fake video, fabricated recommendation, or invented API response.

## 1. Primary Live Demo Flow

Use the normal API-backed flow:

1. Open the landing page.
2. Click **Discover My Communities**.
3. Enter:

   > I love photography, technology and meeting new people. I want to find creative communities and events where I can learn and collaborate.

4. Click **Analyze my interests**.
5. Show the structured profile: interests, categories, goals, traits, and confidence signals.
6. Click **Show My Matches**.
7. Point out that the score, matched interests, matched goals, reasons, and explanation come from the recommendation response.
8. Open a recommended community or event.
9. Show **Why you match** and the upcoming event information.
10. Click **Start a Conversation**.
11. Choose a tone if useful, copy the icebreaker, and click **I'm Interested** on the recommendation.

The central sentence is:

> The student gives us their words; the system turns them into understanding, a transparent match, and a first sentence to start connecting.

## 2. If Gemini Succeeds

Continue normally. In the profile, the source is `ai`. Explain that:

- the model returns structured JSON,
- the backend validates it with Pydantic,
- categories are derived from the controlled vocabulary,
- the backend then ranks communities and events from the structured signals.

Do not claim that Gemini computes the recommendation score. The backend matching service owns that score.

## 3. If Gemini Returns HTTP 503

Do not retry repeatedly and do not change the model during the demo.

Say:

> The external model provider is temporarily unavailable, so the application has switched to its deterministic fallback. The same product flow remains usable: we still extract controlled interests, rank seeded communities and events, explain the evidence, and generate an icebreaker from real shared interests.

Continue with the profile. The profile source will be `fallback`, and the UI presents that as a usable result rather than a crash. Show the recommendation evidence and the fallback icebreaker.

## 4. If the Backend Is Temporarily Unavailable

1. Check health:

   ```powershell
   Invoke-WebRequest http://localhost:8000/api/v1/health
   ```

2. Restart the database and backend using the commands in **Restart Commands**.
3. Refresh the browser.
4. If the outage persists, show the frontend retry/error state and switch to the **30-Second Emergency Demo** only after the backend is restored.

Do not claim that the frontend can provide real recommendations while the backend is down. Mock mode is not the real demo path.

## 5. If the Frontend Fails to Load

1. Confirm the backend health endpoint first.
2. From `frontend/`, reinstall from the lockfile if needed:

   ```powershell
   npm ci
   npm run typecheck
   npm run lint
   npm run build
   ```

3. Start the dev server with API mode explicitly enabled:

   ```powershell
   $env:VITE_API_MODE = "api"
   $env:VITE_API_BASE_URL = "http://localhost:8000/api/v1"
   $env:VITE_DEMO_USER_ID = "89d4a21e-b315-515f-8ff3-80b56e85ed6c"
   npm run dev -- --host localhost --port 5173
   ```

4. Open `http://localhost:5173/` and perform a hard refresh.

If the browser is showing an old tab, close it and open the URL again. Do not switch to mock mode for the judge flow unless the goal is only to demonstrate static UI layout.

## 6. Pre-Seeded Demo-Ready Flow

The PostgreSQL seed is deterministic and idempotent. Prepare it before judging:

```powershell
cd backend
docker compose up -d db
docker compose run --rm api alembic upgrade head
docker compose run --rm api python -m app.seed
docker compose up api
```

Then start the API-backed frontend with the configuration in **Restart Commands**.

If Gemini is unavailable, use the same seeded flow with fallback. The fallback still uses real API routes and real seeded communities/events. It does not fabricate recommendations. The key judge sequence is:

`/discover -> Analyze -> Show My Matches -> open a result -> Why you match -> Start a Conversation -> feedback`

The stable demo user is:

```text
89d4a21e-b315-515f-8ff3-80b56e85ed6c
```

Do not invent or manually type a recommendation score, community, event, or icebreaker.

## 7. Short Judge Explanation About AI Availability

> Gemini is an external dependency and can occasionally return a temporary 503. We designed the product so provider availability does not destroy the user journey: structured interest extraction, embeddings, and icebreakers each have deterministic fallbacks. The demo still shows real API responses, seeded catalog data, backend-owned ranking, and evidence-based explanations. The fallback is a resilience mechanism, not a fake result.

## 8. Restart Commands

### Database and backend with Docker

Run from `backend/`:

```powershell
docker compose up -d db
docker compose run --rm api alembic upgrade head
docker compose run --rm api python -m app.seed
docker compose up api
```

Health check:

```powershell
Invoke-WebRequest http://localhost:8000/api/v1/health
```

### Backend directly from the local Python environment

Use the existing `backend/.env` for the normal provider-backed run:

```powershell
cd backend
alembic upgrade head
python -m app.seed
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

For a deliberate fallback rehearsal, override only the process environment; do not edit source or rotate credentials:

```powershell
cd backend
$env:AI_API_KEY = "test-key"
$env:AI_MODEL = "test-model"
$env:DATABASE_URL = "postgresql+psycopg://aatmoday:aatmoday@localhost:5432/aatmoday"
$env:CORS_ORIGINS = "http://localhost:5173"
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Frontend directly

Run from `frontend/`:

```powershell
npm ci
$env:VITE_API_MODE = "api"
$env:VITE_API_BASE_URL = "http://localhost:8000/api/v1"
$env:VITE_DEMO_USER_ID = "89d4a21e-b315-515f-8ff3-80b56e85ed6c"
npm run dev -- --host localhost --port 5173
```

## 9. Thirty-Second Emergency Demo

1. Start from `/discover`, not the landing page.
2. Paste the prepared student sentence.
3. Click **Analyze my interests**.
4. Say: "This is the structured profile the system understood, including interests and goals."
5. Click **Show My Matches**.
6. Point to one score and one **Why this matches** explanation.
7. Open that result and click **Start a Conversation**.
8. Read the generated or deterministic fallback icebreaker.

Closing line:

> Aatmoday Connect turns a student's words into a reason to show up and a sentence to say when they arrive.

## What Not To Do During the Demo

- Do not repeatedly retry Gemini after a 503.
- Do not change models or API keys live.
- Do not switch the real demo to mock mode.
- Do not invent a score, recommendation, matching reason, or AI response.
- Do not expose provider errors or credentials to judges.
- Do not describe future authentication, chat, notifications, or moderation as implemented features.
