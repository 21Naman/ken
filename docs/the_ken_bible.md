# Project Bible — Household Orchestration Agent
## The Ken's Case Competition 2026 — "The Great Rewiring"

**Status:** Pass 1 (Extraction) complete. Passes 2–4 pending.

---

## PASS 1 — EXTRACTION

### 1.1 Preflight Log

- **Live research capability:** Yes (web search available) — Pass 3 will run fully specified, not corpus-only.
- **Minimum viable corpus:** Satisfied — official Problem Statement context (opening description + judging page), official judging criteria (5 criteria), official competition requirements (10-question Solution Assembly format, ground rules) are all present, plus the team's brainstorm (Ken_case.txt).
- **12-category inventory:**

| # | Category | Status |
|---|---|---|
| 1 | Official PS | Present — team's own framing ("aaj kya banega") + official opening title/blurb ("Sticking to the goal" confirmed NOT applicable; this team's opening is the household-orchestration/cooking one) |
| 2 | Official judging criteria | Present — Evidence, Creativity, Clarity, Feasibility, Thoroughness |
| 3 | Official competition requirements | Present — 10-question Solution Assembly, ground rules, two tracks |
| 4 | Competition instructions/guidelines | Present — ground rules section |
| 5 | Brainstorm | Present — Ken_case.txt, 39 items tagged below |
| 6 | Team notes/observations | Present — team's opening framing paragraph |
| 7 | Previous research | Not provided |
| 8 | Competitor information | Not provided (to be sourced in Pass 3) |
| 9 | Product ideas | Present, embedded in brainstorm |
| 10 | Technical ideas | Present — rail-specific notes (Pine Labs, Delhivery, Gnani) |
| 11 | User pain points | Present, embedded in brainstorm |
| 12 | Additional documents | None beyond the two files + competition page text |

- **Context/length:** Corpus is small enough to hold across all passes without truncation risk. Deliverable is long by design (38 sections + 11 artifacts); building it pass-by-pass, saved to file, with a check-in after each pass.

---

### 1.2 Problem Statement Deconstruction

The competition itself does not supply a canned PS text for this specific opening beyond a working title reference ("aaj kya banega" / household orchestration). The team's own framing functions as the operative PS here, so it is deconstructed as such, with every line marked **stated** or **inferred**.

**Core problem statement (stated, team framing):** In urban Indian households, one person is repeatedly responsible for deciding what to cook, synthesizing (a) fridge contents including spoilage, (b) shifting family taste/health needs, (c) what the cook can realistically prepare in available time, and (d) what must be ordered via quick-commerce to close the gap — with no persistent shared memory across days.

**Explicit requirements (stated):**
- Must track real inventory (including spoilage/expiry) — B001, B013
- Must avoid repeating dishes / support novelty — B002
- Must account for family taste, health conditions, allergies — B003
- Must match dishes to the cook's actual capability — B004
- Must determine what to procure to complete a target dish, given delivery time constraints — B005
- Must respect budget in ingredient/dish choice — B006
- Must respect time-of-day and time-available constraints — B007, B017
- Must support an in-person-shopping fallback to ordering — B008
- Must communicate with a cook whose identity/role varies (chef, spouse) — B009
- Must handle leftovers — B010
- Must produce dish recommendations — B011
- Must capture preference feedback over time — B012
- Must support festival/occasion-specific meals — B014
- Must compare price/quality across ordering options — B015
- Must balance nutrition/macros against family requirements — B016
- Must handle last-minute mishaps (spoiled-in-cooking, dropped dish) — B018
- Must handle unplanned guests — B019
- Must reason about monthly budget allocation across a mix of bulk/consolidated orders and per-dish top-ups, comparing prices across apps, consolidating into as few orders as possible, and asking approval for unusual spend — B020

**Implicit requirements (inferred):**
- The system must maintain **persistent, cross-day memory** — the explicit complaint is that WhatsApp/verbal/ad hoc tools have no shared memory, so *not* accumulating state across decisions would fail the core premise, even though no single brainstorm line says "build memory" directly.
- The system must operate **multilingually / across registers**, since the cook may be addressed differently than the family (B009, B029) and may not be literate in the household's primary app language.
- The system must tolerate **ambiguous or partial input** (voice in a noisy kitchen, informal WhatsApp text) rather than requiring structured data entry, since the stated inputs are fridge photos/voice/text and WhatsApp voice/text (B031) rather than a dedicated data-entry UI.
- The system needs a **human-override / approval mechanism**, since B020 explicitly asks for approval on unusual purchases and B024 describes a human making the final call when AI-scored options are close.

**Target users (stated):** the household decision-maker (implicitly the person who currently absorbs "aaj kya banega"), the cook (who "might vary — chef, wife, husband"), and the household's eaters more broadly (whose preferences/feedback feed the system) — B009, B012.

**Stakeholders (stated + inferred):** decision-maker (stated), cook (stated), other household eaters/family members (stated via preferences/feedback), quick-commerce/delivery platforms (inferred, as procurement counterparties), and — per the official case's rail structure — Pine Labs, Delhivery, Gnani as infrastructure stakeholders (stated, from rail-partner descriptions).

**User problems (stated):** decision fatigue, food waste, repeated low-grade emotional burden despite having help (cook, 10-minute delivery) — from the team's framing paragraph.

**Contextual problems (stated):** no shared memory across existing tools (WhatsApp, verbal check-ins, ad hoc app orders); taste is not static but "contextual + temporal + household-specific" (B028) — a stated dish preference this week may not hold next week depending on how heavy/light/healthy/cheat-meal the household wants to go.

**Constraints (stated):** budget (B006, B020), delivery time windows (B005), cook's real skill/time (B004, B007), kitchen background noise degrading voice capture (from the Gnani rail note, B039).

**Desired outcome (stated):** "Not a better recipe or meal-planning app... an agent that takes over the orchestration itself" — B021, B034, B035. The stated bar is a system that *takes over the decision* rather than assisting a human who still makes it, i.e., "I've figured out what we're eating, made sure we have what we need, told the cook, and remembered what happened so tomorrow is easier" (B035).

**Success conditions (inferred):** every workaround "already tried in that shape has failed to stick" (stated) — implying success is specifically defined by *durability of adoption*, not just correctness of a single recommendation. A dish suggestion that is accurate but requires daily manual re-engagement would not meet the team's own stated bar.

**Assumptions embedded in the PS (inferred, to be tested in Pass 3):**
- That households with a cook present (not just self-cooking households) are the primary target — most brainstorm items assume a cook distinct from the decision-maker.
- That quick-commerce/10-minute delivery is already present and trusted enough to receive agent-placed orders (B025, B037) — not yet validated against real willingness to hand over payment authority (the trust questions in B032 flag this as unresolved even by the team itself).
- That WhatsApp is the de facto coordination layer for Indian households (implicit in B031, B040) rather than a competition-specific reach for familiarity.

**Ambiguities in the PS (inferred):** Whether the primary decision-maker and the cook are ever the same person (self-cooking households) is unaddressed by the brainstorm, which consistently frames "cook" as a distinct role. Whether the agent is expected to operate across multiple simultaneous households (shared extended family, joint kitchens) is also unaddressed.

**Unanswered questions the PS raises (inferred):** How does the system resolve conflicting feedback from multiple eaters (B012) when preferences differ? What happens when the cook disagrees with or overrides the agent's decision — is that logged as a preference update or discarded?

---

### 1.3 Judging-Criteria Deconstruction

| Criterion | What it actually means | What judges are likely looking for | Evidence for a high score | What causes a low score | Average vs exceptional |
|---|---|---|---|---|---|
| **Evidence** | Did a real person tell you this, not just the team's own intuition? | First-hand interviews/recordings with people who actually experience this (decision-makers, cooks), and — notably — insights *not already in the team's own framing*, meaning something surprising found during the process, not just confirmation of the brainstorm | Recorded or documented conversations; a specific quote or observed workaround (e.g., an actual WhatsApp thread, a notebook, a fridge whiteboard) that reshaped a specific design decision | Evidence that only confirms what the brainstorm already assumed; no proof of contact with real users; insight that reads as generic ("people are busy") rather than specific and non-obvious | Average: cites that "people find this stressful." Exceptional: cites a specific, surprising behavior (e.g., what the decision-maker is actually protecting when they insist on cooking a specific dish) and shows exactly which design element exists *because* of it |
| **Creativity** | Is the solution fresh, counterintuitive, different from an obvious AI-wrapper answer? | A framing that isn't "ChatGPT for recipes" — the team's own material already anticipates this failure mode ("not a recipe-making app... needs agency") | A genuinely surprising mechanism (e.g., the agent negotiating with the cook rather than the user, or the green/yellow/red order-classification idea, B030) | A polished but generic meal-planner; anything that reads like existing recipe/grocery apps with a chat interface bolted on | Average: "AI suggests meals + orders groceries." Exceptional: a mechanism nobody else in the room proposed — e.g., agent-to-cook negotiation as the primary interface rather than agent-to-consumer |
| **Clarity** | Is the solution communicated specifically, not vaguely? | The six-step agent description fitting in 15 words/step without hand-waving; unambiguous statements of rail roles | Precise, falsifiable statements ("the agent orders milk when inventory model predicts <2 days remaining") | Vague verbs ("the agent understands preferences and helps decide") with no mechanism specified | Average: describes what the agent does. Exceptional: describes exactly how, with concrete triggers and thresholds |
| **Feasibility** | Can this actually be built/implemented in a reasonable way, given real-world constraints (voice error rates in noisy kitchens, payment auth friction, logistics windows)? | Awareness of where the idea breaks against the actual rail limitations (already partially flagged in Ken_case.txt itself, e.g., Gnani struggling with pressure-cooker noise, Pine Labs failing on variable-weight produce) | A design that names its own weakest technical link and proposes a workaround, rather than ignoring it | A design that assumes perfect voice transcription, frictionless variable-amount payments, or same-day logistics with no acknowledgment of the stated rail limitations | Average: proposes the idea. Exceptional: proposes the idea *and* shows where it currently breaks against the real rail (this is explicitly asked for in Q5 of the submission) |
| **Thoroughness** | Is the solution meticulous and detailed rather than a sketch? | Depth across the full loop (decision → inventory → procurement → cook → consumption → next decision, B022), not just the flashiest step | Detail on edge cases (guests, B019; last-minute mishaps, B018; leftovers, B010) as well as the happy path | A pitch that only covers the "agent suggests a dish" moment and stops before procurement/cook communication/inventory update | Average: covers the happy path. Exceptional: covers the loop closing (inventory gets updated after cooking, feeding tomorrow's decision) |

**Mapping chain (per criterion → product):**
```
JUDGING CRITERION → JUDGE EXPECTATION → REQUIRED EVIDENCE → PRODUCT REQUIREMENT → FEATURE
Evidence      → non-obvious, real insight        → interview/recording/artifact → insight-driven design choice → a specific loop step justified by that insight
Creativity    → non-generic mechanism            → a mechanism no recipe app has → agent-to-cook negotiation, not agent-to-consumer-only → cook-facing interface
Clarity       → falsifiable, specific description → 15-word/step six-step spec   → named triggers/thresholds → e.g. inventory depletion forecast triggers reorder
Feasibility   → acknowledges real rail limits     → named breaking point + workaround → rail-aware architecture → e.g. fallback to text when voice fails
Thoroughness  → full loop coverage incl. edge cases → mishap/guest/leftover handling → loop-closing memory update → post-meal inventory reconciliation step
```

**Note on submission format vs. this document:** the actual deliverable to the competition is the 10-question Solution Assembly (team, one insight, six-step agent, rail touches, rail to innovate on, customer asset, annexation use-case, opening you wouldn't automate, company that should've built this, track) — a highly compressed, word-capped format. This Project Bible is the internal reasoning document from which those 10 compressed answers will be derived in Pass 4; it is explicitly not itself the submission.

---

### 1.4 Brainstorm Inventory — Full Line-by-Line Tagging

Every item from Ken_case.txt, tagged with a stable ID. Condensed per-item analysis (underlying claim, need, severity/frequency signal, workaround, product implication, related items, confidence) rather than full prose per field, to keep this pass navigable — full cross-referencing happens in Pass 2.

| ID | Raw item (paraphrased) | Underlying need | Workaround today (stated/inferred) | Product implication | Related IDs | Confidence |
|---|---|---|---|---|---|---|
| B001 | Utilize available ingredients, accounting for spoilage | Waste reduction, inventory-aware planning | Manual fridge check (inferred) | Inventory tracking with expiry awareness | B013, B025 | Medium (stated, not yet evidenced with real users) |
| B002 | New recipes / avoid repetition | Variety without added cognitive load | Memory-based avoidance by decision-maker (inferred) | Recommendation engine must track recent-dish history | B011, B012 | Medium |
| B003 | Family taste, health, allergies | Safety + satisfaction across multiple eaters | Decision-maker holds this in their head (inferred) | Persistent per-person preference/constraint profile | B012, B016, B028 | High (central to the whole premise) |
| B004 | What can the chef make | Match dish to cook's real capability | Decision-maker's tacit knowledge of cook's skill (inferred) | Cook capability model, not just recipe database | B009, B026 | Medium |
| B005 | What to order to complete a dish, given delivery time + inventory | Gap-filling procurement | Manual mental math (inferred) | Procurement-gap calculation as core loop step | B020, B025, B037 | High |
| B006 | Budget-based dish/ingredient quality choice | Cost control | Manual price comparison (inferred) | Budget constraint baked into recommendation, not post-hoc | B015, B020 | Medium |
| B007 | Time-availability-based dish choice | Realistic scheduling | Decision-maker's judgment (inferred) | Time-to-prepare as a hard filter | B017 | Medium |
| B008 | In-person shopping as alternative to ordering | Cost/quality control, or delivery-time mismatch | Physically visiting shops on the way (stated) | Agent must sometimes recommend "buy yourself" not just "order" | B005 | Low — least developed idea in the corpus |
| B009 | Cook communication; cook role varies (chef/spouse) | Reliable instruction-passing regardless of who cooks | Verbal/WhatsApp check-in (stated) | Cook-facing interface must be role-agnostic and register-appropriate | B004, B026, B029 | High |
| B010 | Deal with leftovers | Waste reduction, loop-closing | Manual reincorporation into next meal (inferred) | Leftover tracking feeds next-day recommendation | B001, B013 | Medium |
| B011 | Dish recommendations | Core output of the system | N/A — this is the system's job | Recommendation engine, gated by all above constraints | B002, B004 | High |
| B012 | Preferences + feedback mechanism | Learning loop over time | None persistent today (stated — this is the core gap) | Feedback capture after each meal, feeding memory | B002, B003, B028 | High |
| B013 | Ingredient expiration + leftovers (near-duplicate of B001/B010) | Same as B001/B010 | — | Same as above — flagged as duplicate | B001, B010 | High (reinforces, not new) |
| B014 | Festival/occasion-based meals | Cultural/contextual dish selection | Manual seasonal awareness (inferred) | Calendar-aware recommendation layer | B027 | Low — underdeveloped, single mention |
| B015 | Price/quality comparison while ordering | Value optimization | Manual app-switching (inferred) | Cross-platform price comparison before order placement | B006, B020 | Medium |
| B016 | Nutrition/macro balancing | Health management | Manual awareness or none (inferred) | Nutrition constraint layer alongside taste | B003 | Medium |
| B017 | Meal-time-of-day distinction | Contextually appropriate suggestions | Implicit human judgment (inferred) | Time-of-day as a recommendation parameter | B007 | Medium |
| B018 | Last-minute mishaps (dish spoiled/dropped while cooking) | Real-time recovery, not just planning | Improvisation by cook (inferred) | Agent must support mid-cook recovery, not just pre-cook planning | B022 | Low — single mention, high specificity |
| B019 | Guests showing up unannounced | Dynamic scaling of quantity/dish choice | Improvisation (inferred) | Guest-count as a live input, not just planned state | — | Low |
| B020 | Budget-aware bulk/consolidated ordering across apps, approval on unusual spend | Financial control + reduced order friction | Manual, ad hoc ordering per app (stated) | Core procurement-agent spec: depletion recognition, forecasting, consolidation, price comparison, budget-bounded ordering, approval gate | B005, B006, B015, B025, B030, B037 | High — most fully specified single item in the corpus |
| B021 | Explicit rejection of "just a recipe app" — needs agency | Differentiation from failed prior art | N/A | Positions the whole product as agentic, not generative-only | B034, B035, B036 | High — stated as the team's central thesis |
| B022 | Core loop: decision → inventory → procurement → cook → consumption → next decision | System architecture backbone | N/A | This is the literal state machine the agent must implement | B018, B025 | High |
| B023 | Entity list: chef, diet history, preferences, allergies, nutrient reqs, delivery apps, fridge, WhatsApp, dining table, day-of-week limits, time-of-day | Complete state model | N/A | Defines the agent's state/context schema | B003, B031 | High |
| B024 | Interface: AI scores dish options, consumer makes final call, else highest-rated forwarded to chef | Human-in-the-loop decision closure | N/A | Defines the approval/default mechanism at the decision step | B026, B032 | Medium |
| B025 | Agent places routine orders (e.g., milk) accounting for expiry | Autonomous routine procurement | N/A | Low-risk automatic reorder path, distinct from discretionary orders | B005, B030, B037 | Medium |
| B026 | Communicating with the chef is itself agentic | Frames cook-communication as a first-class agent capability, not a notification | N/A | Cook-facing dialogue must be bidirectional and adaptive, not templated | B004, B009, B029 | High |
| B027 | Agentic loop triggered at variable timestamps based on dynamic calendar | Proactive, not purely reactive, operation | N/A | Scheduler/trigger design is a core architecture question | B014 | Medium |
| B028 | Taste is contextual + temporal + household-specific, on top of static preferences | Preferences aren't fixed; they drift with mood/context | N/A | Preference model must be dynamic/contextual, not a static profile | B003, B012 | High — one of the sharper non-obvious claims in the corpus |
| B029 | Agent extracts action-relevant info from regional voice chat; "joins the kitchen conversation" via Gnani rather than moving workflow to text | Meet the cook in their existing medium | N/A | Voice-first, ambient capture is a hard requirement, not a nice-to-have | B009, B026, B039 | High |
| B030 | Order classification: green (routine)/yellow (usual brand unavailable)/red (large/expensive/unique) | Risk-tiered autonomy for spending | N/A | Defines the approval-gate logic directly | B020, B032, B037 | High |
| B031 | Inputs: fridge inventory (photo/voice/text), WhatsApp channels, audio from chef/eaters | Multi-modal, low-friction data capture | N/A | Input layer spec | B023, B029 | High |
| B032 | Trust questions: read grocery orders? talk to cook? read family WhatsApp? spend ₹500/₹2,000 without asking? | Explicit acknowledgment of the trust/consent barrier | N/A — the team itself is flagging this as unresolved | These become literal onboarding/consent questions and a direct input to Q6 (customer asset) | B006, B020, B024 | High — this is evidence the team already anticipates its own adoption risk |
| B033 | Who has users + data + payment relationship (grocery, food delivery, payments, household commerce, appliances, consumer platforms) | Identify the incumbent best positioned to have built this | N/A | Directly answers submission Q9 framing | B037, B038, B039 | Medium — a prompt to research, not a finding |
| B034 | "Don't build an AI that tells me what to cook. Build an AI that runs the kitchen." | Restates B021 as the product tagline | N/A | Positioning statement | B021, B035 | High |
| B035 | Meal-planning app answers "what should we eat"; agent answers "I've handled it and remembered for tomorrow" | Defines the bar for what counts as success | N/A | This is the functional spec for "done" | B012, B021, B034 | High |
| B036 | "Your opening isn't really about food. It's about household orchestration." | Reframe: the product category is orchestration, not food-tech | N/A | Positions the pitch and possibly the annexation answer (Q7) | B021 | High |
| B037 | Pine Labs rail: auto-debit for recurring bulk orders; breaks on variable-weight/loose produce triggering fraud/2FA | Payments rail role + named limitation | N/A — team-authored rail analysis | Direct input to submission Q4/Q5 (which rail to touch, which to innovate on) | B020, B030 | High — team has already done first-pass rail feasibility work |
| B038 | Delhivery rail: bulk/scheduled staple delivery; breaks on tight delivery windows and perishables — team's own note says "kinda useless most people don't require it" | Logistics rail role + team's own skepticism of its relevance | N/A | Signals this rail may have a *weak* role in the actual solution — worth testing in Pass 3 rather than assuming it's load-bearing | B005 | Medium — the team is already skeptical of its own idea here |
| B039 | Gnani rail: multilingual/code-mixed voice capture; breaks on kitchen background noise + dialect variation | Voice rail role + named limitation | N/A | Direct input to Q5 (rail to innovate on) — voice-in-noisy-kitchen is explicitly named as unsolved | B029, B031 | High |

**Duplicates identified:** B013 duplicates B001/B010 (ingredient expiration + leftovers stated twice). **Reinforcements:** B021/B034/B035/B036 all restate the same "agency, not recipes" thesis from different angles — this is the single most-repeated idea in the corpus, a strong signal of where the team's conviction is strongest.

---

*Pass 1 complete.*

---

## PASS 2 — CONNECTION

### 2.1 Idea Relationship Map

Relationships across the 39 tagged items, by type. (Only relationships worth acting on are listed — not every possible pair.)

**Reinforcement** (different items, same underlying problem):
- B021 ↔ B034 ↔ B035 ↔ B036 — all restate "agency over recipes" from different angles. Strongest reinforcement cluster in the corpus.
- B001 ↔ B010 ↔ B013 — spoilage/leftovers/expiration are one problem said three times.
- B006 ↔ B015 ↔ B020 — budget-aware ordering appears at three levels of specificity (dish choice → price comparison → full procurement spec).

**Complementarity** (stronger combined than alone):
- B004 (chef capability) + B009 (cook communication) + B026 (cook comms is agentic) → together these define an entire cook-facing subsystem that no single item describes alone.
- B028 (taste is contextual/temporal) + B012 (feedback mechanism) → a feedback loop is only actually useful *because* taste drifts; if taste were static, a one-time preference form would suffice. B012 without B028 is a static profile; B012 with B028 is a learning system.
- B030 (green/yellow/red order classification) + B032 (trust questions about spend) → B030 is the technical answer to the exact concern B032 raises. This pairing is likely your strongest Feasibility + Evidence combination.
- B031 (multimodal input) + B029 (voice joins kitchen convo via Gnani) → defines the entire ambient-capture input layer.

**Dependencies** (one only works if the other is also true):
- B025 (autonomous routine reorder) depends on B001/B013 (accurate expiry-aware inventory) — without reliable inventory state, autonomous reordering is just guessing.
- B005 (procurement gap-filling) depends on B004 (cook capability model) — you can't know what's missing for a dish until you know which dish the cook can actually make.
- B024 (AI scores, human/cook decides) depends on B011 (recommendation engine existing) as a precondition.
- Q5/Q7 of the actual submission (rail to innovate on; annexation) depend on B037/B038/B039 being resolved first — you cannot answer "which rail to innovate on" until Pass 3 tests whether B038 (logistics) is even load-bearing.

**Contradictions** (cannot both be fully true):
- B008 (in-person shopping as an alternative) sits in tension with B021/B034/B035 (agent "runs the kitchen," takes over the decision). If the agent is meant to fully take over, why does the corpus preserve a manual, human-executed fallback? This isn't fatal, but it's a real design tension: either the agent dispatches a task to a human ("go buy X on your way") as a legitimate agent action, or B008 is a hedge against the agent's own confidence that hasn't been resolved.
- B027 (proactive, calendar-triggered loop) is in mild tension with B018 (reactive last-minute mishap handling) — the architecture needs to support both a scheduled cadence *and* interrupt-driven recovery, which are different triggering models. Not contradictory in principle, but the corpus never reconciles how both triggers coexist in the same agent loop.

**Duplicates:** B013 is a duplicate of B001+B010 (already noted in Pass 1).

**Hidden connections** (not obvious from any single item):
- B009 (cook role varies: chef/wife/husband) + B023 (entity list includes "day of the week limitations") — read together, this implies the agent may need a *different communication register per household*, not just per cook-type, since who cooks on which day may itself vary. No single brainstorm line states this, but it falls directly out of combining two items.
- B032's trust questions ("would you let it read your family WhatsApp") + B031 (WhatsApp as an input channel) expose that the single riskiest input channel (family group chat, likely containing far more than meal talk) is also the one the corpus treats most casually as a data source. This is a real product risk that isn't flagged anywhere except implicitly.
- B030 (order risk tiers) + B024 (AI-scored options with human fallback) together suggest the *same* tiering logic (green/yellow/red) could generalize beyond orders — dish decisions might also deserve a green/yellow/red framing (routine dinner vs. a healthy-alternative override vs. a full guest-driven menu change), but the corpus only ever applies it to procurement.

**Emergent insight** (visible only once multiple items are combined):
- No single brainstorm item claims this, but B003 + B012 + B028 + B024 together imply that **the actual product is a preference-arbitration system, not a recommendation system.** The hard problem isn't generating a candidate dish (B011 is comparatively easy) — it's resolving whose preference wins today, given that everyone's stated preferences are themselves moving targets (B028) and multiple eaters may disagree (B012 doesn't specify how conflicts resolve). This reframes the core technical challenge away from "recipe generation" (which the team has already correctly rejected, B021) toward "constraint satisfaction across a shifting, multi-party preference set" — a meaningfully different (and more defensible) problem than most teams pursuing food-tech openings will likely land on.

---

### 2.2 Root Cause Analysis

```
SYMPTOM → CAUSE → ROOT CAUSE → USER NEED → OPPORTUNITY
```

**Thread 1 — Decision fatigue**
- Symptom: decision-maker re-answers "what to cook" every single day (stated).
- Cause: no tool aggregates the four inputs (inventory, preference, cook capability, procurement gap) in one place (stated).
- Root cause: existing tools (WhatsApp, verbal check-ins, delivery apps) have **no persistent shared memory** across days (stated) — each day's decision starts from zero.
- User need: a system that remembers yesterday's outcome and uses it today, without being re-asked.
- Opportunity: memory-as-the-product, not recommendation-as-the-product — the differentiator is persistence, not intelligence.

**Thread 2 — Food waste**
- Symptom: spoiled/expired ingredients, discarded leftovers (B001, B010, B013).
- Cause: inventory state exists only in the decision-maker's head, updated inconsistently.
- Root cause: there is no system-of-record for what's physically in the house that updates automatically from both procurement (what came in) and cooking (what got used) — the loop (B022) is currently closed manually, by memory, if at all.
- User need: inventory that updates itself from both ends of the loop.
- Opportunity: the "consumption → next decision" edge of B022 is the actual hard engineering problem (inferring usage from what was cooked, not requiring manual logging) — likely the single most technically interesting and defensible piece of the whole system.

**Thread 3 — Repeated emotional burden despite having help**
- Symptom: burden persists even with a cook and 10-minute delivery available (stated) — the problem isn't lack of *execution* help, it's lack of *decision* help.
- Cause: existing help (cook, delivery) requires the decision to already be made; neither actually makes the decision.
- Root cause: the entire ecosystem around this household (cook, delivery apps, grocery apps) is execution infrastructure with zero shared decision layer sitting on top of it.
- User need: something that sits *above* existing execution tools and coordinates them, rather than one more execution tool.
- Opportunity: this is exactly what B036 states directly ("it's about household orchestration") — the root cause analysis independently arrives at the same place the team's own thesis already claims, which is a good sign the team's instinct is sound, not just asserted.

**Thread 4 — Cook communication breakdown**
- Symptom: cook role varies and communication is ad hoc (B009).
- Cause: no single consistent channel/register works across chef, spouse, or other cook-types.
- Root cause: the system currently expects the decision-maker to translate the decision into cook-appropriate instructions themselves, every time, in whatever language/register that specific cook needs (inferred from B009 + B029).
- User need: the agent absorbs the translation work, not just the decision work.
- Opportunity: voice-first, register-adaptive cook interface (B029) as a distinct, separately valuable subsystem — arguably valuable even stripped of the meal-decision logic entirely.

---

### 2.3 Current User Workflow (Reconstructed, Without Any Agent)

**Steps actually taken today (inferred from stated pain points, since no direct workflow-observation data exists yet — this is the target for Pass 3 evidence-gathering):**

1. Decision-maker mentally reviews (or physically checks) fridge/pantry contents — no record kept.
2. Decision-maker recalls recent dishes to avoid repetition — memory-dependent, error-prone.
3. Decision-maker weighs stated family preferences, allergies, and *today's* mood/context (light vs. heavy, cheat day) — B028 says this shifts daily, so yesterday's answer doesn't carry over.
4. Decision-maker estimates what the cook can realistically make today, given the cook's skill and available time.
5. Decision-maker identifies the gap between what's on hand and what the dish needs.
6. Decision-maker checks (or guesses) delivery time windows and decides: order via app, or personally stop at a shop en route (B008)?
7. Decision-maker compares price/quality across apps if ordering (B015) — manual app-switching.
8. Decision-maker communicates the final decision to the cook, in whatever channel/register that cook uses (verbal, WhatsApp voice/text) — B009.
9. Cook prepares the meal; any mishap (spoiled dish, dropped dish) is handled ad hoc, off-system (B018).
10. Family eats; feedback (liked/disliked, "too heavy," "not again") is expressed informally, often not captured anywhere durable (B012) — this is the step where the "no shared memory" problem actually bites.
11. Leftovers, if any, are dealt with ad hoc, usually re-decided from scratch the next day rather than systematically folded into tomorrow's plan (B010).
12. Cycle repeats from step 1, with no carry-over of steps 9–11 into step 1 the next day.

**Coordination required:** with the cook (verbal/WhatsApp), with delivery apps (comparison across multiple apps), and implicitly with other family members (whose preferences must be solicited or guessed).

**Cognitive burden concentration:** steps 3–5 (matching preference + cook capability + inventory simultaneously) are the highest-burden steps, since none of the three inputs live in the same place and all three shift day to day.

**Time cost concentration:** step 7 (cross-app price/quality comparison) and step 6 (delivery-time-window checking) are the highest manual-time-cost steps, since they require switching between multiple apps with no aggregation.

**Most likely abandonment point:** step 10 — feedback capture — is the step most likely to simply not happen, because it has no natural end point or reward for the decision-maker; this is exactly the step the "no shared memory" complaint (stated) is describing, and it's the step where a manual system would be expected to quietly decay first.

**Where a new product can credibly intervene:** steps 1–2 (inventory + repetition-avoidance) are the most mechanically tractable — inventory can be captured via photo/voice (B031) and dish history is simple to log. Steps 8–9 (cook communication, mishap handling) require the hardest technical bet (voice-first, register-adaptive, real-time). **Where it cannot credibly intervene, at least at MVP:** step 4 (estimating a cook's real skill) likely still requires a human-provided capability model at first — inferring "what can this specific person cook" purely from data is a much harder cold-start problem than inventory or price comparison, and should probably be an explicit MVP scope boundary (flagged for Pass 4 / MVP Prioritization) rather than something the agent claims to solve immediately.

---

### 2.4 Stakeholder Analysis

| Stakeholder | Goals | Needs | Pain points | Constraints | Incentives | Info available to them | Info they lack | Decisions they make | Actions they take |
|---|---|---|---|---|---|---|---|---|---|
| **Decision-maker** | Get meals decided with less daily effort; reduce waste; keep family satisfied | A system that remembers and acts, not just suggests | Decision fatigue; feels burden despite having help (stated) | Budget, time, trust in handing over control | Wants the mental load gone, but risk-averse about spend/privacy (B032) | Full (tacit) knowledge of preferences, cook skill, inventory — but only in their head | A record of what actually worked over time | What to cook; how much autonomy to grant the agent; when to override it | Checks fridge, recalls preferences, instructs cook, places/approves orders |
| **Cook** (chef/spouse/etc., role varies) | Clear, actionable instructions; not be second-guessed constantly | To receive instructions in their own language/register, without friction | Ambiguous or last-minute instructions; being blamed for mishaps outside their control (spoiled ingredients they didn't choose) | Their own skill ceiling and available time | Wants fewer ad hoc interruptions, clear expectations | What they can physically prepare, what's currently in the kitchen (partially) | The decision-maker's current-day preference shifts (B028) unless told | What to actually cook, substitutions in the moment | Prepares the meal; may deviate from instructions live (B018) |
| **Other household eaters** | Meals they like; health needs met; occasional say in decisions | A feedback channel that's actually captured, not just spoken and forgotten | Preferences overridden or ignored; no mechanism to register "not again" persistently | Time/willingness to give explicit feedback | Want influence without doing the coordination work themselves | Their own preferences (tacit) | Whether their feedback ever reaches the actual decision | Whether to voice a preference at all this time | Comment informally, may not repeat feedback if it's never acted on |
| **Quick-commerce / delivery platforms** | Order volume, retained users | N/A (external) | N/A | Delivery windows, catalog/price data availability, fraud controls on variable-weight items (B037) | Want more orders, ideally larger/more predictable ones | Real-time catalog, price, delivery-window data | Household-specific context (which is exactly what the agent adds) | Which orders to fulfill, at what price | Fulfill or reject orders based on availability/fraud checks |
| **Pine Labs (payments rail)** | Adoption of P3P/Grantex for agentic payments | Agent flows that respect authorisation limits | Variable-cart-value purchases (loose produce) triggering fraud/2FA (B037 — team's own finding) | Bank-level fraud rules, real-time 2FA requirements | Wants to prove agentic payments work at scale | Authorisation/spend-limit APIs | Household-specific purchase context | Whether to authorize a given autonomous payment | Approve/decline transactions, trigger 2FA |
| **Delhivery (logistics rail)** | Adoption of Maps/MCP access by teams | Use-cases where scheduled bulk delivery genuinely fits | Team's own brainstorm calls this rail "kinda useless" for this opening (B038) — a real gap between what the rail offers and what this use-case needs | No real-time granular delivery-window API (stated) | Wants to prove logistics APIs are useful to agents | Delivery network capacity/scheduling | Household-specific urgency (a 30-min-before-cooking need) | Which orders to route through bulk vs. quick-commerce | Fulfill scheduled deliveries |
| **Gnani (voice rail)** | Adoption of voice API in a genuinely voice-first use-case | A use-case where ambient, multilingual capture is core, not decorative | Kitchen background noise + code-mixed dialect degrading accuracy (B039 — team's own finding) | Speech-to-text accuracy under noisy, multilingual, code-mixed conditions | Wants to prove voice-first works in a hard real-world setting | Voice models across languages/accents | Household-specific vocabulary (ingredient names, dish names) | N/A (infrastructure) | Processes voice input, returns transcription/intent |

**Explicit stakeholder conflicts:**
- Decision-maker wants autonomy handed to the agent (less daily effort); Pine Labs' actual rail behavior currently *requires* more manual intervention (2FA) precisely on the irregular, real-world purchases (loose vegetables) that are most common in Indian grocery shopping — a direct tension between the product's ambition and the payments rail's current limitation, and likely a strong candidate for Q5 (which rail to innovate on).
- The cook wants stable, unambiguous instructions; the decision-maker's preferences are stated to be contextual/temporal (B028), i.e., inherently unstable day to day — the system is asked to absorb this instability so it doesn't reach the cook as churn, which is a real design burden on the cook-facing subsystem.
- Other eaters want influence over decisions but have no low-friction way to exert it without becoming another coordination burden on the decision-maker — the very problem the product exists to remove.

---

*Pass 2 complete.*

---

## PASS 3 — RESEARCH

### 3.1 Systematic External Research — Key Findings

**Problem validation (India-specific, quantitative):**
- India's Time Use Survey (2019, NSO) found women spend roughly 299 minutes/day on unpaid domestic work versus roughly 97 minutes/day for men — a direct, government-sourced quantification of the gendered mental-load premise underlying the whole opening (source: Feminism in India, reporting NSO data).
- A qualitative study of food decision-making in rural Kerala found decisions are made weighing money, time, and effort against household needs, with food preferences of husband and children given more weight than health considerations, and women disproportionately bearing the burden of balancing everyone's expectations within available means (peer-reviewed, PMC). This independently corroborates B003/B028 (taste is a moving, multi-party target the decision-maker must arbitrate) and the "burden despite help" framing.
- UNEP's Food Waste Index Report (2021) estimates Indian households generate ~50 kg of food waste per capita per year (~68.76 million tonnes annually), with households responsible for 61% of all food waste globally. A 2023 interview-based study (Environmental Science and Pollution Research) attributes Indian household food waste specifically to miscalculation in meal preparation and inconsistent planning — directly supporting B001/B010/B013 as a real, evidenced, not merely assumed, problem.

**Competitor and alternative landscape:**
- A large, crowded global market already exists for "recipe from what's-in-your-fridge" apps (SuperCook, Cookly AI, FoodiePrep, Nutrola, Fridge Recipe AI, From Your Fridge, MyFridgeFood, BigOven, Pantry Pal, Whisk, ChatGPT-based cooking assistants). Common capabilities: photo/voice ingredient capture, expiry alerts, macro/dietary filtering, consolidated shopping lists. **None of these were found to include a cook-facing communication layer, a household-multi-eater preference-arbitration model, or integration with India-specific quick-commerce/payments/logistics rails.** This validates the team's own rejection of "just a recipe app" (B021) as a real, not merely assumed, differentiation — the category is saturated exactly where the team said not to compete, and empty exactly where the team proposes to build.
- India's quick-commerce apps (Blinkit, Zepto, Swiggy Instamart) already surface **"your usuals"** on the home screen based on individual order history, and this single feature reportedly roughly doubles repeat-order frequency for the operators using it (industry source, 2026). **This means simple habit-based reordering (B025, "agent orders milk") is not novel** — the incumbents already do a version of it at the individual-account level. The team's differentiation has to be the *household*-level, multi-person, cook-mediated layer sitting above this, not the reorder mechanic itself.
- No direct competitor was found operating as a cook-facing orchestration agent (i.e., nothing found treats "communicate with a domestic cook, in their language, on the household's behalf" as a product surface) — domestic-help apps found (Bookmybai, Maidvy, Broomees, Domestic App) are all *hiring/staffing* marketplaces, not *coordination* tools for an already-employed cook. This is a genuine, evidenced white space.

**Rail feasibility — direct evidence, including where it *contradicts* the brainstorm's own assumptions:**
- **Pine Labs / payments:** P3P is live (launched June 2026) and built on UPI's existing Single Block Multiple Debit (SBMD) and One-Time Mandate / Reserve Pay frameworks — a consumer reserves a ceiling once, and the agent can execute variable-value debits against that ceiling without further authentication, with Grantex handling identity/spend-limit/audit. **This directly contradicts B037's claim that "micro-authorizations for variable cart values (loose vegetables priced by weight) trigger fraud alerts / 2FA."** SBMD is architecturally designed to "block now, debit on event" for exactly this kind of variable, event-triggered spend. This needs to be re-tested rather than assumed in Pass 4 — the team's own rail-feasibility note may be stale relative to what P3P actually now supports, and if so, the "where it breaks" story for payments needs to be rewritten around a different, real limitation (e.g., Grantex's spend-limit UX for *household*, not individual, budgets — see Research Question Bank below).
- **Delhivery / logistics:** Delhivery Maps (launched June 2026) is a **geospatial/address-intelligence API suite** (geocoding, reverse geocoding, address validation/standardisation, vehicle-aware routing, distance/ETA, map tiles) built on Delhivery's own shipment telemetry — **not** a bulk/scheduled staple-delivery product as the brainstorm assumed (B038 describes "24–48 hour delivery of bulky staples," which is not what the opened rail actually is). This is a significant correction: the actual capability on offer is *location intelligence*, which could plausibly serve very different roles in this product — e.g., validating a delivery address before a quick-commerce order is placed, computing a realistic ETA against a tight pre-cooking window, or identifying the nearest kirana/shop for a B008-style "buy it yourself" fallback — rather than "bulk staple logistics," which the team's own brainstorm already called "kinda useless" for this opening (B038). This rail's actual role needs to be redefined entirely in Pass 4, not merely refined.
- **Gnani / voice:** Gnani's noise-robustness and code-mixed/Hinglish claims (14M+ hours of training audio, #1 on 8 of 9 Indian languages on the Kathbath Noisy benchmark) are specifically validated on **telephony-grade (8kHz, PSTN/VoIP) audio** — i.e., call-center and phone-line conditions. **It is not established from public material whether this generalizes to near-field, in-room kitchen ambient noise** (pressure cooker whistles, running exhaust fans, TV) captured via a phone mic rather than a telephony channel — a materially different acoustic profile. This is a genuine open research question, not a confirmed capability or a confirmed limitation — B039's claim that kitchen noise "leads to high speech-to-text error rates" is plausible but currently unverified against Gnani's actual benchmarks one way or the other, and should be tested directly (a real audio sample from a real kitchen, run through the actual API) rather than asserted in the submission.

**Anti-confirmation-bias findings (deliberately searching against the team's assumptions):**
- Trust in AI agents for shopping in India is measured as very high in aggregate (Accenture's 2026 Consumer Pulse Survey: 94% of Indian respondents want to shop inside gen-AI tools, 90% say they trust an AI agent's purchase recommendation over a best friend's) — this is genuinely good news for the core premise of an autonomous procurement agent, and pushes back against an assumption the team itself seemed unsure of (B032's trust questions read as if the team expected resistance).
- However, a separate 2026 cross-market study (Canva/Harris Poll) found 58% of consumers, India included, do *not* want a brand/AI **anticipating** their needs before they've expressed them, and a related report found 22% describe such anticipatory personalisation as "creepy" rather than merely intrusive. **This is a real tension the brainstorm does not address:** B025 (agent autonomously reorders milk "taking into account expiry," with no mention of asking first) is exactly the anticipatory-action pattern this research finds a meaningful share of Indian consumers actively dislike, even in a market that otherwise shows very high general AI trust. The distinction likely to matter in practice is *between* "the agent noticed and asks" and "the agent noticed and acted" — B030's green/yellow/red tiering already gestures at this distinction but the corpus doesn't explicitly connect it to this specific trust research.
- No evidence was found (in this pass) that existing meal-planning apps have failed specifically *because* they lack persistent household-level memory, as the team's framing paragraph asserts as established fact. The team's framing states this as a settled premise ("every workaround already tried in that shape has failed to stick"); external research in this pass did not turn up churn data on Indian meal-planning-app usage specifically, so this remains an **ASSUMPTION**, not a confirmed **FACT**, and is flagged in the Assumption Register below as a real risk: if this premise is wrong (i.e., if the actual failure mode of past attempts was something else — poor recipe relevance, no cook integration, price — rather than absence of memory), the product's central bet may be aimed at the wrong root cause. This is the single most important unresolved research gap in this pass and is a strong candidate for the team's own primary-research interviews (submission Q2) to close directly, since it cannot be resolved by desk research alone.

---

### 3.2 Anti-Confirmation-Bias Research — Summary Judgment

Per the above: the team's assumptions survive research reasonably well on the *problem* side (food waste and gendered mental load are independently, quantitatively evidenced) but survive less well on the *rail-feasibility* side, where two of three rail-specific claims in the brainstorm (Pine Labs' actual breaking point, Delhivery's actual product surface) appear to be based on outdated or incorrect assumptions about what the rails currently do, and the third (Gnani) is unverified either way. The team should not treat B037/B038 as settled feasibility findings when drafting Q4/Q5 — they should be explicitly re-tested against the live rail documentation before submission.

---

### 3.3 Research Methodology Note

For each question pursued: defined precisely, searched with multiple independent phrasings, cross-checked across source types (press releases, independent trade press, academic/peer-reviewed sources, official rail documentation), and — where a finding contradicted the team's own brainstorm — flagged explicitly rather than smoothed over (see 3.1 rail feasibility findings above). Limitations: searches were desk research only, conducted in one session; no primary interviews were run by this process (that remains the team's job for submission Q2, and is exactly the gap desk research cannot close — see the "most important unresolved research gap" note above). Recency: rail-partner findings are current as of their respective 2026 launch announcements; academic sources (Kerala food-decision study, food-waste study) are peer-reviewed but predate 2026 and should be read as background evidence of a durable pattern, not as commentary on any 2026-specific product.

---

### 3.4 Research Question Bank

| # | Question | Category | Status |
|---|---|---|---|
| RQ1 | Do real Indian households with a cook actually lack persistent shared memory today, or do informal tools (a shared notes app, a recurring WhatsApp pin, a physical notebook) already serve this function adequately? | Problem validation | **Open** — desk research found no data either way; requires the team's own interviews |
| RQ2 | What specifically caused prior meal-planning app attempts in these households to fail — no cook integration, poor recipe relevance, price, or absence of memory (the team's assumed cause)? | Problem validation | **Open** — same as RQ1, highest-priority interview question |
| RQ3 | How do multiple eaters' conflicting preferences actually get resolved today when they disagree — deferred to whoever's loudest, to the decision-maker's judgment, to the cook's default? | User behaviour | **Open** |
| RQ4 | Does Pine Labs' SBMD/OTM mandate structure, as actually implemented, support variable per-item pricing (loose produce) within a single household-level reserved ceiling, or does the fraud/2FA friction the team described still occur in practice at the point of a live quick-commerce checkout? | Technical feasibility (payments) | **Partially answered** — architecture supports it in principle (3.1); real checkout behaviour not confirmed, worth testing in Pine Labs' sandbox directly |
| RQ5 | What is Grantex's actual UX for setting and adjusting a *household* (not individual) spend mandate, and does it support the tiered green/yellow/red approval model the team envisions (B030)? | Technical feasibility (payments) | **Open** |
| RQ6 | Can Delhivery Maps' address-validation/ETA/routing capability be used to (a) improve quick-commerce delivery-window reliability for a tight pre-cooking need, or (b) locate the nearest suitable kirana/shop for a manual-purchase fallback (B008)? | Technical feasibility (logistics) | **Open** — now the central logistics question, replacing the original (incorrect) bulk-staples framing |
| RQ7 | Does Gnani's transcription accuracy on real, ambient (non-telephony) kitchen audio — pressure cooker, exhaust fan, TV — hold up to the same standard as its published telephony benchmarks? | AI feasibility (voice) | **Open** — requires a direct test with real audio, not inferable from public benchmarks |
| RQ8 | Where does the "anticipatory action vs. ask-first" line actually sit for this specific household — is a routine reorder (milk) still acceptable to act on autonomously, or does the Canva/Harris "creepy" finding (3.1) apply even to low-stakes routine items? | Trust / UX | **Open** — directly shapes the design of B030's "green" tier |
| RQ9 | What annexation use-case (submission Q7) is actually defensible given that quick-commerce incumbents already own "your usuals" reordering at the individual level — does the household/cook layer proposed here extend naturally into an adjacent use-case they don't already own? | Differentiation / judging strategy | **Open** |
| RQ10 | Which existing Indian company (grocery, delivery, payments, household commerce, appliances, consumer platforms — B033) has the closest existing users+data+payment relationship, and what specifically has stopped them from building this (submission Q9)? | Competitive / judging strategy | **Partially answered** — see Pass 4 candidate answer, pending final team decision |

---

### 3.5 Competitor and Alternative Analysis

| Competitor/alternative | What it actually solves | What it fails to solve | Why the gap exists | Where the opportunity lies | Is the team's differentiation defensible? |
|---|---|---|---|---|---|
| Ingredient-to-recipe AI apps (SuperCook, Cookly AI, FoodiePrep, Nutrola, etc.) | Generates a dish idea from listed/photographed ingredients; some track expiry and build shopping lists | No cook-facing interface; no household multi-eater arbitration; no India-specific rail integration; treats each session as independent (no accumulating household memory) | Built for a single-user, global, self-cooking market — the underlying assumption is "you cook for yourself," not "you decide, someone else cooks" | The team's cook-mediated, memory-persistent layer is genuinely absent from this category | Yes, but only if the cook-facing subsystem is actually built and central — if the MVP quietly becomes "another recipe generator," the differentiation evaporates |
| Quick-commerce apps' own "your usuals" reorder feature (Blinkit, Zepto, Instamart) | Individual-level habit-based reordering, already shipped and reportedly effective at doubling repeat orders | Doesn't reason about *why* an item is needed at a household level (which dish it's for, whose preference, cook capability); doesn't coordinate with a cook; is platform-locked (single app, not cross-app) | Their incentive is to keep the user on their own app, not to orchestrate cross-app or cross-person decisions | A household-level layer that sits above and can call into these apps, rather than replacing them | Partially — this is the most direct incumbent threat, since they already have the users, data and payment relationship (see B033) and could plausibly extend "usuals" toward a full household layer themselves |
| Domestic-help hiring platforms (Bookmybai, Maidvy, Broomees, Domestic App) | Finding and hiring a cook/maid | Nothing for coordinating with a cook *already* in place | Their business model is placement, not ongoing coordination — different unit economics entirely | None directly, but a byproduct: these platforms could eventually be a distribution channel (an add-on for cooks placed through them) | Not competitive at all — adjacent, not overlapping |
| Manual coordination via WhatsApp/verbal check-in (the actual status quo) | Works, in the sense that meals do get made every day | No persistent memory, no aggregation, all the pain points the team identified | Not a product at all — it's the absence of one | This is the baseline the product must beat, not a competitor to out-feature | N/A |

### 3.6 Is AI Actually Necessary? (Per Capability)

| Proposed capability | Best implementation | Justification |
|---|---|---|
| Inventory tracking from photo/voice/text (B031) | LLM/vision call for extraction, deterministic storage after | Extraction from unstructured photo/voice needs a model; the resulting state is a plain database, not itself "AI" |
| Dish recommendation given constraints (B011) | Constraint satisfaction / optimization over a rules+preference model, with an LLM only for natural-language explanation | The *hard part* (per Pass 2's emergent insight) is arbitration across shifting, multi-party constraints — this is closer to a constraint-satisfaction/ranking problem than a generative one; an LLM call to explain the choice in natural language is a reasonable, but non-essential, layer on top |
| Preference/feedback capture over time (B012, B028) | LLM for parsing informal/voice feedback into structured preference deltas; deterministic model update after | Necessary because feedback arrives as unstructured natural language, not a form |
| Cook communication (B009, B026, B029) | LLM + voice model (Gnani) for register-appropriate, bidirectional dialogue | Genuinely requires language generation/understanding — this is the strongest, least substitutable AI use case in the whole system |
| Order classification green/yellow/red (B030) | Deterministic rules engine (price/amount/brand-availability thresholds), not an LLM | This is explicitly a rules/logic problem — using an LLM here would add cost and unpredictability without benefit; a clear case where the "just use AI everywhere" impulse should be resisted |
| Price/quality comparison across apps (B015, B020) | Deterministic retrieval + comparison logic (API calls, structured comparison) | No generative reasoning is needed to compare structured price data across a small number of known APIs |
| Budget-aware order consolidation (B020) | Optimization/deterministic logic over a spend model, with LLM only to summarize the decision back to the human | Core logic is a constrained-optimization problem, not a language problem |

**Verdict:** AI (specifically LLM/voice-model capability) is genuinely necessary for exactly three things: extracting structured state from unstructured multimodal input, arbitrating/explaining preference conflicts in natural language, and cook-facing dialogue. Everything else in the brainstorm (order classification, price comparison, budget math) is better served by deterministic logic — and claiming otherwise in the submission would actually hurt the Creativity/Feasibility scoring, since judges are explicitly primed to penalize AI-washing ("this is usually where AI-generated solutions fail," per the judging page itself).

### 3.7 Is an Agent Actually Necessary?

Testing the core loop (B022: decision → inventory → procurement → cook → consumption → next decision) against the official agent tests:

- **Genuine goal being pursued?** Yes — get an acceptable meal decided, sourced, and prepared today, within budget/time/taste constraints, without daily manual re-derivation.
- **Choosing between actions?** Yes — order vs. don't order, which app, which rail, ask the human vs. act autonomously (B030's tiering *is* this choice).
- **Multiple valid paths to the goal?** Yes — the same dish can be reached via different procurement combinations (in-stock only, top-up order, in-person purchase per B008) depending on time/budget/delivery-window state.
- **Environment changes over time, requiring response?** Yes — inventory depletes, prices/availability shift across apps, a guest arrives (B019), a dish spoils mid-cook (B018).
- **Feedback required to know if an action worked?** Yes — did the cook actually make the dish, was it eaten, was it liked (B012) — this isn't knowable until after the loop closes.
- **Iterative reasoning, not single-pass?** Yes — the loop is explicitly cyclical (B022), and B027 calls for variable, calendar-aware re-triggering.
- **Recovery from failure/error required?** Yes — B018 (mishap handling) and B008 (fallback to manual purchase) are both explicit recovery paths.
- **Would a deterministic workflow actually suffice?** No, not end-to-end — the *individual* steps within the loop (order classification, price comparison) are deterministic (per 3.6), but the *loop itself*, with its branching, environment-responsiveness, and feedback dependency, is not reducible to a fixed workflow.

**Verdict:** Genuine agency is justified for the system as a whole — this is correctly a single agent (not obviously multi-agent; there's one coherent goal and one continuous state, even though it talks to multiple parties) orchestrating a mix of deterministic tools and a smaller number of genuinely generative/reasoning steps. The team's own instinct (B021, "needs agency, not just a recipe app") holds up against the formal test, which strengthens rather than merely confirms the pitch.

---

*Pass 3 complete.*

---

## PASS 4 — ADVERSARIAL SYNTHESIS

### 4.1 Product Requirements (Traceable)

```
EVIDENCE → PROBLEM → USER NEED → REQUIREMENT → FEATURE → JUDGING CRITERION
```

| Category | Requirement | Traced from | Judging criterion served |
|---|---|---|---|
| Functional | Track inventory with expiry, updated from both procurement and post-cook consumption | B001/B010/B013 + food-waste evidence (3.1) | Thoroughness, Feasibility |
| Functional | Generate a small set of candidate dishes filtered by cook capability, time, budget | B004, B006, B007, B011 | Clarity |
| Functional | Capture informal, voice/text feedback and update a *dynamic* (not static) preference model | B012, B028 + Kerala study (3.1) | Evidence, Thoroughness |
| Functional | Communicate the final instruction to the cook in their register, bidirectionally | B009, B026, B029 | Creativity (this is the least-copied capability found in competitor research) |
| Intelligence | Arbitrate conflicting multi-eater preferences, not just rank single-user options | Pass 2 emergent insight; B012 | Creativity, Clarity |
| Data | Persistent per-household state: inventory, per-person preference/health profile, recent-dish history, cook capability model | B023, "no shared memory" (stated problem) | Thoroughness |
| UX | Tiered autonomy — routine actions execute, unusual ones ask (green/yellow/red) | B030, B032, Canva/Harris anti-anticipation finding (3.1) | Feasibility, Evidence |
| AI | LLM used only for: multimodal extraction, preference arbitration/explanation, cook dialogue — not for order classification or price math | 3.6 finding | Creativity (avoids "AI-washing" the judges are primed to penalize), Feasibility |
| Agent | Single agent, continuous state, event- and schedule-triggered | 3.7 finding; B022, B027 | Thoroughness |
| Tool | Gnani voice (cook interface), Delhivery Maps (address/ETA confidence), Pine Labs P3P/Grantex (tiered spend execution) | B037–B039 + rail-correction findings (3.1) | Feasibility |
| Memory | Loop-closing: post-cook consumption inference feeds next-day inventory and preference state automatically | Root Cause Thread 2 (Pass 2) | Thoroughness, the strongest differentiator vs. any competitor found |
| Safety/Trust | Never place a "red" (large/unusual) order without explicit approval; never surface family WhatsApp content beyond what's needed for the specific decision | B032; anti-anticipation trust finding (3.1) | Evidence, Feasibility |

### 4.2 The Solution

**Product definition:** A household orchestration agent that sits above (not in place of) existing execution tools — the cook, quick-commerce apps, payment rails — and owns the *decision and coordination* layer that currently lives, unrecorded, in one person's head.

**Target user:** the household decision-maker in a home with a distinct cook (chef, spouse, domestic help) — evidenced as disproportionately, though not exclusively, a woman managing this as unpaid, unrecorded labor (3.1).

**Core problem:** daily re-derivation of a four-way synthesis (inventory, shifting multi-party preference, cook capability, procurement gap) with no memory carried forward.

**Core insight (the reframe from Pass 2, evidenced further in Pass 3):** this is a **preference-arbitration system operating on a moving target**, not a recipe-recommendation system — the hard problem is deciding whose shifting preference wins today, not generating a candidate dish.

**Value proposition:** "I've decided, sourced, and briefed the cook — and I remembered what happened, so tomorrow starts from where today ended," not "here's a recipe idea."

**Workflow — six steps (final form, ≤15 words each, matches submission Q3):**
1. Trigger: daily scheduled check-in, or ad hoc — new guest, spoiled dish, low-stock alert.
2. Knows: inventory/expiry, per-person preferences/allergies, cook's skill, today's budget, recent-dish history.
3. Does: proposes 2–3 dishes, computes the ingredient gap, checks budget and delivery feasibility.
4. Deals with: messages the cook in their language/register; queries quick-commerce APIs for price/availability.
5. Asks human: only for yellow/red spend tiers, or when eaters' preferences genuinely conflict.
6. Done when: cook confirms meal made, eaters give quick feedback, inventory/preference memory updates.

**Features (MVP vs. future — see 4.6):** inventory capture (photo/voice), dynamic per-person preference model, cook-facing bidirectional voice/text interface, tiered procurement automation, post-cook memory update loop.

**RAG design:** Not a classic document-RAG use case — the "retrieval" here is structured state retrieval (inventory, preference history, past-dish log) rather than unstructured document search; a vector store is unnecessary overhead unless the household starts accumulating unstructured content (e.g., saved recipes, festival-specific notes) worth semantic search over — flagged as a future-scope decision, not an MVP requirement.

**Tools:** Gnani (cook voice interface), Delhivery Maps (address validation + deadline-aware delivery-confidence, once built — see Q5), Pine Labs P3P/Grantex (tiered spend execution), quick-commerce price/catalog APIs (assumed available, not confirmed — see Assumption Register).

### 4.3 Agent Architecture

| Component | Design | Why it exists / what it prevents |
|---|---|---|
| Goal | Get today's meal decided, sourced, and communicated to the cook, within budget/time/taste constraints, with tomorrow easier than today | Anchors every downstream decision to the stated success bar (B035) |
| State | Per-household: inventory+expiry, per-person preference/health profile, cook capability model, recent-dish history, budget ledger | Without persistent state, the system degrades into a stateless recipe generator — the exact failure mode the team explicitly rejects (B021) |
| Context | Current day/time, calendar (festival/occasion, B014), guest count (B019), recent feedback | Prevents stale, one-size-fits-all recommendations on days that are contextually different (B028) |
| Memory | Long-term (preference drift, dish history) + short-term (today's specific constraints, e.g., a guest just arrived) | Two different time-horizons genuinely need different update rules — long-term memory shouldn't be overwritten by a one-off event |
| Planning | Candidate-dish generation → gap calculation → procurement-path selection (order / manual-purchase fallback / already in stock) | Encodes B008's manual fallback as a legitimate planned action rather than an unexplained hedge (resolves the Pass 2 contradiction) |
| Reasoning approach | LLM for multimodal extraction, preference arbitration/explanation, and cook dialogue; deterministic rules/optimization for everything else (3.6) | Prevents AI-washing; keeps the parts judges can most easily distrust (spend math, classification) fully auditable |
| Tools available | Gnani (voice), Delhivery Maps (address/ETA), Pine Labs P3P/Grantex (payment), quick-commerce catalog/price APIs | Matches the official rail structure exactly, so the submission's Q4 answer is architecturally grounded, not just claimed |
| Tool-selection logic | Rule-gated: voice tool triggers on cook-facing messages only; payment tool triggers only after budget check passes; logistics tool triggers only when an order is being considered | Prevents unnecessary/unsafe tool calls (e.g., never calls the payment tool speculatively) |
| Feedback loop | Post-meal: cook confirmation + eater reaction → updates preference model and inventory | This is the single most load-bearing mechanism in the whole design — it's what makes tomorrow easier, per the value proposition itself |
| Verification mechanism | Before acting on a "green" routine order, checks current inventory state was updated within a recency window (else treat as stale and ask) | Prevents acting on stale inventory data silently |
| Reflection mechanism | Weekly summary of accepted/rejected dish proposals, surfaced to the decision-maker | Lets a human catch systemic drift (e.g., agent consistently misjudging cook's skill) before it compounds |
| Error recovery | On a mid-cook mishap (B018): agent offers a fast substitute using only current in-stock inventory, no new order | Matches the reactive-trigger need identified in Pass 2 (B018 vs. B027 tension) without requiring a full new planning cycle |
| Human-in-the-loop points | (1) yellow/red spend approval, (2) genuinely conflicting multi-eater preferences, (3) weekly reflection review | Directly answers the trust research (3.1) — routine acts autonomously, unusual/conflicting does not |
| Guardrails | Never a "red" order without explicit approval; never surfaces raw family WhatsApp content beyond the specific extracted instruction | Directly addresses B032's own flagged risk and the WhatsApp-privacy hidden connection found in Pass 2 |
| Termination conditions | A day's loop terminates once cook-confirmation + eater feedback are received, or a fixed timeout after which it flags itself as "unclosed" rather than assuming success | Prevents silently incomplete memory updates, which would quietly recreate the "no shared memory" problem the whole product exists to solve |

### 4.4 Full Traceability & Rejected Ideas

All 39 items trace to a surviving requirement/feature above **except**:

| Rejected/downgraded item | Reason | Might resurface as |
|---|---|---|
| B008 (manual shopping fallback) | Not rejected, but downgraded from "hedge" to a first-class planned action (see Planning row, 4.3) — resolves the Pass 2 contradiction rather than discarding the idea | Already incorporated — no further action needed |
| B014 (festival/occasion meals) | Single mention, underdeveloped — kept as a context input (4.3) but not built as a dedicated feature for MVP | v2: a proper festival/calendar-aware recommendation layer |
| B004 (modeling "what can the chef make" from data) | Flagged in Pass 2 as a hard cold-start problem; MVP treats this as a human-provided profile, not learned | v2: infer capability from accepted/rejected dish history over time |
| B038's original framing (bulk staple logistics via Delhivery) | Factually incorrect per Pass 3 — Delhivery Maps is not a staples-delivery product | Replaced entirely by the address/ETA-confidence use of the rail (Q5/Q6) |
| B033 (which company should have built this) | Not a feature — a research prompt, resolved into the Q9 draft answer below | N/A |

### 4.5 Adversarial Judge Simulation

| Criterion | Why it could score high | Why it could score low | Highest-impact fix |
|---|---|---|---|
| Evidence | Independent NSO/UNEP/Kerala-study corroboration exists | **No primary interviews have actually been conducted by the team yet** — this is the single biggest live risk to the whole submission, since Q2 is explicitly scored on real conversations, not desk research | Run at least 3–5 real interviews before Sept 10 and let one genuinely surprising finding reshape a specific design element, per the submission's own instructions |
| Creativity | Cook-facing agentic dialogue is genuinely uncrowded (3.1 competitor scan) | Could still read as "another AI meal planner" if the pitch leads with the recipe/recommendation layer instead of the cook-communication and memory layers | Lead the pitch with "runs the kitchen," not "suggests dinner" |
| Clarity | Six-step workflow is concrete and falsifiable | Rail answers (Q4/Q5) risk sounding vague if the team doesn't correct the Delhivery misunderstanding before submitting | Use the corrected Delhivery framing (address/ETA-confidence), not the original bulk-logistics framing |
| Feasibility | Rail-by-rail feasibility has now been checked against live documentation, not assumption | Gnani-in-kitchen-noise is genuinely unverified; if a judge asks "have you tested this," honesty here matters more than confidence | Actually run one real kitchen audio sample through Gnani's API before the finale, or explicitly flag it as an open validation step in the submission itself, per the ground-rules' emphasis on honest, authentic answers |
| Thoroughness | Full loop, including edge cases (mishap, guest, leftovers) is covered | MVP scope explicitly excludes cook-capability learning (B004) — a judge could call this incomplete | Frame the exclusion as a deliberate MVP boundary with a stated v2 path (4.4), not an oversight |

**Rejection test — "if I wanted to reject this project, what arguments would I use?"**
1. *"You have no evidence this is actually about memory rather than something else."* — Conceded as an open risk (3.1); mitigated only by running real interviews before submission.
2. *"Your rail analysis was wrong about two of three rails until you corrected it — how do we know the correction is right either?"* — Rebutted: corrections are grounded in the rails' own live documentation and launch announcements (3.1), not guesses; the team should cite these sources directly in the submission.
3. *"An incumbent (Swiggy/Blinkit) could build the household layer on top of their existing 'usuals' feature faster than you can."* — Acknowledged as a real threat (3.5); the defensible edge is the cook-facing subsystem and the incumbents' structural disincentive (see Q9) to reduce order volume by making home-cooking more efficient.
4. *"Green/yellow/red is not new — every fraud system has risk tiers."* — Conceded partially; the novelty claim should rest on applying the tiering to *household decision-making*, not payment fraud, which is the less-explored application.

---

## Required Output Artifacts (A–K)

**A. Brainstorm Matrix** — see Pass 1, §1.4 (39 items, IDs B001–B039).
**B. Idea Relationship Graph** — see Pass 2, §2.1.
**C. Judging Matrix** — see Pass 1, §1.3 and Pass 4, §4.1 (rightmost column).
**D. Research Question Bank** — see Pass 3, §3.4 (10 questions, open/partial status marked).
**E. Evidence Table** — see Pass 3, §3.1 (each claim marked with its source).
**F. Assumption Register:**

| Assumption | Evidence | Confidence | Consequence if wrong |
|---|---|---|---|
| Past meal-planning failures were specifically due to lack of memory | None found in desk research (3.1) | Low-medium | Product solves the wrong root cause; needs team's Q2 interviews to confirm/deny before finalizing pitch |
| Quick-commerce catalog/price APIs are accessible for cross-app comparison | Not confirmed (assumed from B015/B020) | Low | Price-comparison feature (B015) may be technically blocked; needs direct API-access check |
| Households in this target segment have a distinct cook role (not self-cooking) | Consistent throughout brainstorm, not independently verified | Medium | If wrong for a meaningful share of the target segment, cook-facing subsystem needs a "no cook" mode |
| Gnani's noise robustness generalizes from telephony to kitchen ambient audio | Unconfirmed (3.1, RQ7) | Low-medium | Voice-first cook interface may need a text fallback as primary, not backup |

**G. Competitor Matrix** — see Pass 3, §3.5.
**H. Requirement Traceability Matrix** — see Pass 4, §4.1 and §4.4.
**I. Agent Architecture** — see Pass 4, §4.3 (agent justified per §3.7).
**J. MVP Prioritization:**

| Feature | Value | Evidence | Judging impact | Complexity |
|---|---|---|---|---|
| Inventory capture + expiry tracking | High | Direct food-waste evidence (3.1) | Thoroughness | Low-medium |
| Dynamic per-person preference model | High | Kerala study + B028 | Evidence, Clarity | Medium |
| Cook-facing voice/text interface | Highest (core differentiator) | Competitor gap confirmed (3.5) | Creativity | High (depends on RQ7) |
| Tiered procurement automation (green/yellow/red) | High | Trust research (3.1) | Feasibility | Medium |
| Post-cook memory-update loop | Highest (closes the actual root cause) | Pass 2 root-cause thread 2 | Thoroughness | Medium-high |
| Cook-capability learning (B004) | Deferred | Cold-start problem (Pass 2) | — | High — excluded from MVP |
| Festival/calendar-aware layer (B014) | Deferred | Single mention only | — | Low, but low priority |

**K. How-We-Win Strategy:** Win on the combination the research actually supports — not "AI picks your dinner" (crowded, per 3.5) but "the agent runs the cook-facing side of your kitchen and remembers, so the decision-maker's actual burden — re-deriving everything daily — disappears." This is evidenced (NSO time-use data, Kerala study, food-waste index), differentiated (no competitor found bridges decision-maker↔cook↔rails together), and rail-grounded (corrected, not assumed, feasibility per rail). The single biggest thing standing between this and a strong submission is real primary evidence (Q2) — everything else in this Bible can be desk-derived, that cannot.

---

*Pass 4 complete. Full four-pass Project Bible is done. Draft answers to the actual 10-question Solution Assembly follow below — several (Q1, Q2, Q8, Q10) genuinely need your team's own input and can't be responsibly fabricated.*

---

## DRAFT SUBMISSION ANSWERS (Solution Assembly)

**Q1 (team/right-to-win):** *Needs your team's own info* — one line per member (name + closest personal connection to this pain) and the team-level "what do we have that others don't" (a specific cook/household you can access, something you've already done). I don't have your team members' names or personal connections — fill this in directly; don't let me guess at it.

**Q2 (one customer insight, 60 words, scored on real evidence):** *Cannot be responsibly drafted yet* — this must come from an actual conversation with a real decision-maker, cook, or both. Based on this Bible, the single highest-value question to go ask is RQ1/RQ2: "what actually happened to the last tool/system you tried for this, and why did it stop?" Whatever surprising answer you get there is your Q2 — write it after you have it, not before.

**Q3 (six-step agent, ≤15 words/step):** ready to use, from §4.2:
1. Daily scheduled check-in, or ad hoc — new guest, spoiled dish, low-stock alert.
2. Knows inventory/expiry, per-person preferences/allergies, cook's skill, today's budget, recent-dish history.
3. Proposes 2–3 dishes, computes the ingredient gap, checks budget and delivery feasibility.
4. Messages the cook in their language/register; queries quick-commerce APIs for price/availability.
5. Asks the human only for yellow/red spend tiers, or genuinely conflicting preferences.
6. Done when cook confirms the meal made, eaters give feedback, memory updates.

**Q4 (rail touches, one sentence each):**
- *Payments:* Pine Labs' P3P/Grantex lets the household set a spend ceiling once, so the agent executes routine reorders and pre-approved top-ups without repeated authentication.
- *Logistics:* Delhivery Maps validates delivery addresses and estimates real arrival time against the cook's actual start time, or locates the nearest shop for a manual-purchase fallback.
- *Voice:* Gnani lets the agent listen to and talk with the cook in their own language and register, inside the kitchen, without moving the workflow to text.

**Q5 (which rail to innovate on, 40 words):** Delhivery Maps gives ETA and routing, but no confidence score against a real deadline ("cook starts in 25 minutes"). The missing capability: deadline-aware delivery-confidence scoring, so the agent knows whether to order or fall back to manual purchase.

**Q6 (customer asset, 30 words):** The household's existing WhatsApp thread with the cook (or a dedicated line into it) — because that's the one channel already carrying real daily instructions and feedback today.

**Q7 (annexation, 30 words):** Whole-household monthly grocery/pantry budgeting, not just individual meals — it falls to this agent next because it already holds the consumption and spend data needed to allocate it.

**Q8 (opening you'd never hand to an assistant):** *Needs the full list of the sixteen openings* — I only have two (yours, and one unrelated one mentioned earlier by mistake). Pick from the actual list; I can help reason through the answer once you share it.

**Q9 (which Indian company should've built this, 60 words):** Swiggy — through Instamart and food delivery they already hold grocery-ordering history, payment relationships, and a read on household routines. They likely haven't built it because it cuts against their core incentive: an agent that makes home-cooking more efficient and less wasteful probably means *fewer* delivery orders, not more. Their model rewards outsourcing meals, not optimizing home cooking.

**Q10 (track):** *Your call* — Product Strategy suits this Bible's current depth (full flows, segment map, named wall) without needing working code; Product Build would require standing up at least the cook-voice interface against a real sandbox before Sept 10, which is tight given RQ7 is still unverified. Tell me which you're leaning toward and I can tailor the rest of the submission to that track's expectations.

---

The full Project Bible (all four passes) is saved to the file below. Given the deadline, I'd prioritize: **(1) real interviews for Q2 today, (2) the full list of 16 openings for Q8, (3) your team's info for Q1, (4) a track decision for Q10** — everything else above is ready to paste in with light editing.
