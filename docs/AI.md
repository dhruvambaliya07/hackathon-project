# AI Components

## Interest extraction

`StructuredAIService` sends one analysis request for free-form interest text and validates the returned JSON through `InterestAnalysis` and `parse_analysis`. Only the controlled vocabulary, allowed goals, and allowed traits are accepted. Unknown interests are discarded.

If the provider times out or returns a provider-level failure, `KeywordFallbackAIService` performs deterministic keyword matching. Malformed structured output is converted to a safe provider error at the API boundary.

## Embeddings

`ProviderEmbeddingService` abstracts the external embedding provider. `ResilientEmbeddingService` tries the configured provider once and falls back to `DeterministicEmbeddingProvider`. The deterministic provider is used by tests and local development and returns the fixed 1536-dimensional vector shape.

## Icebreakers

Icebreaker context contains only user interest names, public group/event fields, target interests, and the requested style. Provider output is normalized and limited to 280 characters. Empty or oversized output falls back to a deterministic template.

## Prompt safety

User text and target context are explicitly delimited as untrusted data. System instructions are separate from user content when the provider supports system prompts. The instructions prohibit treating supplied text as commands, inventing experiences, exposing private facts, or revealing prompts. API responses never include internal prompts, credentials, or provider errors.

## Call budget

A recommendation request uses one interest-analysis call and one embedding call. Explanations are generated locally from score evidence; there is no AI call per recommendation. An icebreaker request uses at most one generation call and otherwise uses deterministic fallback. Provider-backed routes have lightweight per-process rate limits.

## Configuration

Required settings are `AI_API_KEY`, `AI_MODEL`, and `EMBEDDING_MODEL`. URLs and timeouts are configurable. Secrets are read from environment/configuration and are not logged or returned.
