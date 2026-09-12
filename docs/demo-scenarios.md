# Demo scenarios

Every scenario is deterministic and independently reloadable. On the dashboard,
open the **Demo scenario** selector, choose the named value below, then select
**Reset selected demo**. This replaces the local fixture data; it does not depend on
a committed database file. Start on **Today** and use **Plan routine dinner** where
called out below.

## 1. Expiry — `expiry_routine`

**Demonstrates:** near-expiry ingredients and leftovers drive a safe, transparent
recommendation and a completed green local task.

**Trigger:** select `expiry routine`, reset it, then click **Plan routine dinner**.

**Look for:** Vegetable Khichdi's **Why this score** explanation lists carrot under
expiry use. The agent timeline records `routine expiry`, an expiry-led khichdi plan,
a green `local task created`, and `completed` outcome capture. The fixture has
carrots and carrot sabzi due today; it is not merely displaying an expiry date.

## 2. Preference conflict — `preference_conflict`

**Demonstrates:** a safety constraint overrides a conflicting household taste, and
the decision remains visible for approval rather than being silently applied.

**Trigger:** select `preference conflict`, reset it, then click **Plan routine
dinner**.

**Look for:** Paneer Bhurji appears under **Excluded** with `allergen present:
paneer`. The timeline says paneer was excluded for allergy and shows a pending red
approval for an allergy-safe dinner. Rohan's paneer preference is present in the
fixture, but Asha's dairy/paneer safety constraint wins.

## 3. Guests — `guests`

**Demonstrates:** an unexpected guest-arrival trigger is represented as an explicit
agent-loop event.

**Trigger:** select `guests` and reset it. Planning is not needed to see the
trigger.

**Look for:** the timeline shows **Trigger: guest arrival**, state `triggered`, and
the audit event `triggered — guest_arrival`, with the context note that four guests
are arriving for dinner.

## 4. Mishap recovery — `cook_mishap`

**Demonstrates:** a cooking mishap follows the existing recovery path using viable
stock instead of starting a new external ordering flow.

**Trigger:** select `cook mishap`, reset it, then click **Plan routine dinner**.

**Look for:** Vegetable Khichdi has the `use stock` route. The timeline identifies
the cooking mishap, records `recovery plan`, `stocked alternative`, the khichdi
cook brief, and `recovery in progress`. The fixture makes paneer unusable and adds
stocked moong dal, so the recovery is actually feasible.

## 5. Feedback learning — `feedback_learning`

**Demonstrates:** a completed meal's feedback survives in memory and affects the
next deterministic ranking.

**Trigger:** select `feedback learning`, reset it, then click **Plan routine
dinner**.

**Look for:** the completed timeline's memory section lists `Paneer Bhurji — Too
heavy` and `Prefer light dinners after paneer felt too heavy`. The next plan shows
Vegetable Khichdi with its score. The fixture's persisted preference signal is the
input to the planner's light-dinner bonus, not a static explanatory label.

## 6. Budget constraint — `budget_constraint`

**Demonstrates:** the remaining budget changes procurement routing and makes the
over-cap choice visible for approval.

**Trigger:** select `budget constraint`, reset it, then click **Plan routine
dinner**.

**Look for:** Paneer Bhurji is a `manual purchase` costing ₹137, because the
fixture leaves only ₹90. Vegetable Khichdi's ₹88 moong-dal gap remains a
`simulated order`. The timeline shows the ₹137 paneer basket and a pending yellow
approval. This verifies a budget-driven route decision, not merely a displayed
budget amount.

## Review-first inventory capture

The **Inventory** view is shared by all scenarios. Typed inventory is always
available. Voice and photo uploads first produce editable review candidates; only
**Confirm capture** sends `confirmed: true` and changes inventory. When optional
Whisper, vision, Ollama, or the scheduler is unavailable, the dashboard displays a
local fallback and preserves the typed path.
