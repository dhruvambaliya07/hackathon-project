# Aatmoday Connect Presentation Package

## Strong Opening

"Students do not need another directory of clubs; they need a faster path from what they like to where they belong."

## Core Story

Student's words -> structured understanding -> personalized recommendations -> explainable matching -> a practical first conversation.

## 1. Problem Statement

Students often know they want to meet people or try something new, but campus communities are organized as lists and categories. The student has to translate natural interests into search terms, compare many options, and still does not know why a result fits or how to start a conversation.

## 2. Problem Explanation

The gap is not only discovery. It is interpretation and confidence:

- Students describe interests naturally, not in database vocabulary.
- Relevant groups and events are spread across a large catalog.
- A recommendation without evidence is difficult to trust.
- The first message is often the hardest part of joining a new community.

## 3. Solution Explanation

Aatmoday Connect turns one natural-language description into a structured interest profile, ranks seeded Aatmoday groups and events, shows the evidence behind every match, and generates an icebreaker on demand for the selected community or event.

The system is designed as one continuous journey:

1. Describe what you like.
2. Review what the system understood.
3. See ranked communities and events.
4. Inspect why a result matches.
5. Start a conversation.

## 4. Two-Minute Live Demo Script

**0:00-0:15 | Landing**

"This is Aatmoday Connect. The student starts with words, not filters. The promise is simple: describe what you like, discover where it fits, understand why, and get help starting the first conversation."

Click **Discover My Communities**.

**0:15-0:35 | Student's words**

Enter:

> I love photography, technology and meeting new people. I want to find creative communities and events where I can learn and collaborate.

Click **Analyze my interests**.

**0:35-0:55 | What the system understood**

"The text is converted into a structured profile: normalized interests, goals, traits, and confidence signals. This is the bridge between natural language and matching."

Point out interests such as photography and programming, plus goals such as learning and meeting people. If the provider is unavailable, explain that the visible result is the deterministic fallback, not an error screen.

Click **Show My Matches**.

**0:55-1:20 | What it recommends**

"The backend owns the ranking. Each card shows the score returned by the recommendation API, not a score recalculated in the browser."

Point to a community and an event. Mention the matched interest badges and the evidence sentence.

**1:20-1:40 | Why it matches**

Open a recommendation. Point to:

- matched interests,
- matched goals,
- semantic relevance or event connection,
- upcoming event information.

"The explanation is assembled from scoring evidence, so it does not invent a personal fact about the student."

**1:40-2:00 | Connect**

Click **Start a Conversation**, select a tone if useful, copy the generated icebreaker, and submit **I'm Interested** feedback.

"The icebreaker is requested only when the student asks for it. The recommendation response does not contain embedded conversation text. This turns relevance into an action the student can take immediately."

## 5. Five-Minute Presentation Script

### 0:00-0:40 | Hook and problem

"Finding a campus community should begin with a student's interests, not with a perfect search query. Today, a student may have a sentence like 'I love photography, technology and meeting new people,' but the available experience is usually a catalog of disconnected names. They still need to decide what fits and how to approach people."

### 0:40-1:20 | Product

"Aatmoday Connect closes that gap. It takes natural language, extracts a structured profile, ranks communities and events, explains the evidence, and gives the student a safe first line for a conversation."

Show the landing page and the four-step value proposition:

- Describe naturally.
- Discover your fit.
- See why it matches.
- Start connecting.

### 1:20-2:10 | Understanding

Run the exact demo input. Show the profile.

"The profile is not a black-box label. It exposes normalized interests, categories, confidence, goals, traits, and optional preferences. The server validates the model output against a strict Pydantic schema and derives controlled categories itself."

### 2:10-3:05 | Matching

Open recommendations.

"The recommendation service combines the submitted interest analysis, persisted profile signals, candidate group/event interests, optional embeddings, goals, and event context. The backend calculates and persists the score. The frontend only renders the returned score and evidence."

Show one group and one event. Point to the matched interests and goals.

### 3:05-3:45 | Explainability and connection

Open a detail page.

"Why this matches is made from the same evidence used in scoring: matched interests, compatible goals, semantic relevance, and event/group context. Then the student requests an icebreaker. It is generated on demand with the selected target and style, validated, and shown with copy and regenerate actions."

Submit feedback using the persisted recommendation ID.

### 3:45-4:25 | Reliability

"The demo does not depend on one perfect provider response. Invalid or fenced JSON is safely parsed only when it is unambiguous, then validated with Pydantic. Provider failures use deterministic keyword and template fallbacks. The recommendation pipeline also has a deterministic embedding fallback. The user can still get a usable profile, ranking, and icebreaker."

Do not describe fallback as equivalent to the model; describe it as a continuity mechanism.

### 4:25-5:00 | Close

"Aatmoday Connect turns a student's words into a reason to show up and a sentence to say when they arrive. It makes discovery more personal, matching more transparent, and the first connection easier."

## 6. User Journey

`Landing -> Discover -> natural-language input -> structured profile -> ranked recommendations -> group/event detail -> Why this matches -> on-demand icebreaker -> feedback`

The profile is stored in browser session storage for continuity between Discover and Recommendations. Recommendation records and feedback are persisted by the backend.

## 7. Key Features

Implemented:

- Natural-language interest analysis.
- Normalized interests with categories and confidence.
- Goals, traits, and optional preferences.
- Group and event catalog browsing.
- Backend-ranked recommendations with scores from 0-100.
- Matched-interest and matched-goal evidence.
- Group/event detail pages with upcoming events.
- On-demand icebreakers with casual, friendly, and professional styles.
- Copy and regenerate icebreaker actions.
- Recommendation feedback.
- Deterministic AI, embedding, and icebreaker fallbacks.
- Safe validation, rate limits, generic provider errors, and 404/422 handling.

## 8. AI Architecture

1. The frontend sends text to `POST /api/v1/interests/analyze`.
2. `StructuredAIService` calls the configured OpenAI-compatible provider.
3. Analysis requests request JSON output with a bounded output budget.
4. The response parser accepts raw JSON, a complete JSON Markdown fence, or one unambiguous embedded object.
5. `AIInterestAnalysis` validates the payload with Pydantic and rejects missing, wrong-type, extra, malformed, or ambiguous output.
6. Interest aliases are normalized to the controlled vocabulary; categories are derived server-side.
7. Provider, parsing, or validation failure uses `KeywordFallbackAIService`.

The current implementation uses configurable OpenAI-compatible chat and embedding endpoints. The repository does not include a vendor-specific Gemini integration. Do not promise provider availability; describe fallback as the resilience path.

## 9. Recommendation Architecture

The backend pipeline is:

`user interests -> structured analysis -> candidate groups/events -> matching -> ranking -> evidence -> response`

The default hybrid weights are:

- Semantic similarity: 0.50
- Interest overlap: 0.25
- Goal compatibility: 0.15
- Event relevance: 0.10

The score is normalized to 0-100. Missing embeddings do not make a candidate fail; available components are reweighted. At most 100 groups and 100 events are retrieved with deterministic ordering, then the requested limit is returned.

## 10. Explainability Approach

Every recommendation includes:

- persisted recommendation ID,
- backend score,
- matched interests,
- matched goals,
- reasons,
- deterministic explanation.

Explanations are derived from the scoring breakdown. They can mention matched interests, compatible goals, semantic relevance, schedule, and group/event fit. They do not claim unsupported personal attributes or private facts.

## 11. AI Fallback Strategy

Fallback is deliberately narrow and deterministic:

- Interest fallback uses controlled keyword and alias matching.
- Embedding fallback creates a deterministic fixed-size vector.
- Icebreaker fallback uses a real shared interest and target name when available.
- Invalid AI output is rejected rather than trusted.
- API responses expose a safe `source` marker for interest analysis, not provider internals.

Provider HTTP failures are external availability events. They should result in usable fallback behavior, not an architectural change.

## 12. Technology Stack

- Frontend: React, TypeScript, Vite, React Router, TanStack React Query, Tailwind CSS, Framer Motion, Lucide icons.
- Backend: FastAPI, Pydantic, SQLAlchemy, PostgreSQL 16, Alembic, HTTPX.
- AI integration: configurable OpenAI-compatible HTTP chat and embedding providers.
- Testing: Pytest, deterministic provider doubles, SQLite tests, PostgreSQL integration tests.
- Deployment support: Docker Compose for PostgreSQL and backend startup.

## 13. System Architecture

The browser uses a centralized API client and service layer. In API mode, services call the backend and map direct FastAPI response bodies into view models. React Query owns server-state loading and error states.

The backend keeps route handlers thin:

`HTTP route -> request/response schema -> service -> provider/database -> response schema`

The frontend never connects directly to PostgreSQL and does not calculate recommendation scores.

## 14. Database Architecture

PostgreSQL stores users, canonical interests, user-interest weights, groups, events, relationship tables, recommendation records, and feedback. UUIDs identify users and recommendation targets. Foreign keys and check constraints protect ownership, ranges, capacities, and event dates.

Alembic head is `0002_profile_feedback_state`. Seed data is deterministic and idempotent: 34 interests, 20 communities, 40 events, 5 users, and relationship links. Group and event embeddings are optional JSON values with a fixed 1536-dimensional application contract; no database extension is required for the current MVP.

## 15. Future Scope

Not implemented in this demo:

- Real student authentication and authorization.
- Direct chat or messaging.
- Push notifications and event reminders.
- Moderation workflows and reporting.
- Production-grade vector indexing and retrieval at larger scale.
- Admin catalog management.
- Richer feedback analytics and model evaluation dashboards.
- Provider routing, quotas, and observability for production AI operations.

These are future directions, not current capabilities.

## 16. Judge Q&A

**Q: Is the score calculated in the frontend?**  
A: No. The backend matching service calculates the hybrid score and returns it. The frontend renders that value.

**Q: What makes the explanation trustworthy?**  
A: It is generated from the same scoring evidence: normalized matched interests, compatible goals, semantic relevance, and event/group context. It does not invent user attributes.

**Q: What happens if the AI provider is unavailable?**
A: Interest analysis falls back to deterministic keyword matching, embeddings use a deterministic fallback, and icebreakers use a deterministic template based on real shared interests and target data.

**Q: Does every recommendation trigger an AI call?**  
A: No. Recommendations use one analysis request and one embedding request. Explanations are built locally from scoring evidence. Icebreakers are requested only on demand.

**Q: How is malformed model output handled?**  
A: The service accepts only safely extractable JSON, validates it with Pydantic, rejects ambiguity and schema violations, and then uses fallback.

**Q: How do you prevent the model from inventing private facts?**  
A: User text and target context are delimited as untrusted data. Icebreaker instructions prohibit invented experiences and private facts, and the context contains only needed interest and public target fields.

**Q: Why use PostgreSQL if the MVP does not require vector search?**  
A: PostgreSQL provides reliable relational ownership, constraints, and deterministic catalog/recommendation persistence. Embeddings are retained as optional JSON for the current MVP and future indexing.

**Q: How do you know the demo data is repeatable?**  
A: Seed IDs use UUID5 keys and the seed operation is upsert-based, so repeated runs produce the same catalog and relationships.

**Q: What is the main production risk?**  
A: External AI availability and rate limits. The current demo remains usable through deterministic fallback; production would add provider observability, quotas, and stronger operational controls.

**Q: What is not implemented?**  
A: Authentication, chat, notifications, moderation, and production-scale vector retrieval are future scope, not hidden claims in this demo.

## 17. Strong Closing

"Aatmoday Connect does not stop at recommending a place; it explains the fit and gives the student a first sentence, turning interest into participation."
