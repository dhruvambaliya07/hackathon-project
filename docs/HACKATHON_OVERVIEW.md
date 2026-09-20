# Aatmoday Connect

Aatmoday Connect helps students move from "what I like" to "where I belong". It finds relevant seeded communities and events, explains the match, and helps the student start a conversation.

## Problem

Students often describe their interests naturally, while communities and events are organized as catalog entries and categories. A list alone does not show which option fits or how to approach a new community.

## Solution

The application converts natural-language interests into a validated profile, ranks groups and events using multiple signals, returns the evidence behind each match, and generates a short icebreaker on demand.

The current application is a discovery and recommendation experience. It does not create events or groups, manage memberships, provide messaging, or implement authentication.

## How It Works

The core technical path is:

```text
Student natural-language input
  -> interest extraction
  -> normalized structured profile
  -> candidate retrieval
  -> hybrid matching
  -> ranked recommendations
  -> evidence-based explanation
  -> personalized icebreaker
```

The React frontend calls the FastAPI REST API. The API validates requests, persists profile and recommendation state through SQLAlchemy, reads seeded PostgreSQL catalog data, and calls configurable OpenAI-compatible providers when available.

## User Journey

1. The student enters a description such as interests, goals, or activities.
2. The system extracts normalized interests, confidence values, goals, traits, and preferences.
3. The structured signals are shown as a profile and recognized interests can be persisted for the demo user.
4. The backend retrieves up to 100 groups and 100 events, ranks them, and returns recommendation records.
5. Each result shows a score, matched interests, matched goals, reasons, and an explanation.
6. The student browses group and event details.
7. The student requests a casual, friendly, or professional icebreaker for a selected target.
8. The student submits recommendation feedback such as `interested` or `wrong_match`.

## AI Architecture

The backend uses configurable OpenAI-compatible HTTP endpoints:

- `AI_API_URL` and `AI_MODEL` configure chat completion requests.
- `EMBEDDING_API_URL` and `EMBEDDING_MODEL` configure embedding requests.
- Timeouts and the fixed `EMBEDDING_DIMENSION=1536` are configurable within validated limits.

Interest analysis requests structured JSON containing interests, goals, traits, and preferences. Pydantic validates the response. Interests are normalized to a controlled vocabulary, aliases are handled, categories are assigned by the server, and unsupported values are discarded.

Embeddings are attempted for recommendation input and catalog candidates. They are stored as JSON arrays; the current system does not use pgvector or a vector database.

Icebreakers are generated only when requested. Their context is limited to user interest names, public group/event details, target interests, and the selected style.

## Recommendation Engine

Recommendation ranking is local application logic, not a model-generated score. It combines:

| Signal | Default weight |
| --- | ---: |
| Semantic similarity | 0.50 |
| Interest overlap | 0.25 |
| Goal compatibility | 0.15 |
| Event relevance | 0.10 |

The result is normalized to `0-100`. Recommendation records are persisted and carry the IDs used by feedback and icebreaker flows. Explanations are assembled from the same score evidence: matched interests, matched goals, semantic relevance, and event/group context.

## Why This Is More Than an LLM Wrapper

The provider is only one input to a larger, testable system:

- Structured output is validated and constrained instead of being rendered directly.
- The backend normalizes interests and derives controlled categories.
- PostgreSQL stores profiles, catalog relationships, recommendations, and feedback.
- Candidate retrieval is bounded and deterministic.
- Hybrid ranking is implemented in local Python with explicit weights.
- Explanations are generated from scoring evidence, not invented by a free-form model call.
- Recommendation IDs connect ranking to feedback and later user state.
- Deterministic fallbacks keep the main journey usable when a provider fails.

## Technology Stack

- **Frontend:** React, TypeScript, Vite, React Router, TanStack React Query, Tailwind CSS, Framer Motion, and Lucide React.
- **Backend:** Python 3.12, FastAPI, Pydantic, SQLAlchemy, Psycopg, Alembic, HTTPX, and Uvicorn.
- **Data:** PostgreSQL 16 with JSON-stored 1536-dimensional embeddings.
- **Testing:** Pytest backend tests with SQLite and PostgreSQL-gated integration coverage; frontend TypeScript, ESLint, and Vite build checks.
- **Local infrastructure:** Docker Compose for PostgreSQL and the API container.

## Reliability and Fallbacks

- Interest analysis falls back to deterministic keyword and alias matching after provider failure, timeout, malformed output, or placeholder keys.
- Embedding failure falls back to a deterministic SHA-256-derived 1536-value vector.
- Icebreaker failure falls back to a short template based on real shared interests and public target details.
- Recommendation explanations are deterministic local output and do not require a second AI call per result.
- FastAPI returns generic provider errors rather than exposing credentials or provider internals.
- Rate limits are applied in memory to interest analysis, recommendations, and icebreakers.

These fallbacks preserve continuity; they are not claimed to be equivalent to a learned model.

## Testing and Validation

The repository contains backend tests for API validation, AI parsing and fallback, matching, embeddings, icebreakers, recommendations, profiles, feedback, security controls, seed behavior, and PostgreSQL-backed flows.

In the current workspace validation on 2026-09-20:

- `npm run typecheck`: passed.
- `npm run lint`: passed with zero warnings allowed.
- `npm run build`: passed.
- Backend `pytest` did not run because `pytest` was not installed in the active `.venv`; no unverified backend test count is claimed here.

The frontend has no separate automated test script. PostgreSQL integration tests require a running PostgreSQL 16 database and migrations.

## Security Considerations

- Request bodies use strict Pydantic schemas with bounded text, list, UUID, enum, and pagination values.
- User text and target context are marked as untrusted data in AI prompts.
- Provider credentials are backend environment variables and are not exposed to the frontend or API responses.
- CORS requires explicit origins; wildcard origins are rejected.
- Provider-backed routes have process-local rate limits.
- Unexpected failures return generic messages.
- Authentication and authorization are not implemented, so the demo user UUID must not be treated as an access-control boundary.

## Limitations

- The default API flow uses one seeded demo user and has no authentication.
- Group/event saved or interested UI state is partly browser-local rather than a complete server-side workflow.
- Embeddings are JSON and are not vector-indexed.
- Candidate retrieval is limited to 100 groups and 100 events per recommendation request.
- Rate limits are per process and reset on restart.
- Database work uses synchronous SQLAlchemy sessions inside FastAPI handlers.
- There are no real-time updates, notifications, messaging, group creation, event creation, membership, or registration workflows.

## Future Scope

Possible next steps are authentication and authorization, server-side saved-item persistence, group membership and event registration, richer pagination metadata, vector indexing for larger catalogs, production observability, and background embedding/indexing jobs. These are not current features.
