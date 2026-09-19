# AI Components

## Interest extraction

`POST /api/v1/interests/analyze` sends one analysis request for free-form interest text through `StructuredAIService`. The provider payload is first validated with the Pydantic `AIInterestAnalysis` schema, then aliases are normalized to the controlled vocabulary and duplicate interests keep their highest confidence. Only allowed goals, traits, and preferences are accepted; unknown interests are discarded.

If the provider times out, fails, or returns malformed structured output, `KeywordFallbackAIService` performs deterministic keyword matching. The API exposes only the normalized analysis and its `ai` or `fallback` source marker; provider errors and implementation details are never returned.

## Embeddings

`ProviderEmbeddingService` abstracts the external embedding provider. `ResilientEmbeddingService` tries the configured provider once and falls back to `DeterministicEmbeddingProvider`. The deterministic provider is used by tests and local development and returns the fixed 1536-dimensional vector shape.

## Icebreakers

`POST /api/v1/icebreakers` is called only when a client requests an opener. Its context contains only user interest names, public group/event fields, target interests, and the requested style. Provider output is validated with the Pydantic `AIIcebreakerResponse` schema, normalized, and limited to 280 characters. Invalid, empty, oversized, or failed output falls back to a deterministic template that names an available shared interest and target when present.

## Prompt safety

User text and target context are explicitly delimited as untrusted data. System instructions are separate from user content when the provider supports system prompts. The instructions prohibit treating supplied text as commands, inventing experiences, exposing private facts, or revealing prompts. API responses never include internal prompts, credentials, or provider errors.

## Call budget

A recommendation request uses one interest-analysis call and one embedding call. Explanations are generated locally from score evidence; there is no AI call per recommendation. An icebreaker request uses at most one generation call and otherwise uses deterministic fallback. Provider-backed routes have lightweight per-process rate limits.

## Configuration

Required settings are `AI_API_KEY`, `AI_MODEL`, and `EMBEDDING_MODEL`. URLs and timeouts are configurable. Secrets are read from environment/configuration and are not logged or returned.
