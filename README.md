# Aatmoday Connect

A polished React + TypeScript frontend for discovering Aatmoday hobby communities and events from free-form interests.

## Run locally

```bash
cd frontend
npm install
npm run dev
```

Create a production build with `npm run build`.

## Frontend structure

- `src/types` contains the shared domain contracts.
- `src/services/apiClient.ts` is the centralized, typed REST client with JSON parsing, timeout handling, and consistent API errors. It reads `VITE_API_BASE_URL`.
- `src/services/interestService.ts` owns the interest analysis contract, including the current mock implementation and manual fallback. It can later call `POST /api/v1/interests/analyze` without changing the UI.
- `src/services/recommendationService.ts` owns recommendation retrieval, profile data, and local saved/interested state. It is prepared for `POST /api/v1/recommendations`.
- `src/services/groupService.ts` owns community retrieval and local saved/interested state. It is the backend-ready boundary for the community directory and group detail actions.
- `src/services/eventService.ts` owns event retrieval, local interested state, and client-side `.ics` calendar downloads. It is the backend-ready boundary for event discovery and detail actions.
- `src/services/icebreakerService.ts` owns contextual conversation-starter generation and is prepared for `POST /api/v1/icebreakers`.
- `src/services/profileService.ts` owns the shared interest profile and local interest persistence. Updating interests refreshes the recommendation profile and feed queries.
- `src/services/feedbackService.ts` provides typed local feedback persistence until a confirmed backend feedback endpoint is available.
- `src/hooks` exposes TanStack Query hooks for UI consumption.
- `src/components` contains reusable primitives and feature component locations.
- `src/pages` contains the routed discovery, recommendation, community, event, and profile experiences.

## Routes

`/`, `/discover`, `/recommendations`, `/groups`, `/groups/:id`, `/events`, `/events/:id`, and `/profile` are implemented.

The homepage at `/` includes the complete discovery journey: hero CTAs, an interactive interest preview that routes to `/discover`, value highlights, a three-step explainer, featured communities, upcoming events, and a final discovery CTA.

The `/discover` flow accepts natural-language interests, supports suggested prompts, shows short analysis progress states, and presents an explainable interest profile with scored signals, goals, traits, and a route to personalized matches.

The `/recommendations` page presents explainable community and event matches, profile relevance bars, match reasons, filters, sorting, skeleton loading, recoverable errors, empty states, and locally persisted save/interested actions.

The `/groups` directory supports client-side search plus category, interest, and popularity filters. `/groups/:id` includes community context, personalized match evidence, activities, group events, and locally persisted interested/save actions with confirmation feedback.

The `/events` directory supports search plus date, category, community, and location filters. `/events/:id` includes event details, matched interests, reasons to attend, community information, related events, local interested state, and an `.ics` Add to Calendar download.

Icebreakers can be launched from group details, event details, and recommendation cards. The responsive dialog supports casual, friendly, and professional styles, short generation loading, regeneration, copy confirmation, keyboard Escape handling, and a mobile bottom-sheet layout.

The `/profile` page shows interest strengths, goals, traits, saved communities, interested events, activity, and recent recommendations. Its edit mode adds/removes interests through `profileService`, allowing recommendation relevance and match chips to change from the same client-side profile state.

## Backend integration status

This checkout currently contains no FastAPI application, OpenAPI document, routes, or Pydantic schemas to inspect. Because no endpoint could be confirmed, the feature services keep their mock implementations isolated and do not make speculative network requests. Set `VITE_API_BASE_URL` when the backend is added, then map confirmed schemas in the service modules before enabling calls.
