from dataclasses import dataclass
from datetime import date
from typing import Any


SKILL_RANK = {"beginner": 0, "intermediate": 1, "advanced": 2}
SUBSTITUTIONS = {"paneer": "firm tofu", "tomato": "canned tomato", "moong dal": "masoor dal"}
# Local fallback pack estimates keep discovery useful when a household has not
# loaded a store catalogue. They are only estimates; no purchase is performed.
LOCAL_PRICE_ESTIMATES = {
    "eggs": {"store_name": "Local estimate", "price_inr": 48, "unit": "dozen"},
    "egg": {"store_name": "Local estimate", "price_inr": 48, "unit": "dozen"},
    "yeast": {"store_name": "Local estimate", "price_inr": 25, "unit": "packet"},
    "baking powder": {"store_name": "Local estimate", "price_inr": 35, "unit": "packet"},
    "pizza dough": {"store_name": "Local estimate", "price_inr": 70, "unit": "piece"},
    "mozzarella cheese": {"store_name": "Local estimate", "price_inr": 120, "unit": "200 g"},
    "cheese": {"store_name": "Local estimate", "price_inr": 120, "unit": "200 g"},
    "tomato sauce": {"store_name": "Local estimate", "price_inr": 60, "unit": "200 g"},
    "butter": {"store_name": "Local estimate", "price_inr": 55, "unit": "100 g"},
    "milk": {"store_name": "Local estimate", "price_inr": 30, "unit": "500 ml"},
    "bread": {"store_name": "Local estimate", "price_inr": 40, "unit": "packet"},
    "oil": {"store_name": "Local estimate", "price_inr": 150, "unit": "1 l"},
    "olive oil": {"store_name": "Local estimate", "price_inr": 250, "unit": "500 ml"},
    "oregano": {"store_name": "Local estimate", "price_inr": 30, "unit": "packet"},
    "flour": {"store_name": "Local estimate", "price_inr": 45, "unit": "1 kg"},
    "rice": {"store_name": "Local estimate", "price_inr": 60, "unit": "1 kg"},
    "dal": {"store_name": "Local estimate", "price_inr": 80, "unit": "500 g"},
    "salt": {"store_name": "Local estimate", "price_inr": 20, "unit": "1 kg"},
    "sugar": {"store_name": "Local estimate", "price_inr": 45, "unit": "1 kg"},
    "onion": {"store_name": "Local estimate", "price_inr": 35, "unit": "1 kg"},
    "potato": {"store_name": "Local estimate", "price_inr": 30, "unit": "1 kg"},
    "tomato": {"store_name": "Local estimate", "price_inr": 40, "unit": "1 kg"},
    "garlic": {"store_name": "Local estimate", "price_inr": 30, "unit": "100 g"},
    "ginger": {"store_name": "Local estimate", "price_inr": 25, "unit": "100 g"},
}


@dataclass(frozen=True)
class PlanInput:
    servings: int
    available_minutes: int
    today: date
    inventory: list[dict[str, Any]]
    leftovers: list[dict[str, Any]]
    members: list[dict[str, Any]]
    cook_skill: str
    budget_remaining: float
    recent_dishes: list[str]
    preferences: list[str]
    stores: list[dict[str, Any]]


def _normal_ingredient_name(name: str) -> str:
    cleaned = name.strip().casefold()
    aliases = {
        "tomatoes": "tomato",
        "eggs": "egg",
        "potatoes": "potato",
        "onions": "onion",
        "carrots": "carrot",
        "chillies": "chilli",
        "green chillies": "green chilli",
        "cheeses": "cheese",
        "flours": "flour",
        "all purpose flour": "flour",
        "all-purpose flour": "flour",
        "maida": "flour",
        "atta": "flour",
        "whole wheat flour": "flour",
        "wheat flour": "flour",
        "pizza sauce": "tomato sauce",
        "tomato puree": "tomato sauce",
        "tomato paste": "tomato sauce",
    }
    return aliases.get(cleaned, cleaned)


def _normal_unit(unit: str) -> str:
    aliases = {"grams": "g", "gram": "g", "kilogram": "kg", "kilograms": "kg", "litre": "l", "litres": "l", "liter": "l", "liters": "l", "pieces": "piece", "packets": "packet", "tablespoon": "tbsp", "tablespoons": "tbsp"}
    return aliases.get(unit.strip().casefold(), unit.strip().casefold())


def _convert(quantity: float, from_unit: str, to_unit: str) -> float | None:
    """Convert only unambiguous household units; never guess cups or packets."""
    source, target = _normal_unit(from_unit), _normal_unit(to_unit)
    if source == target:
        return quantity
    factors = {"g": ("weight", 1), "kg": ("weight", 1000), "ml": ("volume", 1), "l": ("volume", 1000), "piece": ("count", 1), "dozen": ("count", 12)}
    if source not in factors or target not in factors or factors[source][0] != factors[target][0]:
        return None
    return quantity * factors[source][1] / factors[target][1]


def _quantity_by_name(inventory: list[dict[str, Any]], today: date) -> dict[str, list[tuple[float, str]]]:
    totals: dict[str, list[tuple[float, str]]] = {}
    for item in inventory:
        expiry = item.get("expiry_date")
        if expiry:
            try:
                exp_date = date.fromisoformat(str(expiry)) if isinstance(expiry, str) else expiry
                if exp_date < today:
                    continue
            except (ValueError, TypeError):
                pass
        raw_name = str(item["ingredient"]).strip().casefold()
        norm_name = _normal_ingredient_name(raw_name)
        val = (float(item["quantity"]), str(item.get("unit", "")))
        totals.setdefault(raw_name, []).append(val)
        if norm_name != raw_name:
            totals.setdefault(norm_name, []).append(val)
    return totals


def _gaps(dish: dict[str, Any], servings: int, inventory: list[dict[str, Any]], today: date) -> list[dict[str, Any]]:
    factor = servings / max(1, dish["servings"])
    stock = _quantity_by_name(inventory, today)
    gaps = []
    for ingredient in dish["ingredients"]:
        needed = float(ingredient["quantity"]) * factor
        # Older persisted/test records may not include a unit, and cups/packets
        # cannot be safely converted. Preserve their historic same-number
        # behavior while preferring precise conversions where known.
        raw_name = str(ingredient["name"]).strip().casefold()
        norm_name = _normal_ingredient_name(raw_name)
        matched_stock = stock.get(raw_name) or stock.get(norm_name, [])
        available = sum(
            converted if (converted := _convert(quantity, unit, str(ingredient["unit"]))) is not None else quantity
            for quantity, unit in matched_stock
        )
        if available < needed:
            name = ingredient["name"]
            gaps.append({"ingredient": name, "needed": round(needed, 2), "available": round(available, 2), "shortfall": round(needed - available, 2), "unit": ingredient["unit"], "substitution": SUBSTITUTIONS.get(raw_name) or SUBSTITUTIONS.get(norm_name)})
    return gaps


def _eligibility(dish: dict[str, Any], data: PlanInput) -> list[str]:
    reasons: list[str] = []
    tags = {tag.lower() for tag in dish.get("tags", [])}
    ingredients = {item["name"].lower() for item in dish["ingredients"]}
    allergies = {allergy.lower() for member in data.members for allergy in member.get("allergies", [])}
    diets = {diet.lower() for member in data.members for diet in member.get("dietary_preferences", [])}
    if ingredients & allergies:
        reasons.append(f"allergen present: {', '.join(sorted(ingredients & allergies))}")
    if "vegetarian" in diets and "vegetarian" not in tags:
        reasons.append("does not meet vegetarian household diet")
    if dish["prep_minutes"] > data.available_minutes:
        reasons.append(f"needs {dish['prep_minutes']} minutes; only {data.available_minutes} available")
    if SKILL_RANK.get(dish["cook_skill_required"], 99) > SKILL_RANK.get(data.cook_skill, -1):
        reasons.append(f"requires {dish['cook_skill_required']} cook skill")
    return reasons


def _procurement(gaps: list[dict[str, Any]], data: PlanInput) -> dict[str, Any]:
    if not gaps:
        return {"route": "use_stock", "estimated_cost_inr": 0, "items": [], "reason": "All ingredients are in confirmed usable stock."}
    prices = {item["ingredient"].strip().casefold(): item for item in data.stores}
    items = []
    total = 0.0
    missing_local = False
    for gap in gaps:
        raw_gap = gap["ingredient"].strip().casefold()
        norm_gap = _normal_ingredient_name(raw_gap)
        item = (
            prices.get(raw_gap)
            or prices.get(norm_gap)
            or LOCAL_PRICE_ESTIMATES.get(raw_gap)
            or LOCAL_PRICE_ESTIMATES.get(norm_gap)
        )
        if item is None:
            missing_local = True
            items.append({**gap, "store": None, "price_inr": None})
        else:
            total += float(item["price_inr"])
            items.append({**gap, "store": item["store_name"], "price_inr": item["price_inr"]})
    if missing_local or total > data.budget_remaining:
        return {"route": "manual_purchase", "estimated_cost_inr": round(total, 2), "items": items, "reason": "A local item is unavailable or the seeded-store basket exceeds the remaining budget."}
    return {"route": "simulated_order", "estimated_cost_inr": round(total, 2), "items": items, "reason": "Seeded local-store items cover the gap within the remaining budget; this is a simulation only."}


def assess_discovered_dish(dish: dict[str, Any], servings: int, inventory: list[dict[str, Any]], stores: list[dict[str, Any]], budget_remaining: float, today: date) -> dict[str, Any]:
    """Deterministically expose inventory gaps and local-only purchase estimates."""
    gaps = _gaps(dish, servings, inventory, today)
    data = PlanInput(servings=servings, available_minutes=0, today=today, inventory=inventory, leftovers=[], members=[], cook_skill="beginner", budget_remaining=budget_remaining, recent_dishes=[], preferences=[], stores=stores)
    return {"missing_ingredients": gaps, "procurement": _procurement(gaps, data)}


def plan(dishes: list[dict[str, Any]], data: PlanInput) -> dict[str, Any]:
    recommendations, exclusions = [], []
    for dish in dishes:
        reasons = _eligibility(dish, data)
        if reasons:
            exclusions.append({"dish": dish["name"], "reasons": reasons})
            continue
        gaps = _gaps(dish, data.servings, data.inventory, data.today)
        expiry_items = [item["ingredient"] for item in data.inventory if item.get("expiry_date") and 0 <= (date.fromisoformat(item["expiry_date"]) - data.today).days <= 2 and item["ingredient"].lower() in {x["name"].lower() for x in dish["ingredients"]}]
        leftovers = [item["dish_name"] for item in data.leftovers if item.get("expiry_date") and date.fromisoformat(item["expiry_date"]) >= data.today]
        score = 50 + len(expiry_items) * 12 + (8 if leftovers else 0) - (18 if dish["name"] in data.recent_dishes else 0) - len(gaps) * 5
        if "light" in {note.lower() for note in dish.get("nutrition_notes", [])} and any("light" in x.lower() for x in data.preferences): score += 7
        procurement = _procurement(gaps, data)
        recommendations.append({"dish_id": dish.get("id"), "dish": dish["name"], "score": score, "servings": data.servings, "prep_minutes": dish["prep_minutes"], "score_explanation": {"expiry_use": expiry_items, "leftover_use": leftovers, "novelty": "recently served penalty" if dish["name"] in data.recent_dishes else "not recently served", "gaps": len(gaps)}, "missing_ingredients": gaps, "procurement": procurement})
    recommendations.sort(key=lambda item: (-item["score"], item["dish"]))
    return {"recommendations": recommendations[:3], "exclusions": exclusions}
