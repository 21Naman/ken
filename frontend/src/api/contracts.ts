export type OllamaStatus = "available" | "unavailable" | "model_unavailable" | "invalid_response";
export interface HealthResponse { status: "ok"; database: { status: "available" }; ollama: { status: OllamaStatus; model: string; detail: string | null }; scheduler: { status: "available" | "unavailable"; detail: string | null }; }
export interface Household { id: number; name: string; default_language: string; created_at: string; }
export interface Member { id: number; name: string; language: string; dietary_preferences: string[]; allergies: string[]; health_constraints: string[]; likes: string[]; dislikes: string[]; }
export interface CookProfile { id: number; name: string; language: string; skill_level: string; available_hours: string[]; confident_dishes: string[]; }
export interface Budget { id: number; monthly_limit: number; spent_amount: number; planned_amount: number; category_allocations: Record<string, number>; }
export interface InventoryLot { id: number; ingredient: string; quantity: number; unit: string; expiry_date: string | null; freshness: "fresh" | "expiring_soon" | "use_immediately"; storage_location: string; confirmed: boolean; expiry_status: string; }
export interface Leftover { id: number; dish_name: string; portions: number; expiry_date: string | null; storage_location: string; reuse_suggestions: string[]; expiry_status: string; }
export interface DishHistory { id: number; dish_name: string; served_on: string; accepted: boolean | null; rating: number | null; feedback: string | null; leftovers_portions: number; }
export interface Preference { id: number; signal: string; sentiment: string; context: string | null; confidence: number; expires_on: string | null; }
export interface MealLoop { id: number; trigger_type: string; context_note: string | null; status: string; }
export interface AuditEvent { id: number; meal_loop_id: number; event: string; detail: string; created_at: string; }
export interface Approval { id: number; meal_loop_id: number; action: string; tier: "green" | "yellow" | "red"; amount_inr: number; status: string; reason: string; }
export interface IngredientGap { ingredient: string; needed: number; available: number; shortfall: number; unit: string; substitution: string | null; }
export interface Recommendation { dish: string; score: number; prep_minutes: number; missing_ingredients: IngredientGap[]; procurement: { route: string; estimated_cost_inr: number; reason: string }; score_explanation: { expiry_use: string[]; leftover_use: string[]; novelty: string; gaps: number }; }
export interface PlanResponse { context: { servings: number; available_minutes: number; urgency: string }; recommendations: Recommendation[]; exclusions: Array<{ dish: string; reasons: string[] }>; }
export interface CaptureCandidate { ingredient: string; quantity: number; unit: string; expiry_date: string | null; freshness: "fresh" | "expiring_soon" | "use_immediately"; storage_location: string; readability_confidence: number; }
export interface Dish { id: number; name: string; ingredients: Array<{ name: string; quantity: number; unit: string }>; prep_minutes: number; servings: number; nutrition_notes: string[]; tags: string[]; cook_skill_required: string; }
export interface DiscoveredDish { name: string; ingredients: Array<{ name: string; quantity: number; unit: string }>; prep_minutes: number; servings: number; nutrition_notes: string[]; cook_skill_required: string; rationale: string; is_new: boolean; dish_id: number | null; missing_ingredients: IngredientGap[]; procurement: { route: string; estimated_cost_inr: number; items: Array<IngredientGap & { store: string | null; price_inr: number | null }>; reason: string }; }
export interface CapturePreview { source: "audio" | "image"; transcript: string | null; language: string | null; candidates: CaptureCandidate[]; requires_confirmation: boolean; fallback: string | null; warning: string | null; }
