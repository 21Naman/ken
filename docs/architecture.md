# Household Agent architecture

Household Agent is a laptop-local, full-stack prototype for the meal loop:

```text
Trigger → read household state → deterministic plan → procurement/approval
→ cook communication → outcome/feedback → durable memory → next plan
```

It has no cloud deployment, external checkout, payment rail, messaging channel, or
production authentication. A procurement result is either an in-stock choice, a
manual-purchase task, or a simulated local-store order.

## Runtime topology

```text
Browser
  React + Vite dashboard (localhost:5173)
             │ HTTP /api
             ▼
  FastAPI + Uvicorn (localhost:8000)
    ├── SQLite / SQLModel (data/household.db)
    ├── APScheduler (local daily reminder / local task only)
    └── Ollama (127.0.0.1:11434)
          ├── qwen3:4b: constrained language tasks
          └── qwen2.5vl:3b: optional photo inventory proposals

  Optional local faster-whisper: voice transcription
```

The FastAPI lifespan initializes the SQLite schema and starts the scheduler. The
health endpoint reports database, Ollama, and scheduler status independently, so a
missing optional provider is visible rather than silently treated as healthy.

## Persistent household memory

SQLite is the system of record. SQLModel tables persist households and members,
cook profiles, inventory lots, leftovers, dishes, dish history, budgets,
preference signals, meal-loop records, audit events, local tasks, approvals, and
seeded store items. Inventory and leftovers expose deterministic expiry display
states (`expired`, `expires_today`, `expiring_soon`, `fresh`, or `unknown`).

`data/*.db` is gitignored. `POST /api/demo/reset?scenario=…` clears and rebuilds
the selected deterministic fixture; it is the repeatable way to obtain demo data.
The React scenario selector calls that endpoint and then reloads all current
household state.

## Deterministic decision and workflow authority

The backend planner builds its input from durable inventory, expiry dates,
leftovers, household allergies and dietary preferences, cook skill, meal history,
preference signals, budget remainder, and seeded store prices. Python—not an
LLM—filters unsafe/infeasible dishes, calculates gaps and substitutions, ranks
recommendations, and selects a local procurement route. The UI displays the score
factors, exclusions, ingredient gaps, route, and rationale.

Meal loops use explicit persisted states:

```text
triggered → planned → awaiting_approval / approved → cook_briefed → cooking
                                                        ├→ completed
                                                        ├→ recovered → cooking
                                                        └→ unclosed
```

The autonomy policy is also deterministic. Fresh, routine, zero-cost local work
can create a green local task; spending variance, unusual actions, or stale
inventory produce a yellow or red approval request. Approval decisions, local
tasks, and all state transitions write audit events. Scheduler work only creates a
local planning reminder and task.

Capturing an outcome records meal history, feedback/preference signals, leftovers,
consumed inventory, and completed/recovered state. The next planning request reads
those records, which is how the feedback-learning scenario changes a later
recommendation.

## Local models and trust boundaries

`qwen3:4b` is limited to unstructured language operations: structured cook briefs
in the cook's language and structured English/Hindi/Hinglish feedback parsing. Its
responses are validated before use; they cannot authorize spend, select an
autonomy tier, mutate inventory, or determine a workflow transition.

Optional `faster-whisper` transcribes audio locally. Optional `qwen2.5vl:3b`, via
the local Ollama API, proposes fields from a fridge/pantry image using a constrained
JSON schema. Both produce a review preview. Neither voice transcripts nor vision
candidates can change inventory until the user submits `confirmed: true` to the
shared confirmation endpoint. Typed entry remains a direct, available fallback.

The application is local-only by default. `.env.example` documents
`HF_HUB_OFFLINE=1`, and application startup sets it with `setdefault` before
optional faster-whisper imports. A cache miss therefore becomes a local typed
fallback instead of a Hugging Face Hub request. Ollama traffic is directed at
`127.0.0.1:11434`.

## Frontend and API surfaces

The single React application exposes five views: Today, Household, Inventory,
Memory, and Approvals. Today combines runtime health, deterministic plan details,
and the persisted agent timeline. Inventory offers typed entry plus review-first
voice/photo capture. Memory displays dish history, preference signals, and a local
reflection. Approvals displays pending yellow/red decisions and local scheduler
trigger control.

FastAPI routes under `/api` provide the corresponding household CRUD, inventory,
planning, workflow, approvals, outcome, local-model, capture, health, and demo-reset
operations. The frontend contracts mirror these JSON responses. CORS permits the
local Vite origin only.

## Verification and demo hardening

Backend pytest covers persistence, deterministic planning, approval/workflow,
closure, and capture safety. Frontend unit tests cover dashboard and capture
fallback rendering. Playwright drives each deterministic fixture through the real
selector and UI, checks the named scenario behavior, shows provider/scheduler
fallback states, and restarts an isolated backend against the same SQLite file to
prove persistence. See [demo-scenarios.md](demo-scenarios.md) for the six demo
walkthroughs.
