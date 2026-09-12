---
name: household-agent-build
description: Enforces phase-by-phase implementation of the household-orchestration agent against its build_map.md. Use for any request to implement, continue, resume, or build this project, even if no phase is named. Determines current phase, implements ONLY it, tests it, verifies acceptance criteria, reports, then STOPS. Not for planning/redesigning the Build Map.
---

# household-agent-build

Guardrail skill: do exactly one phase, then stop. Never auto-continue to the next.

## Read first
1. `docs/build_map.md` and `docs/plan.md` — source of truth for phase scope. Re-read fresh each run.
2. `docs/progress.md` — source of truth for what's done. 
3. Existing code for files the phase touches.

## Workflow (every step, in order, no skipping)
```
Determine current phase → read its requirements → inspect existing code →
implement ONLY that phase → run tests → smoke test →
verify acceptance criteria → update progress.md → STOP
```

**Current phase** = lowest unmarked-complete phase in `progress.md`. Ignore user
phrasing that implies otherwise unless they explicitly override (e.g. "redo
Phase 2") — confirm before honoring an override. Check the phase's
`Dependencies` are marked done first; if not, stop and say so instead of
implementing out of order.

## Hard rules
- Never build anything under that phase's "Do not implement yet."
- Never skip a phase or pre-build later-phase functionality "while you're in there."
- Deterministic Python owns all business logic, math, ranking, approvals, and
  state transitions — never the LLM. Qwen3 4B is confined to unstructured
  language tasks (parsing Hindi/Hinglish/English input, preference-conflict
  explanations, feedback parsing, cook messages), and only from the phase that
  introduces that usage onward (Phase 5+; Whisper/Qwen2.5-VL from Phase 6).
- No AWS, external rails, WhatsApp, real payments/ordering/checkout, or
  infra/abstractions the current phase doesn't need.
- Preserve prior phases' working behavior and API/UI contracts.
- Tests use deterministic fixtures / mocked local providers, never live LLM calls.
- Check acceptance criteria one item at a time — don't eyeball it. If the phase
  is a mandatory review stop (after Phase 2, 3, 5, or 6), say so in the report.

## Report, then stop
State: phase done, files changed, test results (pass/fail counts), acceptance
criteria met/not met, known limitations, next phase + its dependency on this one.
Update `docs/progress.md` with the same. Then stop — do not start the next
phase's work in any form until the user explicitly says to proceed.

## Invocation
Triggers on `$household-agent-build`, "implement the next phase," "continue the
build," "resume where we left off," "implement Phase N," or similar — not just
the literal skill name.