# PROJECT GOAL

Build a local-first household-orchestration agent that completes this durable loop:

`Trigger → understand state → select meal → identify/source gaps → brief cook → capture outcome → update memory → improve next decision`

The prototype runs entirely on the laptop with Python 3.12, FastAPI, Ollama/Qwen3 4B, SQLite/SQLModel, React/Vite/TypeScript, faster-whisper, APScheduler, pytest, and Playwright.

The LLM is restricted to unstructured language: English/Hindi/Hinglish input parsing, preference-conflict explanations, feedback parsing, and cook-ready messages. Deterministic Python handles inventory, expiry, nutrition, ranking, procurement, budgets, approvals, and state transitions.

AWS, external rails, WhatsApp, real payments, real ordering, and real quick-commerce checkout are out of scope. Procurement is represented by local seeded store data, manual-purchase tasks, simulated orders, and approval records.

# PHASES

## Phase 1 — Foundation and Local Runtime

**Goal:** Establish a minimal, runnable full-stack shell with a verified local model connection.

**Features to implement:**

- FastAPI backend, React/Vite frontend, shared API contract, environment configuration, and local developer commands.
- SQLite/SQLModel connection and database lifecycle.
- Ollama provider health check for `qwen3:4b`; validate structured JSON output.
- Basic dashboard shell, API health display, and seeded demo reset endpoint.
- Initial recipe and local-store seed fixtures.

**Components/files involved:**

- `backend/app/main.py`, settings, database session, Ollama provider, health routes.
- `frontend/src/` application shell, API client, dashboard route.
- Project configuration, test configuration, seed fixtures, architecture documentation.

**Dependencies:** None.

**Tests required:**

- Backend startup and database connection.
- Ollama unavailable/model unavailable/invalid JSON handling.
- API health endpoint.
- Frontend smoke test and seeded reset smoke test.

**Acceptance criteria:**

- Backend and frontend start locally.
- Qwen3 4B health endpoint confirms model availability.
- Seed data can be loaded and reset without manual database edits.
- No business decision logic exists yet.

**Definition of Done:** A developer can start the local stack, view a dashboard, verify Ollama, and reset a clean seeded demo state.

**Do not implement yet:**

- Household CRUD beyond seed data.
- Meal planning, approvals, scheduling, voice, photos, or cook messages.

**Token estimate:** Planning 1,500 · Implementation 5,000 · Testing/debugging 2,000 · **Total 8,500**

**Codex instruction:** Inspect the empty repository and existing runtime first; create only the shared local foundation, test it, report the runnable commands and changed files, then stop.

---

## Phase 2 — Persistent Household Memory

**Goal:** Create the household system of record that prevents every meal decision from starting from zero.

**Features to implement:**

- SQLModel entities and repositories for household members, cook profile, inventory lots, leftovers, dishes, dish history, budgets, preference signals, and meal-loop records.
- Typed inventory entry with quantity, unit, expiry, storage location, and confirmation status.
- Household, inventory, and memory screens with CRUD operations.
- Expiry and leftover status calculation.
- Seeded household: English/Hindi preferences, allergies, cook capability, budget, inventory, leftovers, and prior meals.

**Components/files involved:**

- `backend/app/models/`, migrations/schema initialization, repositories, inventory and household services.
- Household, inventory, and memory frontend pages.
- Domain fixtures and persistence tests.

**Dependencies:** Phase 1.

**Tests required:**

- Entity validation and persistence across restart.
- Inventory quantity/expiry updates.
- Leftover expiry behavior.
- Allergy, dietary, and cook-capability profile persistence.
- CRUD API and UI smoke tests.

**Acceptance criteria:**

- The user can create and edit a household’s persistent state.
- Inventory and leftovers are visible with expiry status.
- Previous meals and feedback are retrievable for future decisions.
- Data survives backend restart.

**Definition of Done:** A seeded or manually configured household contains all state required to make a later meal decision.

**Do not implement yet:**

- Automated meal selection.
- LLM-driven extraction.
- Procurement, approvals, scheduler, voice, or image capture.

**Token estimate:** Planning 1,500 · Implementation 6,000 · Testing/debugging 2,000 · **Total 9,500**

**Codex instruction:** Preserve the Phase 1 runtime; add only durable household state and CRUD, write persistence tests, smoke-test each page, report the schema and API changes, then stop.

---

## Phase 3 — Deterministic Meal Decision Engine

**Goal:** Produce transparent, safe, explainable meal recommendations from household memory.

**Features to implement:**

- `MealContext` built from day/time, guests, cook availability, budget, leftovers, urgency, and current inventory.
- Recipe eligibility filters for allergy, diet, nutrition, cook skill, available time, and portions.
- Deterministic dish scoring for expiry use, leftover use, novelty, preference fit, nutrition, time, budget, and cook capability.
- Top 2–3 recommendations with score explanations and exclusion reasons.
- Ingredient-gap calculation, substitutions, and servings scaling.
- Local procurement comparison using seeded store price/availability/ETA data.
- Budget-aware route selection: use stock, manual purchase, simulated order, or alternate dish.

**Components/files involved:**

- `backend/app/domain/` scoring policies, recipe rules, gap calculator, procurement policy.
- Meal planning service and planning API.
- Today page recommendation cards and score/explanation views.
- Recipe, store, and scenario fixtures.

**Dependencies:** Phase 2.

**Tests required:**

- Allergy exclusion and dietary compliance.
- Expiring ingredients increase ranking only when safe.
- Recent dishes receive repetition penalties.
- Cook/time/budget constraints reject infeasible dishes.
- Ingredient-gap, substitution, quantity scaling, and procurement comparison tests.
- End-to-end seeded “expiry-led routine dinner” scenario.

**Acceptance criteria:**

- Given the same stored state, planning produces the same deterministic recommendation.
- Every recommendation explains its score and missing ingredients.
- No unsafe or infeasible dish is recommended.
- The system can choose a manual-purchase or simulated-order path without external services.

**Definition of Done:** The dashboard can turn real stored household state into a complete, transparent meal-and-procurement proposal.

**Do not implement yet:**

- Autonomous action, approval tiers, cook messaging, feedback parsing, voice, image input, or scheduled triggers.

**Token estimate:** Planning 2,000 · Implementation 7,000 · Testing/debugging 3,000 · **Total 12,000**

**Codex instruction:** Inspect Phase 2 models and fixtures before coding; implement deterministic planning only—do not call the LLM for math or ranking—test all constraints and scenario outputs, report decisions and test results, then stop.

---

## Phase 4 — Agency, Approvals, and Workflow State

**Goal:** Turn recommendations into a controlled agent loop that chooses actions, waits for approval when needed, and records every transition.

**Features to implement:**

- Meal-loop state machine: triggered, planned, awaiting approval, approved, cook briefed, cooking, completed, unclosed, recovered.
- Trigger types: manual, scheduled, guest arrival, low stock, and cooking mishap.
- Green/yellow/red deterministic autonomy classifier.
- Approval queue and action audit trail.
- Stale-inventory check before any green action.
- APScheduler daily trigger and loop timeout; scheduled actions create local tasks only.
- Manual shopping and simulated order task generation.

**Components/files involved:**

- Agent orchestrator, policy engine, state-transition service, APScheduler integration.
- Approval/task/audit models and API routes.
- Today and Approvals page workflow controls.
- State-machine and scheduler tests.

**Dependencies:** Phase 3.

**Tests required:**

- Valid and invalid meal-loop transitions.
- Green action requires fresh inventory and configured consent.
- Yellow/red actions cannot advance without approval.
- Rejected approval returns to replanning or manual fallback.
- Timeout marks a loop unclosed without altering inventory.
- Scheduler-triggered loop creation.

**Acceptance criteria:**

- A plan becomes an explicit task or approval request, never a hidden external action.
- Every meaningful agent decision is visible in an audit timeline.
- The agent can safely pause, resume, reject, and recover within the same meal loop.

**Definition of Done:** The product demonstrates agency through controlled action selection and stateful progress, not merely through recommendations.

**Do not implement yet:**

- LLM cook dialogue, feedback learning, speech recognition, photo ingestion, or external integrations.

**Token estimate:** Planning 1,500 · Implementation 6,000 · Testing/debugging 2,500 · **Total 10,000**

**Codex instruction:** Reuse the Phase 3 planning output; add only explicit workflow transitions, local tasks, approvals, and scheduler behavior; prove forbidden transitions in tests, report the audit flow, then stop.

---

## Phase 5 — Cook Communication, Feedback, and Memory Closure

**Goal:** Close the daily loop so the next decision is improved by what actually happened.

**Features to implement:**

- Qwen3-backed structured parser for typed English/Hindi/Hinglish feedback and ad hoc status input.
- LLM-generated short cook brief in the cook’s configured language/register.
- Cook confirmation, rejection, substitution, and mishap reporting.
- Eater feedback capture: rating, “not again,” “too heavy,” preference change, and contextual feedback.
- Deterministic updates to dish history, preference signals, leftovers, consumed inventory, budget status, and loop completion.
- Weekly reflection summary from auditable structured state.

**Components/files involved:**

- Ollama prompt/response schemas and validation.
- Cook-brief, feedback-parser, and loop-closure services.
- Cook status and feedback UI controls.
- Memory update policies and weekly reflection page.

**Dependencies:** Phase 4.

**Tests required:**

- Mocked structured LLM responses are validated before persistence.
- Invalid/malformed LLM output fails safely and requests manual input.
- Cook confirmation closes a loop only after outcome data is captured.
- Feedback affects a later recommendation but one-off context does not overwrite long-term preferences.
- Guest, cook rejection, and mid-cook mishap recovery scenarios.

**Acceptance criteria:**

- The system can brief a cook in English/Hindi/Hinglish.
- A completed meal changes inventory, history, feedback memory, and future ranking.
- A mishap creates a fast in-stock fallback instead of restarting the product flow.
- LLM output cannot directly authorize spending or modify deterministic policy.

**Definition of Done:** A full text-based meal loop works from trigger through outcome and makes tomorrow’s plan measurably different.

**Do not implement yet:**

- Voice transcription, fridge-photo extraction, real messaging channels, or real procurement/payment actions.

**Token estimate:** Planning 1,500 · Implementation 6,000 · Testing/debugging 2,500 · **Total 10,000**

**Codex instruction:** Build on the existing state machine; limit Qwen usage to validated language tasks, retain deterministic authority for all decisions, test malformed-model and recovery cases, report memory changes, then stop.

---

## Phase 6 — Local Voice and Photo Inventory Input

**Goal:** Add low-friction local multimodal input without weakening the typed-input fallback.

**Features to implement:**

- faster-whisper audio upload/transcription pipeline for English, Hindi, and Hinglish voice notes.
- Transcript preview/edit/confirm flow before state changes.
- Upgrade Ollama when required and add Qwen2.5-VL 3B only for fridge-photo extraction.
- Photo extraction schema for ingredient, estimated quantity, expiry/readability confidence, and storage hint.
- User-confirmation workflow for every uncertain image or transcript field.
- Confidence-based fallback to typed inventory entry.

**Components/files involved:**

- Whisper provider, audio upload API, transcription service.
- Vision provider, image upload API, extraction service.
- Inventory capture UI and confirmation dialogs.
- Fixture audio/images and provider contract tests.

**Dependencies:** Phase 5.

**Tests required:**

- English and Hindi transcript fixtures.
- Code-mixed input parsing and manual correction.
- Unsupported/corrupt audio/image handling.
- Low-confidence extraction always requires review.
- Confirmed multimodal input produces the same inventory state as typed input.
- Browser upload and confirmation smoke tests.

**Acceptance criteria:**

- A user can add inventory through typed, voice, or image input.
- The application never silently trusts uncertain extraction.
- Text input remains fully usable if Whisper or the vision model is unavailable.
- Multimodal data remains local to the laptop.

**Definition of Done:** The primary demo can show voice/photo capture with safe confirmation, while retaining a dependable text-only path.

**Do not implement yet:**

- Ambient always-listening audio.
- External voice/vision rails.
- Background photo processing without user consent.

**Token estimate:** Planning 1,500 · Implementation 5,500 · Testing/debugging 3,000 · **Total 10,000**

**Codex instruction:** Inspect existing typed capture before adding providers; implement one local multimodal path at a time with mandatory confirmation and fallbacks, run fixture and browser tests, report model/runtime requirements, then stop.

---

## Phase 7 — Demo Hardening and End-to-End Validation

**Goal:** Produce a reliable local demonstration of the full household-orchestration loop.

**Features to implement:**

- Deterministic demo reset and scenario selector.
- Visible agent timeline, decision explanations, approval state, and memory changes.
- Complete demo fixtures for expiry, preference conflict, guests, mishap recovery, feedback learning, and budget constraint.
- Error states for Ollama, Whisper, vision, and scheduler unavailability.
- Playwright end-to-end suite and concise local runbook.

**Components/files involved:**

- Demo seed/reset service, scenario fixtures, audit timeline UI.
- Playwright scenarios, pytest integration suite, smoke-test scripts.
- `docs/demo-scenarios.md`, `docs/architecture.md`, local setup/runbook.

**Dependencies:** Phases 1–6.

**Tests required:**

- Full end-to-end flows for all six required demo scenarios.
- Restart persistence.
- Local-only network/offline behavior except local Ollama access.
- Failure-mode tests for unavailable providers and malformed inputs.
- Regression suite for planning, approval, and closure behavior.

**Acceptance criteria:**

- A judge can run the project locally and see the complete agent loop.
- Each demo scenario is reproducible from a clean reset.
- All tests pass and all unavailable external rails are visibly absent rather than implied.
- The system recovers gracefully when optional voice/vision providers fail.

**Definition of Done:** The prototype is demo-ready, repeatable, fully local, and proves agentic orchestration rather than recipe recommendation.

**Do not implement yet:**

- Deployment, AWS, multi-user production auth, external rails, real commerce, or production scaling.

**Token estimate:** Planning 1,000 · Implementation 4,000 · Testing/debugging 3,000 · **Total 8,000**

**Codex instruction:** Make no new product features; inspect all existing behavior, harden demo paths and failures, run the complete automated and manual smoke suite, report evidence of each scenario, then stop.

# TOKEN BUDGET

| Phase | Planning/reasoning | Implementation | Testing/debugging | Total |
|---|---:|---:|---:|---:|
| 1. Foundation and local runtime | 1,500 | 5,000 | 2,000 | 8,500 |
| 2. Persistent household memory | 1,500 | 6,000 | 2,000 | 9,500 |
| 3. Deterministic meal decision engine | 2,000 | 7,000 | 3,000 | 12,000 |
| 4. Agency, approvals, workflow state | 1,500 | 6,000 | 2,500 | 10,000 |
| 5. Cook communication and memory closure | 1,500 | 6,000 | 2,500 | 10,000 |
| 6. Voice and photo input | 1,500 | 5,500 | 3,000 | 10,000 |
| 7. Demo hardening | 1,000 | 4,000 | 3,000 | 8,000 |
| **Entire project** | **10,500** | **39,500** | **18,000** | **68,000** |

Most expensive phases:

- **Phase 3:** constraint scoring, inventory arithmetic, procurement alternatives, and safety tests.
- **Phase 5:** validated LLM integration combined with stateful loop closure and recovery flows.
- **Phase 6:** local multimodal provider integration and hardware-dependent debugging.

Relatively cheap phases:

- **Phase 1:** once toolchain decisions are fixed.
- **Phase 7:** if prior phases maintain tests and deterministic seed fixtures.

Mandatory review stops:

1. After Phase 2: verify the persistent schema matches household reality before building decisions on it.
2. After Phase 3: review scoring behavior and recipe/store seed data before autonomous workflow logic.
3. After Phase 5: review whether the product genuinely closes the loop and improves subsequent recommendations.
4. After Phase 6: verify laptop performance, Hindi/Hinglish quality, and user-confirmation safety before demo hardening.

# MILESTONES

| Milestone | Required working state before proceeding |
|---|---|
| M1 — Local stack | Frontend, backend, SQLite, seeded data, and Qwen3 health check work locally. |
| M2 — Durable memory | Household, cook, inventory, leftovers, history, and budget survive restart and are editable. |
| M3 — Trustworthy decisions | The engine produces safe, explainable meal and procurement proposals from persisted state. |
| M4 — Real agency | Triggered loops, tiered approvals, tasks, audit history, and timeout behavior work without external services. |
| M5 — Closed loop | Cook confirmation and eater feedback update inventory, preferences, history, and next-day recommendations. |
| M6 — Multimodal local capture | Voice/photo input safely enters the same confirmed inventory state as typed input. |
| M7 — Demo ready | All required scenarios pass from a clean reset with tests, error handling, and documented commands. |

# EXECUTION STRATEGY

For every phase, Codex must follow this protocol:

1. Inspect the existing codebase and current test state.
2. Understand the architecture and earlier-phase interfaces before editing.
3. Implement only the current phase’s listed functionality.
4. Avoid dependencies, abstractions, integrations, and infrastructure not required by that phase.
5. Preserve all existing working behavior and backward-compatible API/UI contracts.
6. Add or update unit, integration, and relevant browser tests.
7. Run focused tests, then applicable smoke tests.
8. Fix defects caused by the current implementation only.
9. Report changed files, behavior, tests run, results, and known limitations.
10. Stop after the phase; never start the next phase automatically.

The agent must use deterministic fixtures and mocked local providers in tests. It must never substitute an LLM call for a deterministic policy, calculation, safety rule, approval decision, or state transition.

# FINAL DEFINITION OF DONE

The project is complete when, entirely on the local laptop:

- Qwen3 4B runs through Ollama with GPU acceleration for permitted language tasks.
- SQLite stores household state across restarts.
- The agent handles typed household state, inventory, expiry, leftovers, preferences, allergies, nutrition, cook capability, timing, guests, and budgets.
- The deterministic engine selects and explains safe, feasible meal options and sourcing paths.
- The agent creates local procurement/manual-shopping tasks and enforces green/yellow/red approvals.
- The cook can receive English/Hindi/Hinglish instructions and report completion, substitutions, or mishaps.
- Eater feedback and cooking outcomes update inventory and preference memory so later decisions change appropriately.
- Voice and photo capture are optional local enhancements with explicit human confirmation and text fallback.
- All six demo scenarios are reproducible from a clean seeded reset.
- pytest and Playwright suites pass.
- No unavailable rail, AWS capability, external payment, external order, or external messaging integration is misrepresented as implemented.
