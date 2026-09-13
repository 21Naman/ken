import { FormEvent, useEffect, useState } from "react";
import { api } from "./api/client";
import type { Approval, AuditEvent, Budget, CapturePreview, CookBrief, CookProfile, Dish, DiscoveredDish, DishHistory, GoogleCalendarConnection, HealthResponse, Household, InventoryLot, Leftover, MealLoop, Member, PlanResponse, Preference, ZeptoCart, ZeptoStatus } from "./api/contracts";
import "./styles.css";

type Screen = "today" | "household" | "inventory" | "dishes" | "memory" | "approvals";
const split = (value: FormDataEntryValue | null) => String(value ?? "").split(",").map((x) => x.trim()).filter(Boolean);
const value = (form: FormData, name: string) => String(form.get(name) ?? "");

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [households, setHouseholds] = useState<Household[]>([]);
  const [householdId, setHouseholdId] = useState<number | null>(null);
  const [screen, setScreen] = useState<Screen>("today");
  const [members, setMembers] = useState<Member[]>([]);
  const [memberCalendars, setMemberCalendars] = useState<Record<number, GoogleCalendarConnection>>({});
  const [profile, setProfile] = useState<CookProfile | null>(null);
  const [budget, setBudget] = useState<Budget | null>(null);
  const [inventory, setInventory] = useState<InventoryLot[]>([]);
  const [leftovers, setLeftovers] = useState<Leftover[]>([]);
  const [history, setHistory] = useState<DishHistory[]>([]);
  const [preferences, setPreferences] = useState<Preference[]>([]);
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [loops, setLoops] = useState<MealLoop[]>([]);
  const [audit, setAudit] = useState<AuditEvent[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [dishes, setDishes] = useState<Dish[]>([]);
  const [zepto, setZepto] = useState<ZeptoStatus>({ connected: false, phone_number: null });
  const [message, setMessage] = useState("Loading local household memory…");

  const load = async (selected?: number | null) => {
    try {
      const [nextHealth, nextHouseholds] = await Promise.all([api.health(), api.households()]);
      setHealth(nextHealth); setHouseholds(nextHouseholds);
      const id = selected ?? householdId ?? nextHouseholds[0]?.id ?? null;
      setHouseholdId(id);
      if (id) {
        const [nextMembers, nextProfile, nextBudget, nextZepto, nextInventory, nextLeftovers, nextDishes, nextHistory, nextPreferences, nextLoops, nextAudit, nextApprovals] = await Promise.all([
          api.members(id), api.cookProfile(id), api.budget(id), api.zeptoStatus(id), api.inventory(id), api.leftovers(id), api.dishes(id), api.history(id), api.preferences(id), api.mealLoops(id), api.audit(id), api.approvals(id),
        ]);
        const calendars = await Promise.all(nextMembers.map(async (member) => [member.id, await api.googleCalendar(id, member.id)] as const));
        setMembers(nextMembers); setMemberCalendars(Object.fromEntries(calendars)); setProfile(nextProfile); setBudget(nextBudget); setZepto(nextZepto); setInventory(nextInventory); setLeftovers(nextLeftovers); setDishes(nextDishes); setHistory(nextHistory); setPreferences(nextPreferences); setLoops(nextLoops); setAudit(nextAudit); setApprovals(nextApprovals);
      }
      setMessage(id ? "Persistent household memory is loaded." : "Create a household to begin.");
    } catch { setMessage("The local backend is unavailable."); }
  };
  useEffect(() => { const params = new URLSearchParams(window.location.search); const connectionMessage = params.get("zepto_connection") === "success" ? "Zepto account connected." : params.get("zepto_error") ?? (params.get("calendar_connection") === "success" ? "Google Calendar connected. Choose the calendar for this member below." : params.get("calendar_error")); if (connectionMessage) window.history.replaceState({}, "", window.location.pathname); void load().then(() => { if (connectionMessage) setMessage(connectionMessage); }); }, []); // eslint-disable-line react-hooks/exhaustive-deps
  const current = households.find((item) => item.id === householdId);
  const refresh = () => void load(householdId);
  const createHousehold = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); const form = new FormData(event.currentTarget); const item = await api.createHousehold({ name: value(form, "name"), default_language: value(form, "language") || "English" }); event.currentTarget.reset(); await load(item.id); setScreen("household"); };
  const requireHousehold = () => householdId !== null;

  return <main>
    <p className="eyebrow">LOCAL-FIRST PROTOTYPE · PHASE 7</p><h1>Household Agent</h1>
    <p className="lede">Local household memory, deterministic meal workflows, and review-first voice or photo inventory capture.</p>
    <nav aria-label="Application pages">{(["today", "household", "inventory", "dishes", "memory", "approvals"] as Screen[]).map((item) => <button className={screen === item ? "nav active" : "nav"} key={item} onClick={() => setScreen(item)}>{item === "dishes" ? "Recipe Book" : item}</button>)}</nav>
    <section className="toolbar"><label>Household <select value={householdId ?? ""} onChange={(event) => void load(Number(event.target.value))}><option value="">Select</option>{households.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label></section>
    {!requireHousehold() && <section><h2>Create a household</h2><form onSubmit={(event) => void createHousehold(event)}><input name="name" placeholder="Household name" required /><input name="language" placeholder="Default language" defaultValue="English" /><button>Create household</button></form></section>}
    {screen === "today" && <Today health={health} householdId={householdId} zepto={zepto} plan={plan} loops={loops} audit={audit} approvals={approvals} history={history} preferences={preferences} onRefresh={refresh} onPlan={async () => { if (householdId) setPlan(await api.plan(householdId, { servings: 2, available_minutes: 45, guests: 0, urgency: "routine" })); }} />}
    {requireHousehold() && screen === "household" && <HouseholdPage household={current!} members={members} calendars={memberCalendars} zepto={zepto} profile={profile} budget={budget} onRefresh={refresh} />}
    {requireHousehold() && screen === "inventory" && <InventoryPage inventory={inventory} leftovers={leftovers} householdId={householdId!} onRefresh={refresh} />}
    {requireHousehold() && screen === "dishes" && <RecipeBook householdId={householdId!} dishes={dishes} onRefresh={refresh} />}
    {requireHousehold() && screen === "memory" && <MemoryPage history={history} preferences={preferences} householdId={householdId!} onRefresh={refresh} />}
    {requireHousehold() && screen === "approvals" && <section><h2>Approvals</h2><button onClick={() => void api.scheduledTrigger(householdId!).then(refresh)}>Run scheduled local trigger</button><ul>{approvals.map((item) => <li key={item.id}><strong>{item.action}</strong> · {item.tier} · ₹{item.amount_inr} · {item.status}<button className="quiet" onClick={() => void api.decideApproval(householdId!, item.id, true).then(refresh)}>Approve</button><button className="quiet" onClick={() => void api.decideApproval(householdId!, item.id, false).then(refresh)}>Reject</button></li>)}</ul></section>}
    <p role="status">{message}</p>
  </main>;
}

function Today({ health, householdId, zepto, plan, loops, audit, approvals, history, preferences, onRefresh, onPlan }: { health: HealthResponse | null; householdId: number | null; zepto: ZeptoStatus; plan: PlanResponse | null; loops: MealLoop[]; audit: AuditEvent[]; approvals: Approval[]; history: DishHistory[]; preferences: Preference[]; onRefresh: () => void; onPlan: () => Promise<void> }) {
  const [discovered, setDiscovered] = useState<DiscoveredDish[]>([]);
  const [discoveryMessage, setDiscoveryMessage] = useState("");
  const [isDiscovering, setIsDiscovering] = useState(false);
  const [zeptoCart, setZeptoCart] = useState<ZeptoCart | null>(null);
  const [zeptoMessage, setZeptoMessage] = useState("");
  const [isZeptoLoading, setIsZeptoLoading] = useState(false);
  const discover = async () => {
    if (!householdId) return;
    setIsDiscovering(true);
    setDiscoveryMessage("🤖 AI is scanning your fridge…");
    setDiscovered([]);
    try {
      const result = await api.discoverDishes(householdId);
      setDiscovered(result.dishes);
      setDiscoveryMessage(result.dishes.length ? "AI dishes found from your active inventory." : "No active inventory items are available to turn into dishes yet.");
    } catch (error) { setDiscoveryMessage(`Dish discovery failed: ${error instanceof Error ? error.message : "unknown error"}`); }
    finally { setIsDiscovering(false); }
  };
  const saveDiscovered = async (dish: DiscoveredDish) => {
    if (!householdId) return;
    await api.createDish(householdId, { name: dish.name, ingredients: dish.ingredients, prep_minutes: dish.prep_minutes, servings: dish.servings, nutrition_notes: dish.nutrition_notes, tags: [], cook_skill_required: dish.cook_skill_required });
    setDiscovered((items) => items.map((item) => item.name === dish.name ? { ...item, is_new: false } : item));
    setDiscoveryMessage("Saved to family's personal recipe book!");
    onRefresh();
    await onPlan();
  };
  const requestPurchaseApproval = async (dish: DiscoveredDish) => {
    if (!householdId) return;
    const result = await api.requestDiscoveryApproval(householdId, { name: dish.name, ingredients: dish.ingredients, servings: dish.servings });
    setDiscoveryMessage(result.status === "approval_requested" ? `Approval requested for missing ingredients${dish.procurement.estimated_cost_inr ? ` (estimated ₹${dish.procurement.estimated_cost_inr})` : ""}.` : "Everything for this dish is already in stock.");
    onRefresh();
  };
  const fillOnZepto = async (dish: DiscoveredDish) => {
    if (!householdId) return;
    if (!zepto.connected) {
      try { setZeptoMessage("Opening Zepto mobile OTP connection..."); window.location.assign((await api.zeptoConnect(householdId)).authorization_url); }
      catch (error) { setZeptoMessage(error instanceof Error ? error.message : "Could not start Zepto connection."); }
      return;
    }
    setIsZeptoLoading(true); setZeptoMessage("🛒 Searching Zepto and adding to cart...");
    try { setZeptoCart(await api.zeptoCart(householdId, { dish_name: dish.name, missing_ingredients: dish.missing_ingredients })); setZeptoMessage(""); }
    catch (error) { setZeptoMessage(error instanceof Error ? error.message : "Zepto cart update failed."); }
    finally { setIsZeptoLoading(false); }
  };
  const markDelivered = async () => { if (householdId && zeptoCart) { await api.zeptoSyncInventory(householdId, zeptoCart.items_added); setZeptoMessage("Delivered items were added to inventory."); onRefresh(); } };
  return <>
    <section aria-label="Service health"><h2>Runtime health</h2><p>SQLite: <strong>{health?.database.status ?? "checking"}</strong></p><p>Ollama / {health?.ollama.model ?? "qwen3:4b"}: <strong>{health?.ollama.status ?? "checking"}</strong></p>{health?.ollama.detail && <p className="detail">{health.ollama.detail}</p>}<p>Scheduler: <strong>{health?.scheduler.status ?? "checking"}</strong></p>{health?.scheduler.detail && <p className="detail">{health.scheduler.detail}</p>}<button onClick={onRefresh}>Refresh health</button></section>
    {householdId && <section aria-label="Decision explanation"><h2>Today's deterministic proposal</h2><p>Uses stored household state only; it creates no action or order.</p><button onClick={() => void onPlan()}>Plan routine dinner</button><button onClick={() => void discover()} disabled={isDiscovering} aria-busy={isDiscovering}>{isDiscovering ? "⏳ AI is thinking…" : "✨ Discover dishes from my fridge (AI)"}</button>{discoveryMessage && <p role="status">{discoveryMessage}</p>}{isDiscovering && <div className="loading-bar" aria-hidden="true"><div className="loading-bar-fill" /></div>}{discovered.map((dish) => <article className="decision" key={dish.name}><h3>{dish.name} {dish.is_new && <span className="status fresh">✨ New AI Recipe</span>}</h3><p>{dish.prep_minutes} min · {dish.servings} servings · {dish.cook_skill_required}</p><p>{dish.rationale}</p><p>Ingredients: {dish.ingredients.map((ingredient) => `${ingredient.name} (${ingredient.quantity} ${ingredient.unit})`).join(" · ")}</p><p><strong>Missing ingredients:</strong> {dish.missing_ingredients.length ? dish.missing_ingredients.map((gap) => `${gap.ingredient} (${gap.shortfall} ${gap.unit} needed)`).join(" · ") : "none — ready to cook"}</p><p><strong>Purchase estimate:</strong> ₹{dish.procurement.estimated_cost_inr} · {dish.procurement.route.replaceAll("_", " ")} · {dish.procurement.reason}</p>{dish.missing_ingredients.length > 0 && <><button onClick={() => void fillOnZepto(dish)} disabled={isZeptoLoading}>{isZeptoLoading ? "🛒 Searching Zepto and adding to cart..." : "⚡ Fill Missing on Zepto (10m delivery)"}</button><button onClick={() => void requestPurchaseApproval(dish)}>Request approval to buy missing ingredients</button></>}{dish.is_new ? <button onClick={() => void saveDiscovered(dish)}>Add to Family Recipe Book</button> : <p>Already in your family recipe book.</p>}</article>)}{zeptoMessage && <p role="status">{zeptoMessage}</p>}{zeptoCart && <article className="decision" aria-label="Zepto cart"><h3>Zepto cart · {zeptoCart.store}</h3><ul>{zeptoCart.items_added.map((item) => <li key={item.product_id}>{item.matched_product} — ₹{item.price_inr} × {item.quantity}</li>)}</ul><p><strong>Total: ₹{zeptoCart.total_amount_inr}</strong></p>{zeptoCart.payment_url && <a href={zeptoCart.payment_url}>💳 Pay via UPI / GPay</a>} <a href={zeptoCart.checkout_url} target="_blank" rel="noreferrer">🛍️ View Cart on Zepto</a> <button onClick={() => void markDelivered()}>✅ Delivered (Add to Inventory)</button></article>}{plan && <DecisionExplanation plan={plan} />}</section>}
    {householdId && <AgentTimeline loops={loops} audit={audit} approvals={approvals} history={history} preferences={preferences} />}
  </>;
}

function DecisionExplanation({ plan }: { plan: PlanResponse }) {
  return <div className="decision-list"><p className="detail">Context: {plan.context.servings} servings · {plan.context.available_minutes} minutes · {plan.context.urgency}</p>{plan.recommendations.map((item) => <article className="decision" key={item.dish}><h3>{item.dish} · score {item.score}</h3><p>{item.prep_minutes} min · route: {item.procurement.route.replaceAll("_", " ")} · ₹{item.procurement.estimated_cost_inr}</p><p><strong>Why this score:</strong> expiry use: {item.score_explanation.expiry_use.join(", ") || "none"}; leftovers: {item.score_explanation.leftover_use.join(", ") || "none"}; novelty: {item.score_explanation.novelty}; ingredient gaps: {item.score_explanation.gaps}.</p><p><strong>Gaps:</strong> {item.missing_ingredients.length ? item.missing_ingredients.map((gap) => `${gap.ingredient} (${gap.shortfall} ${gap.unit} short; ${gap.available}/${gap.needed} available/needed${gap.substitution ? `; substitute ${gap.substitution}` : ""})`).join(" · ") : "none"}</p><p><strong>Procurement rationale:</strong> {item.procurement.reason}</p></article>)}{plan.exclusions.length > 0 && <p><strong>Excluded:</strong> {plan.exclusions.map((item) => `${item.dish} (${item.reasons.join("; ")})`).join(" · ")}</p>}</div>;
}

function AgentTimeline({ loops, audit, approvals, history, preferences }: { loops: MealLoop[]; audit: AuditEvent[]; approvals: Approval[]; history: DishHistory[]; preferences: Preference[] }) {
  const auditedLoops = loops.filter((loop) => audit.some((event) => event.meal_loop_id === loop.id));
  return <section aria-label="Agent timeline"><h2>Agent timeline</h2><p>Workflow history from the audit trail. Decision and memory sections show the existing persisted records; no event is inferred.</p>{auditedLoops.length === 0 && <p>No audited workflow events yet.</p>}{auditedLoops.map((loop) => {
    const events = audit.filter((event) => event.meal_loop_id === loop.id);
    const approval = approvals.find((item) => item.meal_loop_id === loop.id);
    const tier = approval?.tier ?? (events.some((event) => event.event === "local_task_created") ? "green" : null);
    return <article className="timeline" aria-label={`Loop ${loop.id} timeline`} key={loop.id}><h3>Trigger: {loop.trigger_type.replaceAll("_", " ")}</h3><p>Current state: <strong>{loop.status.replaceAll("_", " ")}</strong>{loop.context_note ? ` · ${loop.context_note}` : ""}</p>{tier && <p><span className={`autonomy ${tier}`}>Autonomy: {tier}</span>{approval && ` · ${approval.status} — ${approval.action} · ₹${approval.amount_inr}`}</p>}<ol>{events.map((event) => <li className="timeline-event" key={event.id}><strong>{event.event.replaceAll("_", " ")}</strong><span> — {event.detail}</span></li>)}</ol>{approval && <p><strong>Approval state:</strong> {approval.status} · {approval.reason}</p>}{events.some((event) => event.event === "completed" || event.event === "recovered") && <div className="memory-change"><h4>Memory after outcome</h4><p>Meal records: {history.map((item) => `${item.dish_name}${item.feedback ? ` — ${item.feedback}` : ""}`).join(" · ") || "none"}</p><p>Preference signals: {preferences.map((item) => item.signal).join(" · ") || "none"}</p></div>}</article>;
  })}</section>;
}

function HouseholdPage({ household, members, calendars, zepto, profile, budget, onRefresh }: { household: Household; members: Member[]; calendars: Record<number, GoogleCalendarConnection>; zepto: ZeptoStatus; profile: CookProfile | null; budget: Budget | null; onRefresh: () => void }) {
  const [brief, setBrief] = useState<CookBrief | null>(null);
  const [briefError, setBriefError] = useState("");
  const saveHousehold = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); const form = new FormData(event.currentTarget); await api.updateHousehold(household.id, { name: value(form, "name"), default_language: value(form, "language") }); onRefresh(); };
  const addMember = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); const f = new FormData(event.currentTarget); await api.createMember(household.id, { name: value(f, "name"), language: value(f, "language") || "English", dietary_preferences: split(f.get("diet")), allergies: split(f.get("allergies")), health_constraints: [], likes: split(f.get("likes")), dislikes: split(f.get("dislikes")) }); event.currentTarget.reset(); onRefresh(); };
  const saveProfile = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); const f = new FormData(event.currentTarget); await api.putCookProfile(household.id, { name: value(f, "name"), language: value(f, "language"), skill_level: value(f, "skill"), available_hours: split(f.get("hours")), confident_dishes: split(f.get("dishes")) }); onRefresh(); };
  const saveBudget = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); const f = new FormData(event.currentTarget); await api.putBudget(household.id, { monthly_limit: Number(value(f, "limit")), spent_amount: Number(value(f, "spent")), planned_amount: Number(value(f, "planned")), category_allocations: {} }); onRefresh(); };
  const editMember = async (item: Member) => { const name = window.prompt("Member name", item.name); if (name) { await api.updateMember(household.id, item.id, { ...item, name }); onRefresh(); } };
  const makeBrief = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); try { setBriefError(""); setBrief(await api.cookBrief(household.id, value(new FormData(event.currentTarget), "plan-date") || new Date().toISOString().slice(0, 10))); } catch { setBriefError("Could not read the connected calendars. Ensure each member selected a calendar, then reconnect if necessary."); } };
  const connectZepto = async () => { try { const result = await api.zeptoConnect(household.id); window.location.assign(result.authorization_url); } catch (error) { setBriefError(error instanceof Error ? error.message : "Could not connect Zepto."); } };
  return <><section><h2>Household profile</h2><form onSubmit={(e) => void saveHousehold(e)}><input name="name" defaultValue={household.name} required /><input name="language" defaultValue={household.default_language} required /><button>Save household</button></form></section><section><h2>Zepto Quick Commerce</h2>{zepto.connected ? <p className="connected">Connected ({zepto.phone_number ?? "account linked"})</p> : <><p>Connect your Zepto account to search live dark-store inventory and fill recipe gaps.</p><button type="button" onClick={() => void connectZepto()}>Connect Zepto Account</button></>}</section><section><h2>Members</h2><ul>{members.map((item) => <li key={item.id}><strong>{item.name}</strong> · {item.language} · diet: {item.dietary_preferences.join(", ") || "—"} · allergies: {item.allergies.join(", ") || "none"}<CalendarControl householdId={household.id} member={item} connection={calendars[item.id]} onRefresh={onRefresh} /><button className="quiet" onClick={() => void editMember(item)}>Edit</button><button className="quiet" onClick={() => void api.deleteMember(household.id, item.id).then(onRefresh)}>Remove</button></li>)}</ul><form onSubmit={(e) => void addMember(e)}><input name="name" placeholder="Member name" required /><input name="language" placeholder="Language" /><input name="diet" placeholder="Diet, comma-separated" /><input name="allergies" placeholder="Allergies, comma-separated" /><input name="likes" placeholder="Likes, comma-separated" /><input name="dislikes" placeholder="Dislikes, comma-separated" /><button>Add member</button></form></section><section><h2>Calendar-aware cook brief</h2><p>Reads selected members’ event titles and times for this day, then asks the local model to make a cook plan. Reconnect each calendar once to grant this schedule-reading permission.</p><form onSubmit={(event) => void makeBrief(event)}><label>Meal date <input name="plan-date" type="date" defaultValue={new Date().toISOString().slice(0, 10)} /></label><button>Create cook brief from calendars</button></form>{briefError && <p role="alert">{briefError}</p>}{brief && <article className="cook-brief"><h3>Kitchen schedule · {brief.plan_date}</h3><p>{brief.summary}</p><ol>{brief.actions.map((item, index) => <li key={`${item.time}-${index}`}><strong>{item.time} · {item.meal}</strong> — {item.action} for {item.members.join(", ") || "the household"}. <em>Why: {item.reason}</em></li>)}</ol>{brief.questions.length > 0 && <p><strong>Need to confirm:</strong> {brief.questions.join(" · ")}</p>}<h4>Calendar events used</h4>{Object.entries(brief.events_read).map(([member, events]) => <p key={member}><strong>{member}:</strong> {events.length ? events.map((event) => `${event.title} (${event.start} – ${event.end})`).join(" · ") : "No events on this date"}</p>)}</article>}</section><section><h2>Cook profile</h2><form onSubmit={(e) => void saveProfile(e)}><input name="name" defaultValue={profile?.name ?? "Cook"} /><input name="language" defaultValue={profile?.language ?? "Hindi"} /><input name="skill" defaultValue={profile?.skill_level ?? "intermediate"} /><input name="hours" defaultValue={profile?.available_hours.join(", ") ?? ""} placeholder="Available hours" /><input name="dishes" defaultValue={profile?.confident_dishes.join(", ") ?? ""} placeholder="Confident dishes" /><button>Save cook profile</button></form></section><section><h2>Monthly budget</h2><form onSubmit={(e) => void saveBudget(e)}><input name="limit" type="number" min="0" defaultValue={budget?.monthly_limit ?? 0} /><input name="spent" type="number" min="0" defaultValue={budget?.spent_amount ?? 0} /><input name="planned" type="number" min="0" defaultValue={budget?.planned_amount ?? 0} /><button>Save budget</button></form></section></>;
}

function CalendarControl({ householdId, member, connection, onRefresh }: { householdId: number; member: Member; connection?: GoogleCalendarConnection; onRefresh: () => void }) {
  const [options, setOptions] = useState<Array<{ id: string; name: string; primary: boolean }>>([]);
  const [events, setEvents] = useState<Array<{ title: string; start: string; end: string }> | null>(null);
  const [error, setError] = useState("");
  const connect = async () => { try { setError(""); const result = await api.googleCalendarConnect(householdId, member.id); window.location.assign(result.authorization_url); } catch { setError("Google Calendar needs OAuth credentials in .env before it can be connected."); } };
  const choose = async () => { try { setError(""); setOptions(await api.googleCalendars(householdId, member.id)); } catch { setError("Could not load calendars. Reconnect this member's Google account and try again."); } };
  const save = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); const calendarId = value(new FormData(event.currentTarget), "calendar"); const selected = options.find((item) => item.id === calendarId); if (selected) { await api.selectGoogleCalendar(householdId, member.id, { calendar_id: selected.id, calendar_name: selected.name }); setOptions([]); onRefresh(); } };
  const showEvents = async () => { try { setError(""); const today = new Date(); const end = new Date(today); end.setDate(today.getDate() + 30); setEvents(await api.googleCalendarEvents(householdId, member.id, today.toISOString().slice(0, 10), end.toISOString().slice(0, 10))); } catch { setError("Could not read this calendar. Use Change calendar to select the calendar where you created the event, then reconnect if needed."); } };
  return <div className="calendar-control"><p><strong>Google Calendar:</strong> {connection?.connected ? <span className="connected">Connected · {connection.calendar_name ?? "Choose a calendar"} · {connection.email}</span> : "Not connected"}</p>{!connection?.connected ? <button type="button" className="quiet" onClick={() => void connect()}>Connect Google Calendar</button> : <><button type="button" className="quiet" onClick={() => void choose()}>{connection.calendar_id ? "Change calendar" : "Choose calendar"}</button><button type="button" className="quiet" onClick={() => void showEvents()}>Show next 30 days</button><button type="button" className="quiet" onClick={() => void api.disconnectGoogleCalendar(householdId, member.id).then(onRefresh)}>Disconnect</button></>}{options.length > 0 && <form onSubmit={(event) => void save(event)}><label>Calendar for {member.name}<select name="calendar" defaultValue={connection?.calendar_id ?? options.find((item) => item.primary)?.id ?? options[0].id}>{options.map((item) => <option value={item.id} key={item.id}>{item.name}{item.primary ? " (primary)" : ""}</option>)}</select></label><button>Save calendar</button></form>}{events && <p><strong>Events found:</strong> {events.length ? events.map((event) => `${event.title} (${event.start} – ${event.end})`).join(" · ") : "None in the next 30 days for this selected calendar."}</p>}{error && <p role="alert">{error}</p>}</div>;
}

function InventoryPage({ householdId, inventory: inventoryProp, leftovers: leftoversProp, onRefresh }: { householdId: number; inventory: InventoryLot[]; leftovers: Leftover[]; onRefresh: () => void }) {
  const [preview, setPreview] = useState<CapturePreview | null>(null);
  const [captureError, setCaptureError] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadLabel, setUploadLabel] = useState("");
  // Local copies for instant updates
  const [inventory, setInventory] = useState<InventoryLot[]>(inventoryProp);
  const [leftovers, setLeftovers] = useState<Leftover[]>(leftoversProp);
  // Keep local state in sync when parent refreshes
  useEffect(() => { setInventory(inventoryProp); }, [inventoryProp]);
  useEffect(() => { setLeftovers(leftoversProp); }, [leftoversProp]);

  const addInventory = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const newItem = await api.createInventory(householdId, { ingredient: value(f, "ingredient"), quantity: Number(value(f, "quantity")), unit: value(f, "unit"), expiry_date: value(f, "expiry") || null, freshness: value(f, "freshness") || "fresh", storage_location: value(f, "location"), confirmed: f.get("confirmed") === "on" });
    // Instant update — append to local list right away
    setInventory((prev) => [...prev, newItem]);
    e.currentTarget.reset();
    onRefresh();
  };

  const previewUpload = async (kind: "audio" | "image", file?: File) => {
    if (!file) return;
    setIsUploading(true);
    setUploadLabel(kind === "audio" ? "🎙️ Transcribing voice note…" : "📷 Analysing photo with AI…");
    setCaptureError("");
    setPreview(null);
    try {
      setPreview(kind === "audio" ? await api.previewAudio(householdId, file) : await api.previewImage(householdId, file));
    } catch { setCaptureError("Upload could not be previewed. Typed inventory remains available below."); }
    finally { setIsUploading(false); setUploadLabel(""); }
  };

  const confirmCandidate = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const newItem = await api.confirmCapture(householdId, { ingredient: value(f, "ingredient"), quantity: Number(value(f, "quantity")), unit: value(f, "unit"), expiry_date: value(f, "expiry") || null, freshness: value(f, "freshness") || "fresh", storage_location: value(f, "location") || "pantry", confirmed: true });
    // Instant update
    setInventory((prev) => [...prev, newItem]);
    setPreview(null);
    onRefresh();
  };

  const addLeftover = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const newLeftover = await api.createLeftover(householdId, { dish_name: value(f, "dish"), portions: Number(value(f, "portions")), expiry_date: value(f, "expiry") || null, storage_location: value(f, "location") || "fridge", reuse_suggestions: split(f.get("suggestions")) });
    setLeftovers((prev) => [...prev, newLeftover]);
    e.currentTarget.reset();
    onRefresh();
  };

  const editInventory = async (item: InventoryLot) => { const quantity = window.prompt(`Quantity of ${item.ingredient}`, String(item.quantity)); if (quantity !== null && !Number.isNaN(Number(quantity))) { await api.updateInventory(householdId, item.id, { ...item, quantity: Number(quantity) }); onRefresh(); } };
  const editLeftover = async (item: Leftover) => { const portions = window.prompt(`Portions of ${item.dish_name}`, String(item.portions)); if (portions !== null && !Number.isNaN(Number(portions))) { await api.updateLeftover(householdId, item.id, { ...item, portions: Number(portions) }); onRefresh(); } };

  return <><section><h2>Inventory</h2><ul>{inventory.map((item) => <li key={item.id}><strong>{item.ingredient}</strong> · {item.quantity} {item.unit} · <span className={`status ${item.expiry_status}`}>{item.expiry_status.replaceAll("_", " ")}</span> · {(item.freshness ?? "fresh").replaceAll("_", " ")} · {item.storage_location}<button className="quiet" onClick={() => void editInventory(item)}>Edit</button><button className="quiet" onClick={() => void api.deleteInventory(householdId, item.id).then(onRefresh)}>Remove</button></li>)}</ul><h3>Voice or photo capture</h3><p>Files are processed only by configured local models. Review every proposed field before saving.</p>{isUploading && <><p role="status" className="upload-status">{uploadLabel}</p><div className="loading-bar" aria-hidden="true"><div className="loading-bar-fill" /></div></>}<label>Voice note <input aria-label="Voice note" type="file" accept="audio/*" disabled={isUploading} onChange={(e) => void previewUpload("audio", e.currentTarget.files?.[0])} /></label><label>Fridge photo <input aria-label="Fridge photo" type="file" accept="image/*" disabled={isUploading} onChange={(e) => void previewUpload("image", e.currentTarget.files?.[0])} /></label>{captureError && <p role="alert">{captureError}</p>}{preview && <section aria-label="Capture review"><h3>Review capture</h3>{preview.transcript !== null && <><label>Editable transcript <textarea aria-label="Editable transcript" defaultValue={preview.transcript} /></label><p>{preview.language ? `Detected language: ${preview.language}` : "Transcript needs manual parsing."}</p></>}{preview.fallback && <p role="alert">{preview.fallback}</p>}{preview.warning && <p role="alert">{preview.warning}</p>}{preview.candidates.map((candidate, index) => <form key={`${candidate.ingredient}-${index}`} onSubmit={(e) => void confirmCandidate(e)}><input name="ingredient" aria-label="Ingredient" defaultValue={candidate.ingredient} required /><input name="quantity" aria-label="Quantity" type="number" min="0" step="any" defaultValue={candidate.quantity} required /><input name="unit" aria-label="Unit" defaultValue={candidate.unit} required /><select name="freshness" aria-label="Freshness" defaultValue={candidate.freshness || "fresh"}><FreshnessOptions /></select><input name="expiry" aria-label="Expiry" type="date" defaultValue={candidate.expiry_date ?? ""} /><input name="location" aria-label="Storage location" defaultValue={candidate.storage_location} /><span>readability confidence {Math.round(candidate.readability_confidence * 100)}%</span><button>Confirm capture</button></form>)}</section>}<h3>Typed inventory</h3><form onSubmit={(e) => void addInventory(e)}><input name="ingredient" placeholder="Ingredient" required /><input name="quantity" type="number" min="0" step="any" placeholder="Quantity" required /><input name="unit" placeholder="Unit" required /><select name="freshness" aria-label="Freshness" defaultValue="fresh"><FreshnessOptions /></select><input name="expiry" type="date" /><input name="location" placeholder="Storage location" defaultValue="pantry" /><label><input name="confirmed" type="checkbox" /> Confirmed</label><button>Add inventory</button></form></section><section><h2>Leftovers</h2><ul>{leftovers.map((item) => <li key={item.id}><strong>{item.dish_name}</strong> · {item.portions} portions · <span className={`status ${item.expiry_status}`}>{item.expiry_status.replaceAll("_", " ")}</span><button className="quiet" onClick={() => void editLeftover(item)}>Edit</button><button className="quiet" onClick={() => void api.deleteLeftover(householdId, item.id).then(onRefresh)}>Remove</button></li>)}</ul><form onSubmit={(e) => void addLeftover(e)}><input name="dish" placeholder="Dish" required /><input name="portions" type="number" min="0" step="any" placeholder="Portions" required /><input name="expiry" type="date" /><input name="location" defaultValue="fridge" /><input name="suggestions" placeholder="Reuse suggestions" /><button>Add leftover</button></form></section></>;
}

function FreshnessOptions() {
  return <><option value="fresh">Fresh (Good for a week)</option><option value="expiring_soon">Expiring Soon (Use in 2-3 days)</option><option value="use_immediately">Use Immediately (Expires today)</option></>;
}

function RecipeBook({ householdId, dishes, onRefresh }: { householdId: number; dishes: Dish[]; onRefresh: () => void }) {
  const addDish = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await api.createDish(householdId, {
      name: value(form, "name"),
      ingredients: split(form.get("ingredients")).map((name) => ({ name, quantity: 1, unit: "portion" })),
      prep_minutes: Number(value(form, "prep") || 0), servings: Number(value(form, "servings") || 1),
      nutrition_notes: split(form.get("notes")), tags: split(form.get("tags")), cook_skill_required: value(form, "skill") || "beginner",
    });
    event.currentTarget.reset(); onRefresh();
  };
  return <section><h2>Family Recipe Book</h2><p>Recipes saved here are permanent household memory and are available to deterministic dinner planning.</p><ul>{dishes.map((dish) => <li key={dish.id}><strong>{dish.name}</strong> · {dish.prep_minutes} min · {dish.servings} servings · {dish.ingredients.map((ingredient) => ingredient.name).join(", ")}<button className="quiet" onClick={() => void api.deleteDish(householdId, dish.id).then(onRefresh)}>Remove</button></li>)}</ul><h3>Add a family recipe</h3><form onSubmit={(event) => void addDish(event)}><input name="name" placeholder="Dish name" required /><input name="ingredients" placeholder="Ingredients, comma-separated" /><input name="prep" type="number" min="0" placeholder="Prep minutes" /><input name="servings" type="number" min="1" defaultValue="2" /><input name="notes" placeholder="Nutrition notes, comma-separated" /><input name="tags" placeholder="Tags, comma-separated" /><select name="skill" defaultValue="beginner"><option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option></select><button>Add recipe</button></form></section>;
}

function MemoryPage({ householdId, history, preferences, onRefresh }: { householdId: number; history: DishHistory[]; preferences: Preference[]; onRefresh: () => void }) {
  const addHistory = async (e: FormEvent<HTMLFormElement>) => { e.preventDefault(); const f = new FormData(e.currentTarget); await api.createHistory(householdId, { dish_name: value(f, "dish"), served_on: value(f, "served") || new Date().toISOString().slice(0, 10), accepted: f.get("accepted") === "yes", rating: value(f, "rating") ? Number(value(f, "rating")) : null, feedback: value(f, "feedback") || null, leftovers_portions: 0 }); e.currentTarget.reset(); onRefresh(); };
  const addPreference = async (e: FormEvent<HTMLFormElement>) => { e.preventDefault(); const f = new FormData(e.currentTarget); await api.createPreference(householdId, { signal: value(f, "signal"), sentiment: value(f, "sentiment") || "neutral", context: value(f, "context") || null, confidence: Number(value(f, "confidence") || 1), expires_on: value(f, "expires") || null }); e.currentTarget.reset(); onRefresh(); };
  const editHistory = async (item: DishHistory) => { const feedback = window.prompt("Feedback", item.feedback ?? ""); if (feedback !== null) { await api.updateHistory(householdId, item.id, { ...item, feedback, leftovers_portions: item.leftovers_portions }); onRefresh(); } };
  const editPreference = async (item: Preference) => { const signal = window.prompt("Preference signal", item.signal); if (signal) { await api.updatePreference(householdId, item.id, { ...item, signal }); onRefresh(); } };
  const reflect = async () => { const r = await api.reflection(householdId); window.alert(`Reflection: ${r.meals_recorded} meals; rating ${r.average_rating}. ${r.recent_feedback.join(" · ")}`); };
  return <><section><h2>Weekly reflection</h2><button onClick={() => void reflect()}>View reflection</button></section><section><h2>Meal history</h2><ul>{history.map((item) => <li key={item.id}><strong>{item.dish_name}</strong> · {item.served_on} · rating: {item.rating ?? "—"} · {item.feedback ?? "no feedback"}<button className="quiet" onClick={() => void editHistory(item)}>Edit</button><button className="quiet" onClick={() => void api.deleteHistory(householdId, item.id).then(onRefresh)}>Remove</button></li>)}</ul><form onSubmit={(e) => void addHistory(e)}><input name="dish" placeholder="Dish name" required /><input name="served" type="date" /><select name="accepted"><option value="yes">Accepted</option><option value="no">Not accepted</option></select><input name="rating" type="number" min="1" max="5" placeholder="Rating" /><input name="feedback" placeholder="Feedback" /><button>Add meal record</button></form></section><section><h2>Preference signals</h2><ul>{preferences.map((item) => <li key={item.id}><strong>{item.signal}</strong> · {item.sentiment} · confidence {item.confidence}<button className="quiet" onClick={() => void editPreference(item)}>Edit</button><button className="quiet" onClick={() => void api.deletePreference(householdId, item.id).then(onRefresh)}>Remove</button></li>)}</ul><form onSubmit={(e) => void addPreference(e)}><input name="signal" placeholder="Preference or feedback" required /><input name="sentiment" placeholder="Sentiment" defaultValue="neutral" /><input name="context" placeholder="Context" /><input name="confidence" type="number" min="0" max="1" step="0.1" defaultValue="1" /><input name="expires" type="date" /><button>Add signal</button></form></section></>;
}
