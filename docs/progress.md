# Build Progress

## Current status

- **Current phase:** Complete — all seven build-map phases are complete
- **Last updated:** 2026-09-12
- **Application implementation started:** Yes
- **Final phase:** Phase 7 is the final phase in the build map; no further phase is
  planned.

## Phase checklist

- [x] Phase 1 — Foundation and Local Runtime
- [x] Phase 2 — Persistent Household Memory
- [x] Phase 3 — Deterministic Meal Decision Engine
- [x] Phase 4 — Agency, Approvals, and Workflow State
- [x] Phase 5 — Cook Communication, Feedback, and Memory Closure
- [x] Phase 6 — Local Voice and Photo Inventory Input
- [x] Phase 7 — Demo Hardening and End-to-End Validation

## Phase reports

### Phase 1 — Foundation and Local Runtime (complete, 2026-09-12)

**Files added:** FastAPI runtime under `backend/app/`, backend tests, React/Vite
dashboard under `frontend/src/`, project/package configuration, `.env.example`,
local runbook, and Phase 1 architecture documentation.

**Verification:**

- Backend test suite: 6 passed (`.venv/bin/pytest`), including unavailable,
  model-unavailable, and malformed structured-JSON provider cases.
- Frontend smoke test: 1 passed (`cd frontend && npm test`).
- Frontend production build: passed (`cd frontend && npm run build`).
- Runtime smoke: FastAPI started on `127.0.0.1:8000`; `GET /api/health` returned
  SQLite `available` and Ollama `qwen3:4b` `available` after a validated
  structured-JSON response.
- Seed-reset smoke: `POST /api/demo/reset` returned 2 recipes and 3 store items;
  the SQLite database contained exactly those 2 recipe and 3 store fixture rows.
- Dashboard smoke: Vite started on `127.0.0.1:5173` and served the Household Agent
  dashboard shell.

**Acceptance criteria:**

- Backend and frontend start locally: met.
- Qwen3 4B health endpoint confirms model availability: met.
- Seed data loads and resets without manual database edits: met.
- No business decision logic exists: met; Phase 1 contains only runtime health,
  seed fixtures, and a dashboard/reset control.

**Known limitations:** The fixture tables are intentionally not household memory.
There is no household CRUD, meal planning, approvals, scheduler, voice/photo input,
cook messaging, or external commerce behavior.

**Next phase:** Phase 2 — Persistent Household Memory. It depends on this verified
Phase 1 local runtime. A mandatory review stop follows Phase 2.

### Phase 1 smoke-test re-verification (2026-09-12)

- Running FastAPI returned `200` from `GET /api/health`: SQLite and `qwen3:4b`
  were both `available`; the model health check completed a validated JSON response.
- `POST /api/demo/reset` returned the expected 2 recipes and 3 store items, and
  direct SQLite counts matched those values.
- The running Vite server returned the Household Agent dashboard HTML.
- Backend regression suite: 6 passed. No Phase 2 work was started.

### Phase 2 — Persistent Household Memory (complete, 2026-09-12)

**Files changed:** Phase 2 SQLModel entities, repositories, CRUD schemas/routes,
expiry-status service, deterministic household seed fixture, persistence/API tests,
the Household/Inventory/Memory frontend screens and API contracts, and local
architecture/runbook documentation.

**Schema and API:** SQLite now persists households, household members, cook profiles,
inventory lots, leftovers, dishes, dish history, budgets, preference signals, and
passive meal-loop records. Scoped CRUD is available under
`/api/households/{household_id}/…`; the seed-reset response includes the seeded
household ID. Inventory and leftover responses calculate display-only expiry states.

**Verification:**

- Backend test suite: 10 passed (`.venv/bin/pytest`), covering profile/budget
  persistence, inventory quantity/expiry updates, leftover expiry states, seeded
  history/preference retrieval, and file-backed database reopen persistence.
- Frontend rendered smoke test: 1 passed (`cd frontend && npm test`), rendering the
  Inventory page with its expiry state and typed inventory control.
- Frontend production build: passed (`cd frontend && npm run build`).
- Live API smoke: reset produced a seeded household with two members, Hindi cook
  profile, budget, inventory, leftovers, prior meal, and preference signal; a new
  inventory lot transitioned from `expiring_soon` to `fresh` after a typed update;
  a same-day leftover showed `expires_today`.
- Live dashboard shell: Vite served the updated application at `127.0.0.1:5173`.

**Acceptance criteria:**

- Users can create and edit persistent household state: met through scoped CRUD and
  Household/Inventory/Memory controls.
- Inventory and leftovers are visible with expiry status: met.
- Previous meals and feedback are retrievable: met through Memory API and screen.
- Data survives backend restart: met by file-backed reopen test.

**Known limitations:** Phase 2 is a system of record only. It does not select meals,
rank dishes, calculate procurement, authorize actions, schedule work, call an LLM,
capture voice/photos, or message a cook.

**Next phase:** Phase 3 — Deterministic Meal Decision Engine, dependent on this
persistent state. **Mandatory review stop:** do not begin Phase 3 until explicitly
approved by the user.

### Phase 1 + Phase 2 smoke-test re-verification (2026-09-12)

- Automated regression: 10 backend tests passed; rendered frontend UI smoke test
  passed; frontend production build passed.
- Phase 1 live stack: `GET /api/health` confirmed SQLite and local `qwen3:4b`
  structured-JSON availability. `POST /api/demo/reset` restored exactly 2 recipes
  and 3 local store fixtures, confirmed directly in SQLite.
- Phase 2 live stack: the seeded household returned its members, Hindi cook profile,
  budget, meal history, and preference signal. A typed inventory lot was created,
  updated from `expiring_soon` to `fresh`, and deleted; a same-day leftover correctly
  showed `expires_today` and was deleted.
- Vite served the live Household Agent dashboard shell. No errors arose and no Phase
  3 work was added.

### Phase 3 — Deterministic Meal Decision Engine (complete, 2026-09-12)

**Files changed:** deterministic planning domain, planning request schema and API,
expanded seeded recipe fixtures, planner tests, and Today-page proposal cards.

**Verification:** 12 backend tests passed, covering allergy/time exclusions,
deterministic expiry-led scoring, scaled ingredient gaps, substitutions, and seeded
local procurement routing. The rendered frontend smoke test and production build
passed. Live reset-and-plan smoke confirmed identical repeat output, excluded Peanut
Noodles for the seeded peanut allergy, and returned only a simulated local route.

**Acceptance criteria:** met. Recommendations are deterministic, explain score and
gaps, exclude unsafe/infeasible dishes, and select `use_stock`, `manual_purchase`,
or `simulated_order` without external services.

**Known limitations:** Planning creates no task, approval, order, message, or state
transition. It never calls the LLM. Those are later-phase concerns.

**Next phase:** Phase 4 — Agency, Approvals, and Workflow State, dependent on this
planning output. **Mandatory review stop:** do not begin Phase 4 until explicitly
approved by the user.

### Phase 1–3 regression and bug-fix smoke test (2026-09-12)

- Initial full smoke pass: 12 backend tests, the rendered frontend test, production
  build, health/reset, and live planning edge cases passed.
- A code review identified that the planner's inventory expiry filter used the host
  clock instead of the supplied plan-context date. The first fix exposed a missing
  date argument in the gap helper; the new regression test caught it.
- Fixed the helper chain to use the context date throughout. The full backend suite
  now has 13 passing tests, including the deterministic context-date regression, and
  the restarted live planner passed repeatability smoke testing.
- No Phase 4 behavior was added.

### Phase 4 — Agency, Approvals, and Workflow State — IN PROGRESS (2026-09-14)

**Review gate:** Phase 3 mandatory review cleared; Phase 4 authorized.

Implemented and tested:
- Meal-loop transition guard with invalid-transition rejection
- Deterministic green/yellow/red autonomy classifier
- Persistent approval, local-task, and audit-event models
- Loop start and transition APIs with audit entries
- Audit timeline API
- 14 backend tests passing

Still required for full Phase 4 completion:
- Approval decision flow
- Stale-inventory enforcement before green actions
- Local task generation from plans
- Scheduler/timeout behavior (APScheduler)
- Today/Approvals UI controls
- Full acceptance-criteria verification once the above land

**Completion update (2026-09-14):** Added approval decisions, stale-inventory
checks, green local-task generation, APScheduler lifecycle/daily local triggers,
timeout handling, and Today/Approvals controls. Backend: 15 tests passed; frontend
smoke/build passed. Live smoke verified scheduled local trigger, approval decision,
timeout-to-unclosed, and audit events. All Phase 4 acceptance criteria are met:
plans become explicit local tasks or approval requests, decisions are auditable, and
the loop can pause, approve/reject, and recover without hidden external action.

**Mandatory review stop:** Phase 5 is not authorized until explicitly approved.

### Phase 1–4 regression smoke test (2026-09-14)

- Backend: 15 tests passed. Frontend: rendered smoke test and production build passed.
- Restarted live backend verified local model/database health, seeded reset,
  deterministic safe planning, scheduled local trigger, rejected approval flow,
  timeout-to-unclosed, audit visibility, and live dashboard availability.
- No runtime defects were found in this pass. Phase 5 remains untouched.

### Phase 5 — Cook Communication, Feedback, and Memory Closure (complete, 2026-09-14)

- Added validated Qwen structured cook-brief and English/Hindi/Hinglish feedback-parser endpoints with safe manual-entry fallbacks.
- Added deterministic outcome closure: history, preference signals, leftovers, consumed inventory, loop status, audit event, and weekly reflection updates.
- Verification: 17 backend tests passed, frontend smoke/build passed, malformed-model output returned safe `503`, and live closure smoke completed an approved loop and updated reflection.
- No LLM output authorizes spending or changes deterministic policy. At this
  report's time, Phase 6 awaited its mandatory review; later authorization and
  completion are documented below.

### Phase 6 — Local Voice and Photo Inventory Input (complete, 2026-09-12)

- Real local providers verified: `faster-whisper` (`small`) transcribed the AAC
  fixture through the live audio route; `qwen2.5vl:3b` was pulled, directly
  verified on the fridge fixture, then returned editable, confidence-labelled
  candidates through the live photo route. Both routes remain local-only.
- Two full isolated E2E runs proved the mutation boundary. Voice and photo each
  moved inventory `3 → 3 → 3 → 4` for preview, rejected confirmation (`409`),
  and explicit `confirmed: true` respectively. Voice produced an editable
  transcript; when Qwen could not propose inventory items, the UI retained the
  explicit manual typed-confirmation path rather than claiming an extraction.
- Safety validation covers unavailable providers (empty-candidate typed fallback),
  unsupported/corrupt/empty/malformed/oversized inputs (`4xx`), and no mutation
  before confirmation. Audio now rejects obvious non-audio containers before
  invoking Whisper.
- Automated verification: full backend suite passed (23 tests), full frontend
  suite passed (3 tests), and the production build passed. The audio route was
  moved to the async request path after E2E exposed intermittent AAC failure in
  the worker-thread path; the backend suite passed again afterward.

**Acceptance criteria:** met. Typed, voice, and image input work with mandatory
review; uncertain or unavailable extraction never writes state; typed input stays
available; all providers and data handling are local to the laptop.

**Historical review status:** Phase 7 was pending explicit review at this point;
the user later authorized Block 7-A only, documented below.

### Phase 7 — Block 7-A: Demo Reset and Scenario Selector (complete, 2026-09-12)

- `POST /api/demo/reset?scenario=<name>` now routes to deterministic fixtures for
  `default`, `expiry_routine`, `preference_conflict`, `guests`, `cook_mishap`,
  `feedback_learning`, and `budget_constraint`. The response identifies the
  selected scenario; the frontend API client can pass the same parameter.
- Invalid scenario names return `422` before any existing state is deleted or
  replaced. There is no silent fallback to the default fixture.
- Verification: focused backend tests passed (3), and a live API smoke reset every
  scenario twice with identical normalized persisted state. The invalid-scenario
  smoke returned `422` and left the prior fixture unchanged.

**Scope stop:** Block 7-A only. No Phase 7 hardening, UI timeline, Playwright, or
other demo behavior was added.

### Phase 7 — Block 7-B: Six Demo Fixture Scenarios (complete, 2026-09-12)

- Expanded the six named reset fixtures without adding planner, workflow, or
  learning mechanics. Each now makes an existing behavior observable:
  expiry-led carrot scoring; a paneer taste request safely excluded for Asha's
  paneer allergy; a triggered four-guest loop with guest-sized planning and an
  approval path; an active cooking mishap that recovers with stocked khichdi;
  a completed "too heavy" outcome whose learned light-dinner signal adds the
  existing 7-point light-dish bonus; and a ₹90 remaining budget that routes the
  ₹137 paneer basket to manual purchase while retaining the ₹88 dal basket as a
  simulated option.
- Added one reset-and-verify test for every named scenario, alongside the
  existing two-reset normalized-state repeatability check. These tests prove the
  named effect, rather than merely checking that matching fields exist.
- Verification: focused scenario/API suite 28 passed; planner suite 3 passed;
  full backend suite 32 passed; frontend suite 3 passed; frontend production
  build passed. An isolated live FastAPI smoke reset all six selectors cleanly,
  then confirmed the expiry and budget planning outputs through the HTTP API.

**Scope stop:** Block 7-B only. No new automatic preference-conflict resolution,
guest-to-plan binding, recovery selection, or budget-ranking policy was added;
the fixtures deliberately expose the Phase 1–6 mechanics already implemented.

### Phase 7 — Block 7-C: Visible Agent Timeline and Decision Explanations (complete, 2026-09-12)

- The Today screen now has a scenario selector plus an agent timeline rendered
  directly from existing meal-loop, audit-event, and approval records. It shows
  the trigger, ordered state events, current loop state, and the existing green,
  yellow, or red autonomy tier where the persisted audit/approval data provides
  one. No audit fields or workflow rules were added.
- Decision cards now surface the returned deterministic plan fields verbatim:
  score, expiry and leftover use, novelty status, gap count and quantities,
  substitution, route, price, procurement rationale, and exclusions. Feedback
  history and preference signals appear with completed/recovered loop timelines
  as a clearly labelled current memory snapshot; no unrecorded event is inferred.
- Each named fixture now contains existing-model audit records appropriate to its
  staged state, allowing the UI to display an actual persisted sequence. The
  feedback fixture additionally shows its persisted "Too heavy" meal record and
  learned light-dinner signal with the completed loop.
- Verification: backend audit-sequence fixture test and full backend suite passed
  (33 tests); frontend renders all six selected scenario timelines in event order
  and checks approval color/memory output (10 tests); frontend production build
  passed. Isolated live HTTP smoke of expiry reset returned the four-event audit
  sequence and the matching raw plan explanation for Vegetable Khichdi.

**Scope stop:** Block 7-C only. No planning, approval, audit, workflow, or memory
mechanics were changed; the UI reports persisted state and deterministic output.

### Batch A — Real Voice Provider, Step 4 (verified, 2026-09-12)

- Repaired the local Whisper provider's handling of the supplied AAC fixture: when direct decoding fails on its isolated malformed packet, it locally decodes the valid frames to temporary PCM and retries the same `small` Whisper model. No network or typed fallback is used for that recovery.
- Live route smoke: `POST /api/households/1/capture/audio` uploaded `backend/tests/fixtures/audi_test.aac` with `HOUSEHOLD_WHISPER_MODEL=small`. It returned a Hindi transcript, `source: audio`, `requires_confirmation: true`, and `fallback: null`; inventory was unchanged at 3 lots before and after.
- The transcript is exposed through the UI's editable transcript review field. A separate warning may report unavailable inventory candidates from Qwen parsing; it is not a Whisper or typed-entry fallback.
- Regression verification: 21 backend tests passed; 2 frontend tests and the production build passed.

**Historical sub-step status:** Phase 6 was not complete at this point; later
blocks completed it. Phase 7 remains gated by the final Phase 6 review.

### Batch B — Real Vision Provider, Step 7 (verified, 2026-09-12)

- Connected the existing image capture route to the verified local `qwen2.5vl:3b` service with a vision-specific 60-second timeout. The provider now sends a constrained JSON Schema request (at most four observed items), preserving model-returned readability confidence rather than generating it in application code.
- Live route smoke: `POST /api/households/1/capture/image` uploaded `backend/tests/fixtures/fridge_pic.webp` and returned Qwen candidates for bananas, oranges, apples, and kiwi with `fallback: null` and `requires_confirmation: true`. Inventory remained at 3 lots before and after analysis.
- The preview is rendered as editable per-candidate fields with confidence labels. A live unconfirmed capture returned `409` and kept inventory unchanged; only the existing explicit confirmation endpoint can create inventory.
- Regression verification: 21 backend tests passed; 2 frontend tests and the production build passed.

**Historical sub-step status:** Phase 6 remained in progress at this point;
later blocks completed it. Phase 7 remains gated by the final Phase 6 review.

### Batch C — Confirmation Safety and Bad Inputs, Step 8 (verified, 2026-09-12)

- Live confirmation-gate smoke used an actual image-preview candidate (bananas, quantity 3, from `fridge_pic.webp`) and submitted it to the shared confirmation endpoint with `confirmed: false`.
- The API returned `409 Capture requires explicit confirmation`. Direct SQLite snapshots before and after were byte-for-byte equivalent at the row level: the same three inventory lots, IDs, quantities, units, expiry dates, locations, and confirmation flags.
- The confirmation endpoint is source-agnostic; both voice and image previews use the same mutation boundary and payload, so this verifies the single place an unconfirmed capture could create a lot.

**Historical sub-step status:** Phase 6 remained in progress at this point;
later blocks completed it. Phase 7 remains gated by the final Phase 6 review.

### Block 6-A — Real Voice, Step 4 re-verification (2026-09-12)

- Verified the actual local `faster-whisper` provider against
  `backend/tests/fixtures/audi_test.aac` using the cached `small` checkpoint. Its
  deterministic fixture output was the Hindi transcript
  `तोमेंटो पनीर भी आप दाल है, भी नीट पनीर एनाफ फर फोर पुपिपल.` with language
  `hi`.
- Ran an isolated local FastAPI instance configured with
  `HOUSEHOLD_WHISPER_MODEL=small`, then posted that same AAC file to the real
  `/api/households/{id}/capture/audio` endpoint—no provider or route mock. The
  response returned that transcript, `source: audio`, `requires_confirmation:
  true`, and `fallback: null`; inventory remained at 3 rows before and after.
- Added frontend coverage that an audio preview exposes the transcript in the
  editable review field before any confirmation. It does not create inventory.
- Regression verification: 21 backend tests passed; 3 frontend tests and the
  production build passed.

**Scope stop:** this verification changes only the real voice upload path and its
review coverage. No vision behavior was changed.

### Block 6-B — Real Vision Provider, Steps 5–6 (verified, 2026-09-12)

- Ran `ollama pull qwen2.5vl:3b`; `ollama list` confirms the local 3.2 GB model
  is present (`fb90415cde1e`).
- Independently sent `backend/tests/fixtures/fridge_pic.webp` directly to
  `http://127.0.0.1:11434/api/generate` with the image supplied as an Ollama
  vision input and a bounded JSON response schema. This bypassed all application
  provider, upload-route, database, and UI code.
- Raw model detection: `bananas`, `oranges`, `apples`, `kiwi`, `lemons`, and
  `eggs`. Manual fixture inspection confirms bananas are clearly visible and are
  the dominant lower-shelf item, satisfying the direct-model smoke gate.

**Scope stop:** Qwen2.5-VL is installed and independently verified only. No
application code or image upload-route integration was changed.

### Block 6-C — Real Vision, Step 7 (verified, 2026-09-12)

- Connected the real local Qwen2.5-VL preview to the existing
  `/api/households/{id}/capture/image` route with a six-item response limit and
  sufficient output allowance for the full structured preview.
- Live fixture upload returned six editable candidates—bananas, oranges, apples,
  kiwi, eggs, and peaches—with confidence values `0.85`, `0.9`, `0.8`, `0.7`,
  `0.9`, and `0.8`. The dominant and core isolated detections (bananas, oranges,
  apples, kiwi, and eggs) match Block 6-B. The sixth fruit label varied between
  plausible `lemons` and `peaches` across the two constrained prompts, so the
  route preserves Qwen's actual result rather than normalizing it.
- The review UI renders every detected field as an editable input alongside its
  `readability confidence` label; frontend coverage verifies both the label and
  editable field. The route response required confirmation and inventory stayed
  at 3 rows before and after the upload.
- Regression verification: 21 backend tests passed; 3 frontend tests and the
  production build passed.

**Scope stop:** this block connects and verifies the real photo preview only. No
bad-input or confirmation-safety work was added.

### Block 6-D — Confirmation Safety and Bad Inputs, Steps 8–11 (verified, 2026-09-12)

- Tightened the audio route to reject obvious non-audio payloads before invoking
  Whisper. Recognized local containers/frame headers are WebM, Ogg, WAV, ID3,
  and AAC/MP3; this preserves valid AAC fixture handling while malformed bytes
  now receive a clean `422` rather than a provider fallback.
- Added focused automated tests for: rejected confirmation with unchanged
  inventory, confirmed capture committing the expected row, each unavailable
  provider returning an empty-candidate typed-entry fallback, and unsupported,
  corrupt, empty, malformed, and oversized uploads returning `4xx` without a
  mutation. Focused result: 5 passed (14 deselected); the full suite was not run
  by this block's scope.
- Manual isolated SQLite smoke: inventory was 3 rows before, 3 after a
  `confirmed: false` request (`409`), and 4 after `confirmed: true`. The new
  row contained `manual-confirm-smoke`, quantity `1`, unit `piece`, location
  `fridge`, and `confirmed=1`.

**Scope stop:** confirmation and bad-input safety are verified. No work beyond
Steps 8–11 or full-suite execution was started.

### Block 6-E — Automated Suites, Steps 12–14 (verified, 2026-09-12)

- Full backend suite: passed (23 tests). The first full run exposed an existing
  mocked WebM upload that used placeholder bytes; it was updated with a minimal
  WebM header so it remains a valid declared container under Block 6-D's input
  validation. The rerun passed in full.
- Full frontend suite: passed (3 tests).
- Frontend production build: passed (`tsc -b && vite build`).

**Scope stop:** all automated gates are green. No end-to-end work was started.

### Phase 7 — Demo Hardening and End-to-End Validation (complete, 2026-09-12)

**Implemented:** Blocks 7-A through 7-F added deterministic reset fixtures and the
dashboard scenario selector; persisted agent timelines, decision explanations,
approval state, and memory snapshots; the six documented demo walkthroughs;
explicit Ollama/Whisper/vision/scheduler failure states; local-only Whisper startup
defaults; Playwright UI coverage; restart-persistence coverage; and the local
runbook and architecture documentation. No Phase 1–6 product behavior or external
rail was added.

**Verification:**

- Current cold-start smoke used the documented backend command
  `.venv/bin/uvicorn app.main:app --app-dir backend --reload` and frontend command
  `cd frontend && npm run dev`. They started without dependency installation,
  migrations, or model/cache-warm messages. `GET /api/health` returned database,
  Ollama `qwen3:4b`, and scheduler `available`; the dashboard returned HTTP 200.
- Current regressions passed: backend pytest **35 passed** (3 deprecation
  warnings), frontend production build passed, frontend unit suite **12 passed**,
  and Playwright **8 passed**. The browser suite exercises each of the six named
  fixtures, visible provider/scheduler fallbacks, and a backend restart against the
  same isolated SQLite file.
- Repeatability is covered by the named-scenario reset test, which resets every
  fixture twice and compares normalized persisted state. The focused final audit
  tests for repeatability, audit sequences, default offline mode, local-cache-only
  Whisper loading, and unavailable-provider typed fallbacks all passed (**5
  passed**).
- Network isolation is the default: `.env.example` documents
  `HF_HUB_OFFLINE=1`; application startup applies it before optional Whisper
  imports; and a process started with `HF_HUB_OFFLINE` explicitly absent reported
  `1` after importing `app.main`. Whisper also passes `local_files_only=True`.
  Block 7-D additionally traced an environment-scrubbed FastAPI process while it
  served health, reset, audio, and image requests: its only AF_INET connection was
  the local Ollama address `127.0.0.1:11434`, with no external connection.

**Acceptance criteria:**

- A judge can run the project locally and see the complete agent loop: met. The
  verified cold start, runtime health card, deterministic proposal, persisted audit
  timeline, approval state, outcome memory, and local runbook make the full loop
  inspectable on the laptop.
- Each demo scenario is reproducible from a clean reset: met. All six selector
  fixtures have repeatability tests and passing Playwright UI flows.
- All tests pass and unavailable external rails are visibly absent rather than
  implied: met. The current full suites pass; simulated/manual procurement is
  labelled as such, and browser/UI tests show explicit Ollama, Whisper, vision, and
  scheduler fallback details with typed inventory still available.
- The system recovers gracefully when optional voice/vision providers fail: met.
  Provider tests return typed-entry fallbacks without candidates or inventory
  mutation, and the UI/browser tests make those fallbacks visible.

**Known limitations:** Voice transcription and the subsequent local language-model
parse are separate steps. A successful Whisper transcript can still have no
inventory candidates if the local Qwen parser is unavailable or rejects its output;
the route preserves the editable transcript, returns an explicit warning, and keeps
typed confirmation available. This is an accepted, documented graceful-degradation
path, not a silent extraction failure. Voice, vision, and Ollama remain optional
local services; there are no external ordering, payment, messaging, AWS, or
deployment integrations.

**Final phase:** Phase 7 is the final phase specified by `docs/build_map.md`.
The build-map implementation is complete; no Phase 8 or excluded-scope work was
started.
