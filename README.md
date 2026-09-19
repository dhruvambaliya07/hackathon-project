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
- `src/services/api.ts` is the REST-ready service boundary. It currently returns local mock data while the FastAPI backend is being built.
- `src/services/interestService.ts` owns the interest analysis contract, including the current mock implementation and manual fallback. It can later call `POST /api/v1/interests/analyze` without changing the UI.
- `src/hooks` exposes TanStack Query hooks for UI consumption.
- `src/components` contains reusable primitives and feature component locations.
- `src/pages` contains the routed discovery, recommendation, community, event, and profile experiences.

## Routes

`/`, `/discover`, `/recommendations`, `/groups`, `/groups/:id`, `/events`, `/events/:id`, and `/profile` are implemented.

The homepage at `/` includes the complete discovery journey: hero CTAs, an interactive interest preview that routes to `/discover`, value highlights, a three-step explainer, featured communities, upcoming events, and a final discovery CTA.

The `/discover` flow accepts natural-language interests, supports suggested prompts, shows short analysis progress states, and presents an explainable interest profile with scored signals, goals, traits, and a route to personalized matches.
