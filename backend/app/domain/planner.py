from dataclasses import dataclass
from datetime import date
from typing import Any


SKILL_RANK = {"beginner": 0, "intermediate": 1, "advanced": 2}
SUBSTITUTIONS = {"paneer": "firm tofu", "tomato": "canned tomato", "moong dal": "masoor dal"}


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


def _quantity_by_name(inventory: list[dict[str, Any]], today: date) -> dict[str, float]:
    totals: dict[str, float] = {}
    for item in inventory:
        if item.get("expiry_date") and date.fromisoformat(item["expiry_date"]) < today:
            continue
        totals[item["ingredient"].lower()] = totals.get(item["ingredient"].lower(), 0) + float(item["quantity"])
    return totals


def _gaps(dish: dict[str, Any], servings: int, inventory: list[dict[str, Any]], today: date) -> list[dict[str, Any]]:
    factor = servings / max(1, dish["servings"])
    stock = _quantity_by_name(inventory, today)
    gaps = []
    for ingredient in dish["ingredients"]:
        needed = float(ingredient["quantity"]) * factor
        available = stock.get(ingredient["name"].lower(), 0)
        if available < needed:
            name = ingredient["name"]
            gaps.append({"ingredient": name, "needed": round(needed, 2), "available": round(available, 2), "shortfall": round(needed - available, 2), "unit": ingredient["unit"], "substitution": SUBSTITUTIONS.get(name.lower())})
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
    prices = {item["ingredient"].lower(): item for item in data.stores}
    items = []
    total = 0.0
    missing_local = False
    for gap in gaps:
        item = prices.get(gap["ingredient"].lower())
        if item is None:
            missing_local = True
            items.append({**gap, "store": None, "price_inr": None})
        else:
            total += float(item["price_inr"])
            items.append({**gap, "store": item["store_name"], "price_inr": item["price_inr"]})
    if missing_local or total > data.budget_remaining:
        return {"route": "manual_purchase", "estimated_cost_inr": round(total, 2), "items": items, "reason": "A local item is unavailable or the seeded-store basket exceeds the remaining budget."}
    return {"route": "simulated_order", "estimated_cost_inr": round(total, 2), "items": items, "reason": "Seeded local-store items cover the gap within the remaining budget; this is a simulation only."}


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
