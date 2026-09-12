## Local-first build plan

### 1. Product boundary

Build a working local household-orchestration agent that can decide, coordinate, remember, and recover across the complete meal loop:

```text
Trigger → understand household state → select meal → source gaps
→ brief cook → capture result → update memory → improve next decision
```

Excluded from code for now:

- Gnani, Delhivery, Pine Labs
- AWS and deployment
- Real quick-commerce checkout/payment
- WhatsApp integration

Those actions become local, explicit workflows: a procurement comparison board, a manual-shopping task, and an approval queue.

### 2. Technical stack

| Area | Choice |
|---|---|
| Backend/agent | Python 3.12 + FastAPI |
| Local LLM | Ollama + `qwen3:4b`, GPU-enabled |
| Persistent memory | SQLite + SQLModel |
| Frontend | React + Vite + TypeScript |
| Voice input | faster-whisper, English/Hindi |
| Image inventory | Add `qwen2.5vl:3b` after updating Ollama |
| Scheduling | APScheduler |
| Tests | pytest, Playwright for full workflow tests |

The LLM will only parse unstructured input, explain preference conflicts, and create cook-ready messages. All planning, budget math, inventory calculation, ranking, expiry logic, and approvals remain deterministic Python code.

### 3. Project structure

```text
backend/
  app/
    api/                 # FastAPI routes
    agent/               # Orchestrator and tool policy
    domain/              # Rules, scoring, state transitions
    models/              # SQLite/SQLModel entities
    services/            # Inventory, planner, budget, feedback, speech
    providers/           # Ollama, Whisper, vision-model adapters
    seed/                # Demo household, dishes, store prices
    tests/
frontend/
  src/
    pages/               # Dashboard, inventory, meal plan, approvals
    components/
    api/
docs/
  demo-scenarios.md
  architecture.md
```

### 4. Core data model

Persist these entities per household:

- Household members: name, language, diet, allergies, health constraints, likes/dislikes.
- Cook profile: English/Hindi preference, cooking capability, available hours, dish confidence.
- Inventory lots: ingredient, quantity, unit, purchase date, expiry date, storage location.
- Leftovers: source dish, portions, expiry, reuse suggestions.
- Dish catalog: ingredients, prep time, servings, nutrition, tags, cook-skill requirement.
- Dish history: date, acceptance, rating, leftovers, cook modifications.
- Preference signals: feedback text, parsed sentiment, context, confidence, expiry of temporary preference.
- Budget ledger: monthly limit, spent amount, planned spend, category allocation.
- Procurement options: local stores, prices, stock, delivery estimate, manual-shopping availability.
- Approval requests: action, tier, spend, reason, status.
- Meal loops: trigger, context, proposed dishes, chosen plan, cook status, completion status.

### 5. Agent capabilities

Implement these deterministic tools, callable by one orchestration agent:

1. `capture_inventory`
   - Accept typed entries first.
   - Add voice transcription and photo extraction later.
   - Require human confirmation before uncertain quantities/expiry dates are stored.

2. `build_meal_context`
   - Combine day/time, cook availability, guests, leftovers, budget, recent meals, health constraints, and urgency.

3. `rank_dishes`
   - Exclude unsafe dishes.
   - Reward ingredients nearing expiry and usable leftovers.
   - Penalize recent repetitions.
   - Score household satisfaction, nutrition, prep time, budget, and cook ability.
   - Return 2–3 viable candidates with a transparent score breakdown.

4. `compute_procurement_gap`
   - Compare chosen dish requirements with inventory.
   - Produce: already available, must buy, optional substitution, and insufficient-stock lists.

5. `choose_procurement_path`
   - Compare seeded/local store prices and travel/delivery estimates.
   - Choose one: use stock, manual purchase, simulated order, or alternate dish.
   - Consolidate items and respect monthly and per-meal budgets.

6. `classify_autonomy`
   - Green: routine, within budget, fresh inventory, known item.
   - Yellow: substitution, moderate variance, or unusual budget impact.
   - Red: high spend, new/unusual product, uncertain inventory, health-sensitive change.
   - Green may create a pending local purchase task; yellow/red require explicit approval.

7. `brief_cook`
   - Generate a short English/Hindi/Hinglish cooking brief through Qwen.
   - Include dish, portions, timing, substitutions, and allergy constraints.
   - Let the cook confirm, reject, or report a missing ingredient/mishap.

8. `close_meal_loop`
   - Record cook confirmation, eater feedback, leftovers, and ingredient usage.
   - Update inventory, meal history, temporary preference signals, and budget.
   - Mark incomplete loops as `unclosed`; never infer success silently.

### 6. User experience

Build five screens:

- **Today:** agent status, trigger, selected meal, why it was chosen, cook brief, completion state.
- **Inventory:** pantry/fridge/leftovers, expiry alerts, typed/voice/photo capture.
- **Household:** members, allergies, diets, cook skill, language, and budget configuration.
- **Approvals:** yellow/red decisions with exact cost, alternative, and consequence.
- **Memory:** meal history, feedback trends, waste avoided, weekly reflection.

The main interaction is an action panel, not an open-ended chatbot. The user can write or say: “Guests are coming,” “paneer is spoiled,” “cook has 30 minutes,” or “don’t make dal again,” and the agent turns it into state changes and a revised plan.

### 7. Build phases

1. **Foundation**
   - Create FastAPI/React project, SQLite schema, seed household, recipe catalog, and local store data.
   - Add Ollama health check and structured JSON response validation.

2. **Persistent household memory**
   - Implement inventory, expiry, leftovers, member profiles, cook profile, dish history, and budgets.
   - Build CRUD screens and seed/reset support for demos.

3. **Decision engine**
   - Implement eligibility filters, deterministic scoring, ingredient-gap calculation, substitutions, and procurement routing.
   - Add explainable score breakdowns.

4. **Agency and guardrails**
   - Implement event triggers, green/yellow/red policies, approvals, action audit trail, stale-inventory checks, and loop timeouts.

5. **Cook and feedback loop**
   - Add English/Hindi cook briefs, cook confirmations, eater feedback parsing, leftovers, and preference updates.
   - Add guest and mid-cook-mishap recovery flows.

6. **Local multimodal input**
   - Add faster-whisper for English/Hindi voice notes.
   - Upgrade Ollama and add Qwen2.5-VL 3B for fridge-photo extraction.
   - Keep typed capture as the reliable fallback.

7. **Demo readiness**
   - Create repeatable seed scenarios, error states, visible decision audit, and end-to-end tests.

### 8. Required demo scenarios

- **Expiry-led routine meal:** expiring vegetables drive selection; green procurement task is created.
- **Conflicting household preferences:** agent explains trade-off, asks for a decision, and records the outcome.
- **Unplanned guests:** servings increase; agent changes dish/procurement route and requests approval.
- **Cook mishap:** reported spoiled/dropped dish produces a fast, in-stock alternative.
- **Feedback-driven memory:** “too heavy” feedback changes the next day’s ranking.
- **Budget constraint:** the best-scoring dish is rejected in favor of an affordable option.

### 9. Acceptance criteria

The prototype is ready when it can:

- Run entirely on the laptop using Qwen3 4B and SQLite.
- Persist household state across restarts.
- Produce a transparent, constraint-safe meal decision.
- Handle expiry, leftovers, repeat avoidance, allergies, nutrition, cook ability, time, guests, and budget.
- Calculate missing ingredients and recommend a local procurement/manual-shopping action.
- Require approval for yellow/red actions.
- Create English/Hindi cook instructions.
- Update persistent memory after feedback or cooking outcomes.
- Recover from an unexpected cooking mishap without restarting the entire flow.

No rail integration will be represented as working until you obtain the corresponding access.