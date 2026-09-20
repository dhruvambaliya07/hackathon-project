# Testing

## Test architecture

Backend tests live in `backend/tests` and use Pytest. Most tests use SQLite configured by `tests/conftest.py`; provider calls are replaced with deterministic or mocked services. PostgreSQL-dependent modules are skipped unless `DATABASE_URL` points to PostgreSQL.

Coverage includes:

- API route registration, request validation, and status handling.
- AI JSON parsing, normalization, fallback, prompt safety, and rate limits.
- Deterministic embeddings and matching math.
- Recommendation ranking and persisted recommendation flow.
- Icebreaker generation and fallback.
- ORM constraints and seed constants/idempotency.
- Profile updates, feedback state, duplicate feedback, and security hardening.
- PostgreSQL catalog, profile/feedback, and end-to-end flow tests when PostgreSQL is available.

PostgreSQL-gated modules are `test_catalog_api.py`, `test_end_to_end_flow.py`, and `test_profile_feedback_api.py`.

## Backend commands

From `backend/` with the project virtual environment active:

```powershell
python -m pytest
```

For a PostgreSQL-backed run:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://aatmoday:aatmoday@localhost:5432/aatmoday"
alembic upgrade head
python -m pytest tests/test_catalog_api.py tests/test_end_to_end_flow.py tests/test_profile_feedback_api.py -q
```

The repository does not include a committed test report or coverage artifact. In the current workspace check, the backend command could not start because `pytest` is not installed in `.venv`; install `requirements.txt` before rerunning it. Historical test counts in other documents are not treated as current results.

## Frontend commands

From `frontend/`:

```powershell
npm run typecheck
npm run lint
npm run build
```

Current workspace results on 2026-09-20:

- `npm run typecheck`: passed.
- `npm run lint`: passed with `--max-warnings=0`.
- `npm run build`: passed; Vite produced the production bundle.

There is no frontend unit/integration test script in `frontend/package.json`.

## Integration testing

The API/database integration path requires PostgreSQL 16. Start the database, apply migrations, seed data, and run the PostgreSQL-gated modules as shown above. The tests exercise real SQLAlchemy persistence and route behavior; external AI and embedding network calls remain mocked or deterministic.

The live browser can be smoke-tested by starting the API and Vite, opening `http://localhost:5173`, entering natural-language interests, opening a recommendation, requesting an icebreaker, and submitting feedback. This is a manual flow, not an automated browser test in the repository.

## Important edge cases

- Blank or shorter-than-3-character text and text over 2,000 characters return `422`.
- Unexpected request fields are rejected by strict request schemas.
- Invalid UUIDs, enum values, dates, weights, capacities, and pagination values are rejected.
- AI timeout, provider failure, malformed JSON, and invalid structured output use deterministic fallbacks where implemented.
- Embedding provider responses with a dimension other than 1536 are rejected and trigger deterministic embedding fallback.
- Missing users, groups, events, or recommendations return `404`.
- Duplicate feedback of the same type returns `409`.
- Interest analysis, recommendations, and icebreakers have process-local `429` limits of 60, 30, and 30 requests per minute respectively.
- CORS wildcard configuration is rejected at settings validation time.

## Test limitations

The test harness creates SQLite tables for local tests, while PostgreSQL-specific behavior requires a separately running database. There is no committed coverage configuration or `pytest-cov` dependency. The application itself has no frontend test runner configured.
