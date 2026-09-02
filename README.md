# Listas de Compras — Colaborativas + IA

A mobile-first, installable PWA for collaborative shopping lists, built so that
external AI assistants (ChatGPT, Claude, Gemini, ...) can create and modify lists
through the same authorization rules a human user goes through — never more access
than that.

```
                         ┌──────────────┐
                         │    Usuario   │
                         └──────┬───────┘
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
            PWA              ChatGPT             Claude
             │                  │                  │
             │                MCP/API             MCP/API
             │                  │                  │
             └──────────────────┼──────────────────┘
                                │
                      ┌─────────▼─────────┐
                      │ AI Integration    │
                      │      Layer        │
                      └─────────┬─────────┘
                                │
                      ┌─────────▼─────────┐
                      │   Application API │
                      └─────────┬─────────┘
                                │
                  ┌─────────────┼─────────────┐
                  │             │             │
             PostgreSQL       Redis       WebSockets
```

## Stack

- **Frontend** (`apps/web`): Next.js 15 (App Router) + React 18 + TypeScript, Tailwind
  CSS, Framer Motion, TanStack Query, a hand-rolled Service Worker + Web App Manifest
  (PWA), and an IndexedDB-backed offline queue (`idb`).
- **Backend** (`apps/api`): FastAPI + SQLAlchemy 2 (async, `asyncpg`) + Alembic,
  JWT auth, WebSockets, Redis (pub/sub fanout + cache).
- **Database**: PostgreSQL. **Cache/events**: Redis. **Infra**: Docker Compose,
  GitHub Actions CI.

## Running it

```bash
cp apps/api/.env.example apps/api/.env   # edit JWT_SECRET before any real deployment
docker compose up --build
```

- Web: http://localhost:3000
- API: http://localhost:8000 (docs at `/docs`, health at `/health`)

To run things locally without Docker:

```bash
# API
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head          # requires Postgres running (see docker-compose.yml)
uvicorn app.main:app --reload

# Web
cd apps/web
cp .env.example .env.local
npm install
npm run dev
```

### Tests

```bash
docker compose up -d db redis
cd apps/api && DATABASE_URL=postgresql+asyncpg://shopuser:shoppass@localhost:5432/shopdb_test \
  REDIS_URL=redis://localhost:6379/1 pytest -v
```

CI (`.github/workflows/ci.yml`) runs this same suite against real Postgres/Redis
service containers, plus `npm run build` + `next lint` for the frontend.

## What's implemented end-to-end

- **Auth**: register/login/refresh/logout, bcrypt password hashing, short-lived JWT
  access tokens + longer-lived refresh tokens.
- **Lists & items**: full CRUD, categories, quantities/units/notes/estimated price,
  complete/uncomplete with a progress bar, optimistic UI on the client.
- **Authorization, enforced server-side, always**: every list/item operation
  re-derives the caller's role from `shopping_lists.owner_id` and `list_members`
  (`app/services/authz.py`) — a client-supplied `list_id`, `user_id`, or `role` is
  never trusted. A non-member gets a 404, not a 403, so list existence isn't leaked.
- **Sharing & invitations**: owner invites by email + role, invitee sees it under
  "Compartidas conmigo" after accepting; invitations carry status/expiry/sender/
  receiver.
- **Realtime collaboration**: WebSocket per open list (`/ws/lists/{id}`), Redis
  pub/sub fanout so it works across multiple API instances, partial updates only
  (no full-list refetch) for `ITEM_CREATED` / `ITEM_UPDATED` / `ITEM_DELETED` /
  `ITEM_COMPLETED` / `ITEM_UNCOMPLETED` / `MEMBER_ADDED` / `MEMBER_REMOVED`.
- **Notifications**: in-app notification center (unread count, mark read/all-read)
  for invitations, acceptances, and membership changes.
- **Offline + sync**: IndexedDB cache of lists/items for offline viewing, a pending-
  operations queue for offline mutations, automatic flush on reconnect
  (`lib/offlineQueue.ts`, `hooks/useOfflineSync.ts`). Conflict strategy is
  Last-Write-Wins with a `version` counter per row (see section below on where
  this would evolve).
- **PWA**: manifest + icons, custom Service Worker (app-shell caching + offline
  fallback page), install prompt that explains itself before asking
  (`components/InstallBanner.tsx`).
- **AI Integration Layer** (`apps/api/app/ai/`): fully independent of
  `lists_service`/`items_service`/`users_service` — see "AI integration" below.

## AI integration

Nothing in `app/services/lists_service.py`, `items_service.py`, or the user-facing
routes imports anything from `app/ai`. The dependency only goes one direction:
`app/ai/tools/definitions.py` calls the same services a human request would, through
the same `app/services/authz.py` role checks. Adding a new AI provider means adding
one entry to `app/ai/providers/registry.py` — never touching list/item logic.

- **Scoped tokens, not the user's session**: connecting an assistant
  (Perfil → Integraciones) issues a token scoped to exactly the permissions the user
  checked (`lists:read`, `items:create`, etc. — see `app/ai/permissions/scopes.py`).
  The user's own JWT, password hash, or refresh token is never handed to an
  integration. Only the token's SHA-256 hash is stored; the plaintext is returned
  once, at issuance, and never logged or re-returned.
  Destructive scopes (`lists:delete`, `items:delete`) are **off by default** and
  require the user to explicitly check them.
- **MCP-style tool catalog**: `GET /ai/mcp/tools` lists the available tools (name,
  description, JSON schema, required scopes); `POST /ai/mcp/invoke` calls one. A
  REST mirror of the same operations also exists under `/ai/lists`, `/ai/items/...`
  for clients that prefer plain REST over the tool-invocation shape (see
  `app/ai/routes.py`). Both paths funnel through the exact same handlers in
  `app/ai/tools/definitions.py`, so there's exactly one place scope checks and
  audit logging happen.
- **Ambiguity, not guessing**: `shopping.get_lists` accepts a `name` filter; if two
  lists share a name, the response says `ambiguous: true` and lists both, so an
  assistant can ask the user which one instead of picking wrong.
- **Audit trail**: every AI-driven mutation writes an `audit_logs` row (integration/
  provider, action, resource, an `operation_id`, and a result) — visible to the user
  under Activity (`GET /activity`). Metadata is kept to names/ids/counts, not full
  note contents.
- **What's a placeholder today**: `app/ai/oauth/flows.py` documents where a real
  OAuth2 authorization-code flow would plug in once a provider (ChatGPT/Claude/
  Gemini) offers a public "connect a third-party app" flow to build against — none
  currently do, so tokens are issued directly from the Integrations screen instead.

## Data model

See `apps/api/app/models/` and the initial migration
(`apps/api/alembic/versions/0001_initial.py`) for the authoritative schema: `users`,
`shopping_lists`, `shopping_items`, `list_members`, `invitations`, `notifications`,
`device_subscriptions`, `ai_integrations`, `ai_tokens`, `audit_logs` — matching the
product brief's minimum schema.

## Deliberately scaffolded, not fully built out

Given the size of the brief, these are wired into the architecture (so they're a
small addition later, not a rewrite) but not fully fleshed out yet:

- **Presence / "X is viewing this list"**: `app/ws/manager.py` already tracks who's
  connected to each list (`ConnectionManager.presence`); broadcasting that as a
  `PRESENCE_UPDATED` event and rendering it in the UI is the remaining step.
- **Web Push**: `/push/subscribe`, the `device_subscriptions` table, and
  `app/services/push_service.py` (via `pywebpush`) are in place; it no-ops until
  `VAPID_PUBLIC_KEY`/`VAPID_PRIVATE_KEY` are set, and no notification is triggered
  on the invitation/sharing events yet (only the in-app notification is).
  Nice-to-have: budgets, purchase history, barcode scan, recipes, supermarket price
  integrations (product brief section 1's growth list) — the schema (`shopping_items.
  estimated_price`, free-form `category`) doesn't block any of these, but none are
  built.
- **CRDT-based conflict resolution**: today it's Last-Write-Wins keyed on a
  `version` counter (section 23 of the brief calls this out as the deliberate
  starting point). Swapping in a CRDT later touches `items_service.update_item` and
  the client's optimistic-update path — not the schema.
- **A dedicated MCP stdio/SSE transport**: `GET /ai/mcp/tools` / `POST /ai/mcp/invoke`
  are plain HTTP and already carry everything an MCP server needs (tool schemas,
  scopes); wrapping them behind a proper MCP stdio/SSE server is a thin adapter, not
  a redesign.
- **E2E tests**: backend `pytest` (`apps/api/tests/`) covers auth, list/item CRUD,
  cross-user isolation, sharing/invitations, and AI scope enforcement (including
  that a default-connected integration is denied `items:delete`). A full
  register→share→realtime→push→AI-creates-a-list browser E2E run is not yet
  automated.

## Security notes

- Every resource access re-derives ownership/role from the database — never from a
  client-supplied id or role.
- AI tokens are hashed (SHA-256) at rest, scoped, revocable (disconnect revokes
  immediately), and never appear in any response after issuance.
- Rate limiting (`slowapi`) is applied globally and more tightly on
  `/auth/login` and `/auth/register`.
- CORS origins are explicit (`CORS_ORIGINS`), not `*`.
- The current token storage on the client is `localStorage` for simplicity; moving
  to an httpOnly-cookie session before a real production launch is a drop-in swap
  (`apps/web/lib/tokenStore.ts` is the only place that would change).
