from datetime import date, timedelta

from app.domain.planner import PlanInput, plan


def data(**changes):
    base = dict(servings=2, available_minutes=45, today=date.today(), inventory=[], leftovers=[], members=[{"allergies": ["peanuts"], "dietary_preferences": ["vegetarian"]}], cook_skill="intermediate", budget_remaining=500, recent_dishes=[], preferences=["Prefer light dinners"], stores=[{"ingredient": "paneer", "store_name": "Local", "price_inr": 90}])
    base.update(changes)
    return PlanInput(**base)


def test_allergy_and_time_exclusions_are_never_recommended():
    dishes = [
        {"id": 1, "name": "Peanut Dish", "ingredients": [{"name": "peanuts", "quantity": 1, "unit": "g"}], "servings": 2, "prep_minutes": 10, "tags": ["vegetarian"], "nutrition_notes": [], "cook_skill_required": "beginner"},
        {"id": 2, "name": "Slow Dish", "ingredients": [], "servings": 2, "prep_minutes": 90, "tags": ["vegetarian"], "nutrition_notes": [], "cook_skill_required": "beginner"},
    ]
    result = plan(dishes, data())
    assert result["recommendations"] == []
    assert {item["dish"] for item in result["exclusions"]} == {"Peanut Dish", "Slow Dish"}


def test_expiry_scoring_scaling_gaps_and_procurement_are_deterministic():
    dish = {"id": 1, "name": "Carrot Paneer", "ingredients": [{"name": "carrot", "quantity": 1, "unit": "piece"}, {"name": "paneer", "quantity": 200, "unit": "g"}], "servings": 2, "prep_minutes": 20, "tags": ["vegetarian"], "nutrition_notes": ["light"], "cook_skill_required": "beginner"}
    inventory = [{"ingredient": "carrot", "quantity": 2, "expiry_date": str(date.today() + timedelta(days=1))}]
    result = plan([dish], data(servings=4, inventory=inventory))
    recommendation = result["recommendations"][0]
    assert recommendation["score_explanation"]["expiry_use"] == ["carrot"]
    assert {gap["ingredient"]: gap["shortfall"] for gap in recommendation["missing_ingredients"]} == {"paneer": 400.0}
    assert recommendation["missing_ingredients"][0]["substitution"] == "firm tofu"
    assert recommendation["procurement"]["route"] == "simulated_order"
    assert result == plan([dish], data(servings=4, inventory=inventory))


def test_plan_context_date_controls_expired_inventory_filtering():
    dish = {"id": 1, "name": "Rice", "ingredients": [{"name": "rice", "quantity": 1, "unit": "cup"}], "servings": 1, "prep_minutes": 10, "tags": ["vegetarian"], "nutrition_notes": [], "cook_skill_required": "beginner"}
    inventory = [{"ingredient": "rice", "quantity": 1, "expiry_date": "2026-01-02"}]
    result = plan([dish], data(servings=1, today=date(2026, 1, 3), inventory=inventory))
    assert result["recommendations"][0]["missing_ingredients"][0]["ingredient"] == "rice"
