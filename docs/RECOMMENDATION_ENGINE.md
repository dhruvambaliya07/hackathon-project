# Recommendation Engine

## Inputs

The engine combines:

- one user embedding generated from the submitted interest text
- persisted user interest weights
- AI/fallback structured interests from the same text
- profile-derived goals
- group and event embeddings
- group/event interest weights
- event schedule and group relevance

## Retrieval

PostgreSQL retrieves at most 100 groups and 100 events with deterministic ordering. Candidate relationships are eager-loaded to avoid an N+1 query per candidate. Optional embeddings are retained as JSON for future vector indexing but are not required by the MVP.

## Scoring

The default weights are:

- semantic similarity: `0.50`
- interest overlap: `0.25`
- goal compatibility: `0.15`
- event relevance: `0.10`

The weighted score is normalized to 0-100. If an embedding is missing, available scoring components are reweighted rather than failing the candidate. Interest and goal evidence is normalized and sorted for deterministic output.

Event relevance combines schedule proximity, event interest overlap, and group-interest relevance. It is bounded to 0-1 and never depends on date alone.

## Output

Each returned item contains a persisted recommendation ID, target type/ID, title, description, score, matched interests, reasons, and deterministic explanation. The persisted recommendation ID is required by `POST /api/v1/feedback`.

## Empty and failure behavior

An empty candidate set returns a successful response with an empty recommendations list. Missing users return `404`. Provider failures return a safe `502` unless deterministic embedding/keyword fallback handles them. Database storage failures return `503`.

## Frontend consumption

Use `data.recommendations`, render `reasons` and `explanation`, and retain `id`, `target_type`, and `target_id` for icebreakers and feedback. Do not reconstruct recommendation IDs from target IDs.
