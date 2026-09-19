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
- `src/hooks` exposes TanStack Query hooks for UI consumption.
- `src/components` contains reusable primitives and feature component locations.
- `src/pages` contains the routed discovery, recommendation, community, event, and profile experiences.

## Routes

`/`, `/discover`, `/recommendations`, `/groups`, `/groups/:id`, `/events`, `/events/:id`, and `/profile` are implemented.
