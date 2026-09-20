# AI and Recommendation Behavior

## Provider configuration

The backend implements OpenAI-compatible HTTP providers. It does not contain a vendor-specific Gemini integration.

- `AI_API_KEY`: bearer credential for chat and embedding requests.
- `AI_MODEL`: chat completion model name.
- `AI_API_URL`: chat endpoint; default `https://api.openai.com/v1/chat/completions`.
- `AI_TIMEOUT_SECONDS`: chat timeout; default `10`, maximum `60`.
- `EMBEDDING_MODEL`: embedding model name.
- `EMBEDDING_API_URL`: embedding endpoint; default `https://api.openai.com/v1/embeddings`.
- `EMBEDDING_TIMEOUT_SECONDS`: embedding timeout; default `10`, maximum `60`.
- `EMBEDDING_DIMENSION`: fixed at `1536` by configuration validation and schema design.

`AI_API_KEY=test-key` or `replace-me` selects the deterministic AI service for interest analysis and icebreakers. Do not place real keys in source control or frontend variables.

## Interest extraction

`POST /api/v1/interests/analyze` sends free-form text to `StructuredAIService` when a real provider is configured. The prompt requests JSON with:

- `interests`: names and confidence values from 0 to 1.
- `goals`: allowed values such as `learn`, `create`, `meet_people`, and `build_career`.
- `traits`: allowed values such as `creative`, `technical`, and `collaborative`.
- `preferences`: allowed values such as `beginner_friendly`, `hands_on`, and `low_pressure`.

The response is parsed as raw JSON, a complete JSON code fence, or one unambiguous JSON object. Strict Pydantic validation rejects extra fields and malformed structures. Interests are normalized through aliases, limited to the controlled vocabulary, deduplicated using the highest confidence, and assigned categories server-side. Unknown goals, traits, and preferences are discarded.

## Embeddings

Recommendations attempt one call to the configured embedding endpoint. The provider response must contain a list with exactly 1536 values. Embeddings are stored as nullable JSON arrays on groups and events and are not stored in pgvector or queried through a vector index.

When embedding generation fails, `ResilientEmbeddingService` uses a deterministic SHA-256-derived vector of the required dimension. This keeps local and test flows operational but is not a learned semantic embedding.

## Recommendation logic

Recommendation ranking is local Python code in `MatchingService` and `RecommendationService`. It combines:

| Signal | Default weight |
| --- | ---: |
| Semantic similarity | 0.50 |
| Interest overlap | 0.25 |
| Goal compatibility | 0.15 |
| Event relevance | 0.10 |

The weighted result is normalized to `0-100`. Candidate retrieval is bounded to 100 groups and 100 events. Group and event candidate goals are derived from category and the seed module's `GROUP_GOALS` mapping.

Each returned item includes matched interests, matched goals, event connection, reasons, and a deterministic explanation. There is no AI request for each result.

## Explanation generation

`deterministic_explanation` builds text from the score breakdown. It mentions matched interests, compatible goals, event relevance, and rounded semantic relevance. The recommendation explanation is therefore evidence-based local output, not necessarily AI-generated.

## Icebreaker generation

`POST /api/v1/icebreakers` is called on demand. The context contains the user's interest names, public target details, target interests, and selected style (`casual`, `friendly`, or `professional`). AI output must be a non-empty string of at most 280 characters. The service does not invent private facts or experiences.

## Failure handling and deterministic fallback

- Provider timeout, HTTP failure, malformed JSON, invalid structured output, placeholder key, or empty/oversized icebreaker output triggers a local fallback where implemented.
- Interest fallback uses deterministic keyword and alias matching and returns `source: "fallback"`.
- Embedding fallback always returns a stable 1536-dimensional vector for the same normalized text.
- Icebreaker fallback uses a short template based on a shared interest and target name when available.
- If a provider-backed operation cannot recover, the API returns a safe generic `502` response without provider details.

User text is delimited as untrusted data in prompts. Provider credentials and internal prompts are not returned by the API.
