# Architecture

Aatmoday Connect is a FastAPI application backed by PostgreSQL 16 and pgvector. The frontend is a Vite React application.

## Backend layers

- `app/api/v1`: thin HTTP routes, dependency wiring, validation-to-status translation, and response envelopes.
- `app/schemas`: Pydantic request and response contracts.
- `app/services`: business logic for analysis, embeddings, matching, recommendations, icebreakers, profiles, feedback, and catalog queries.
- `app/models`: SQLAlchemy persistence models and relationships.
- `app/db`: engine/session lifecycle and declarative metadata.
- `migrations`: Alembic schema history.

Routes receive a request, resolve a session/service dependency, call one service operation, and return an `ApiResponse`. Provider calls and state changes are kept out of route handlers.

## End-to-end flow

1. The client submits a user ID and free-form interest text.
2. The AI service returns validated structured interests, goals, and traits, or keyword fallback output.
3. Recognized interests are persisted with bounded weights.
4. One embedding is generated; the provider has a deterministic fallback.
5. PostgreSQL/pgvector retrieves bounded group and event candidate sets.
6. Local matching calculates semantic, interest, goal, and event relevance signals.
7. Candidates are ranked and stored as recommendation records.
8. The client opens the target, requests an icebreaker, and submits feedback using the recommendation ID.
9. Feedback updates profile state and bounded relevant interest weights.

## Lifecycle and boundaries

`get_db` creates one SQLAlchemy session per request and closes it in `finally`. Mutating services commit their own transaction. Provider protocols allow deterministic test doubles without network access. Synchronous SQLAlchemy work is currently called from FastAPI handlers; this is simple and correct for the hackathon deployment, but a high-concurrency deployment should move blocking database work to a worker or async database driver.

## Error handling

Request validation is normalized by the application handler. HTTP details are not returned to clients. Unexpected errors return a generic internal error envelope. Provider-specific recommendation failures return safe `502`; recommendation storage failures return `503`. Health reports only status, database availability, and version.

## Testing

The test suite creates an empty SQLite schema for local non-PostgreSQL tests. Catalog, PostgreSQL lifecycle, and end-to-end database tests run against PostgreSQL when available. AI and embedding providers are mocked or deterministic.
