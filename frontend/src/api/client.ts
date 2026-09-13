import type { Approval, AuditEvent, Budget, CapturePreview, CookProfile, DiscoveredDish, Dish, DishHistory, HealthResponse, Household, InventoryLot, Leftover, MealLoop, Member, PlanResponse, Preference } from "./contracts";

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, { headers: { "Content-Type": "application/json", ...init?.headers }, ...init });
  if (!response.ok) {
    const payload = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(payload?.detail ?? `API request failed (${response.status})`);
  }
  return response.status === 204 ? undefined as T : response.json() as Promise<T>;
}
const householdPath = (id: number) => `/api/households/${id}`;
async function upload<T>(path: string, field: string, file: File): Promise<T> {
  const body = new FormData(); body.append(field, file);
  const response = await fetch(`${baseUrl}${path}`, { method: "POST", body });
  if (!response.ok) throw new Error(`Upload failed (${response.status})`);
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthResponse>("/api/health"),
  households: () => request<Household[]>("/api/households"), createHousehold: (body: object) => request<Household>("/api/households", { method: "POST", body: JSON.stringify(body) }), updateHousehold: (id: number, body: object) => request<Household>(householdPath(id), { method: "PUT", body: JSON.stringify(body) }),
  members: (id: number) => request<Member[]>(`${householdPath(id)}/members`), createMember: (id: number, body: object) => request<Member>(`${householdPath(id)}/members`, { method: "POST", body: JSON.stringify(body) }), updateMember: (id: number, item: number, body: object) => request<Member>(`${householdPath(id)}/members/${item}`, { method: "PUT", body: JSON.stringify(body) }), deleteMember: (id: number, item: number) => request<void>(`${householdPath(id)}/members/${item}`, { method: "DELETE" }),
  cookProfile: (id: number) => request<CookProfile | null>(`${householdPath(id)}/cook-profile`), putCookProfile: (id: number, body: object) => request<CookProfile>(`${householdPath(id)}/cook-profile`, { method: "PUT", body: JSON.stringify(body) }),
  budget: (id: number) => request<Budget | null>(`${householdPath(id)}/budget`), putBudget: (id: number, body: object) => request<Budget>(`${householdPath(id)}/budget`, { method: "PUT", body: JSON.stringify(body) }),
  inventory: (id: number) => request<InventoryLot[]>(`${householdPath(id)}/inventory`), createInventory: (id: number, body: object) => request<InventoryLot>(`${householdPath(id)}/inventory`, { method: "POST", body: JSON.stringify(body) }), updateInventory: (id: number, item: number, body: object) => request<InventoryLot>(`${householdPath(id)}/inventory/${item}`, { method: "PUT", body: JSON.stringify(body) }), deleteInventory: (id: number, item: number) => request<void>(`${householdPath(id)}/inventory/${item}`, { method: "DELETE" }),
  dishes: (id: number) => request<Dish[]>(`${householdPath(id)}/dishes`), createDish: (id: number, body: object) => request<Dish>(`${householdPath(id)}/dishes`, { method: "POST", body: JSON.stringify(body) }), deleteDish: (id: number, item: number) => request<void>(`${householdPath(id)}/dishes/${item}`, { method: "DELETE" }), discoverDishes: (id: number) => request<{ dishes: DiscoveredDish[] }>(`${householdPath(id)}/discover-dishes`, { method: "POST" }),
  requestDiscoveryApproval: (id: number, body: object) => request<{ status: string; approval_id: number | null }>(`${householdPath(id)}/discover-dishes/approval`, { method: "POST", body: JSON.stringify(body) }),
  previewAudio: (id: number, file: File) => upload<CapturePreview>(`${householdPath(id)}/capture/audio`, "audio", file), previewImage: (id: number, file: File) => upload<CapturePreview>(`${householdPath(id)}/capture/image`, "image", file), confirmCapture: (id: number, body: object) => request<InventoryLot>(`${householdPath(id)}/capture/confirm`, { method: "POST", body: JSON.stringify(body) }),
  leftovers: (id: number) => request<Leftover[]>(`${householdPath(id)}/leftovers`), createLeftover: (id: number, body: object) => request<Leftover>(`${householdPath(id)}/leftovers`, { method: "POST", body: JSON.stringify(body) }), updateLeftover: (id: number, item: number, body: object) => request<Leftover>(`${householdPath(id)}/leftovers/${item}`, { method: "PUT", body: JSON.stringify(body) }), deleteLeftover: (id: number, item: number) => request<void>(`${householdPath(id)}/leftovers/${item}`, { method: "DELETE" }),
  history: (id: number) => request<DishHistory[]>(`${householdPath(id)}/history`), createHistory: (id: number, body: object) => request<DishHistory>(`${householdPath(id)}/history`, { method: "POST", body: JSON.stringify(body) }), updateHistory: (id: number, item: number, body: object) => request<DishHistory>(`${householdPath(id)}/history/${item}`, { method: "PUT", body: JSON.stringify(body) }), deleteHistory: (id: number, item: number) => request<void>(`${householdPath(id)}/history/${item}`, { method: "DELETE" }),
  preferences: (id: number) => request<Preference[]>(`${householdPath(id)}/preferences`), createPreference: (id: number, body: object) => request<Preference>(`${householdPath(id)}/preferences`, { method: "POST", body: JSON.stringify(body) }), updatePreference: (id: number, item: number, body: object) => request<Preference>(`${householdPath(id)}/preferences/${item}`, { method: "PUT", body: JSON.stringify(body) }), deletePreference: (id: number, item: number) => request<void>(`${householdPath(id)}/preferences/${item}`, { method: "DELETE" }),
  plan: (id: number, body: object) => request<PlanResponse>(`${householdPath(id)}/plan`, { method: "POST", body: JSON.stringify(body) }),
  mealLoops: (id: number) => request<MealLoop[]>(`${householdPath(id)}/meal-loops`), audit: (id: number) => request<AuditEvent[]>(`${householdPath(id)}/audit`),
  approvals: (id: number) => request<Approval[]>(`${householdPath(id)}/approvals`),
  decideApproval: (id: number, approval: number, approved: boolean) => request(`${householdPath(id)}/approvals/${approval}/decision`, { method: "POST", body: JSON.stringify({ approved }) }),
  startLoop: (id: number) => request<{ id: number }>(`${householdPath(id)}/loops`, { method: "POST", body: JSON.stringify({ trigger_type: "manual" }) }),
  scheduledTrigger: (id: number) => request(`${householdPath(id)}/scheduled-trigger`, { method: "POST" }),
  reflection: (id: number) => request<{ meals_recorded: number; average_rating: number; recent_feedback: string[]; preference_signals: string[] }>(`${householdPath(id)}/reflection`),
  outcome: (id: number, loop: number, body: object) => request(`${householdPath(id)}/loops/${loop}/outcome`, { method: "POST", body: JSON.stringify(body) }),
};
