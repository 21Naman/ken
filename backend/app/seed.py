"""Deterministic local fixtures for a complete Phase 2 household record."""

from datetime import date, timedelta

from sqlmodel import Session, delete

from app.models import (
    ApprovalRequest, AuditEvent, Budget, CookProfile, DemoRecipe, DemoStoreItem, Dish, DishHistory, Household,
    HouseholdMember, InventoryLot, Leftover, LocalTask, MealLoopRecord, PreferenceSignal,
)

RECIPE_FIXTURES = (
    {"slug": "vegetable-khichdi", "name": "Vegetable Khichdi", "ingredients": [{"name": "rice", "quantity": 1, "unit": "cup"}, {"name": "moong dal", "quantity": 0.5, "unit": "cup"}, {"name": "carrot", "quantity": 1, "unit": "piece"}]},
    {"slug": "paneer-bhurji", "name": "Paneer Bhurji", "ingredients": [{"name": "paneer", "quantity": 250, "unit": "g"}, {"name": "tomato", "quantity": 2, "unit": "piece"}]},
)
STORE_FIXTURES = (
    {"store_name": "Neighbourhood Grocer", "ingredient": "paneer", "unit": "250 g", "price_inr": 95},
    {"store_name": "Neighbourhood Grocer", "ingredient": "tomato", "unit": "1 kg", "price_inr": 42},
    {"store_name": "Local Dairy", "ingredient": "moong dal", "unit": "500 g", "price_inr": 88},
)
DEMO_SCENARIOS = (
    "default",
    "expiry_routine",
    "preference_conflict",
    "guests",
    "cook_mishap",
    "feedback_learning",
    "budget_constraint",
)


def reset_demo_data(session: Session, scenario: str = "default") -> dict[str, int | str]:
    """Replace all demo data with the requested deterministic scenario fixture."""
    if scenario not in DEMO_SCENARIOS:
        choices = ", ".join(DEMO_SCENARIOS)
        raise ValueError(f"Unknown demo scenario '{scenario}'. Choose one of: {choices}")

    for model in (AuditEvent, ApprovalRequest, LocalTask, DishHistory, PreferenceSignal, MealLoopRecord, InventoryLot, Leftover, HouseholdMember, CookProfile, Budget, Dish, Household, DemoRecipe, DemoStoreItem):
        session.exec(delete(model))

    session.add_all([DemoRecipe.model_validate(item) for item in RECIPE_FIXTURES])
    session.add_all([DemoStoreItem.model_validate(item) for item in STORE_FIXTURES])
    household = Household(name="Sharma Household", default_language="English")
    session.add(household)
    session.commit()
    session.refresh(household)
    assert household.id is not None
    household_id = household.id

    members = [
        HouseholdMember(household_id=household_id, name="Asha", language="English", dietary_preferences=["vegetarian"], allergies=["peanuts"], likes=["light dinners"], dislikes=["very spicy food"]),
        HouseholdMember(household_id=household_id, name="Rohan", language="Hindi", dietary_preferences=["vegetarian"], likes=["paneer", "dal"]),
    ]
    session.add_all(members)
    session.add(CookProfile(household_id=household_id, name="Sita", language="Hindi", skill_level="intermediate", available_hours=["18:00-20:00"], confident_dishes=["khichdi", "dal", "sabzi"]))
    budget = Budget(household_id=household_id, monthly_limit=12000, spent_amount=3800, planned_amount=0, category_allocations={"groceries": 8500, "dairy": 2000})
    session.add(budget)

    today = date.today()
    inventory = [
        InventoryLot(household_id=household_id, ingredient="carrot", quantity=3, unit="piece", purchased_on=today - timedelta(days=3), expiry_date=today + timedelta(days=1), storage_location="fridge", confirmed=True),
        InventoryLot(household_id=household_id, ingredient="rice", quantity=1.5, unit="kg", expiry_date=today + timedelta(days=90), storage_location="pantry", confirmed=True),
        InventoryLot(household_id=household_id, ingredient="paneer", quantity=200, unit="g", expiry_date=today, storage_location="fridge", confirmed=True),
    ]
    session.add_all(inventory)
    session.add(Leftover(household_id=household_id, dish_name="Moong Dal", portions=1.5, stored_on=today - timedelta(days=1), expiry_date=today + timedelta(days=1), storage_location="fridge", reuse_suggestions=["Serve with rice", "Use in dal paratha filling"]))
    khichdi = Dish(household_id=household_id, name="Vegetable Khichdi", ingredients=RECIPE_FIXTURES[0]["ingredients"], prep_minutes=35, servings=3, nutrition_notes=["protein", "light"], tags=["vegetarian"], cook_skill_required="beginner")
    paneer = Dish(household_id=household_id, name="Paneer Bhurji", ingredients=RECIPE_FIXTURES[1]["ingredients"], prep_minutes=25, servings=2, nutrition_notes=["protein"], tags=["vegetarian"], cook_skill_required="intermediate")
    peanut = Dish(household_id=household_id, name="Peanut Noodles", ingredients=[{"name": "peanuts", "quantity": 100, "unit": "g"}, {"name": "noodles", "quantity": 200, "unit": "g"}], prep_minutes=20, servings=2, nutrition_notes=[], tags=["vegetarian"], cook_skill_required="beginner")
    session.add_all([khichdi, paneer, peanut])
    session.commit()
    session.refresh(khichdi)
    session.add(DishHistory(household_id=household_id, dish_id=khichdi.id, dish_name="Vegetable Khichdi", served_on=today - timedelta(days=8), accepted=True, rating=4, feedback="Comforting and light", leftovers_portions=0))
    baseline_preference = PreferenceSignal(household_id=household_id, member_id=members[0].id, signal="Prefer light dinners on weekdays", sentiment="positive", context="weekday", confidence=0.9)
    session.add(baseline_preference)
    session.add(MealLoopRecord(household_id=household_id, trigger_type="manual", context_note="Historical dinner record only", status="recorded"))
    scenario_loop: MealLoopRecord | None = None
    if scenario == "expiry_routine":
        inventory[0].expiry_date = today
        inventory[2].expiry_date = today + timedelta(days=30)
        session.add(Leftover(household_id=household_id, dish_name="Carrot sabzi", portions=1, stored_on=today - timedelta(days=1), expiry_date=today, storage_location="fridge", reuse_suggestions=["Serve tonight"]))
        members[0].likes = ["light dinners", "use expiring vegetables"]
        scenario_loop = MealLoopRecord(household_id=household_id, trigger_type="routine_expiry", context_note="Carrots must be used tonight", status="completed")
        session.add(scenario_loop)
    elif scenario == "preference_conflict":
        # Rohan's request conflicts with Asha's dairy safety constraint.  The
        # established allergy filter must win over a taste preference.
        members[0].allergies = ["peanuts", "paneer"]
        members[0].health_constraints = ["dairy-free"]
        session.add_all([
            PreferenceSignal(household_id=household_id, member_id=members[0].id, signal="Avoid paneer tonight", sentiment="negative", context="tonight", confidence=0.9, expires_on=today),
            PreferenceSignal(household_id=household_id, member_id=members[1].id, signal="Paneer for dinner", sentiment="positive", context="tonight", confidence=0.9, expires_on=today),
        ])
        scenario_loop = MealLoopRecord(household_id=household_id, trigger_type="preference_conflict", context_note="Rohan requested paneer; Asha must avoid it", status="awaiting_approval")
        session.add(scenario_loop)
    elif scenario == "guests":
        scenario_loop = MealLoopRecord(household_id=household_id, trigger_type="guest_arrival", context_note="Four guests arriving for dinner", status="triggered")
        session.add(scenario_loop)
    elif scenario == "cook_mishap":
        # The paneer is no longer usable; the stocked khichdi ingredients make
        # the existing deterministic recovery option immediately viable.
        inventory[2].quantity = 0
        session.add(InventoryLot(household_id=household_id, ingredient="moong dal", quantity=0.5, unit="cup", expiry_date=today + timedelta(days=90), storage_location="pantry", confirmed=True))
        scenario_loop = MealLoopRecord(household_id=household_id, trigger_type="cooking_mishap", context_note="Paneer was spoiled during prep; recover with stocked khichdi", status="cooking")
        session.add(scenario_loop)
    elif scenario == "feedback_learning":
        # This is the persisted output of a completed feedback loop.  The
        # planner's existing light-preference bonus is deliberately the only
        # learned ranking effect used here.
        baseline_preference.signal = "Keep dinner familiar"
        session.add_all([
            DishHistory(household_id=household_id, dish_id=paneer.id, dish_name="Paneer Bhurji", served_on=today - timedelta(days=1), accepted=False, rating=2, feedback="Too heavy", leftovers_portions=1),
            PreferenceSignal(household_id=household_id, signal="Prefer light dinners after paneer felt too heavy", sentiment="positive", context="completed meal feedback", confidence=1),
        ])
        scenario_loop = MealLoopRecord(household_id=household_id, trigger_type="manual", context_note="Completed Paneer Bhurji loop: too heavy", status="completed")
        session.add(scenario_loop)
    elif scenario == "budget_constraint":
        # ₹90 remains: the ₹137 paneer-and-tomato basket must be a manual
        # purchase, while the ₹88 moong-dal basket remains a simulated option.
        budget.spent_amount = 11910
        inventory[0].expiry_date = today + timedelta(days=30)
        baseline_preference.signal = "Keep dinner familiar"
        scenario_loop = MealLoopRecord(household_id=household_id, trigger_type="budget_constraint", context_note="Only ₹90 remains for the meal", status="awaiting_approval")
        session.add(scenario_loop)

    audit_traces = {
        "expiry_routine": [("triggered", "routine_expiry"), ("planned", "expiry-led Vegetable Khichdi"), ("local_task_created", "simulated_order"), ("completed", "outcome captured")],
        "preference_conflict": [("triggered", "preference_conflict"), ("planned", "paneer excluded for allergy"), ("approval_requested", "red")],
        "guests": [("triggered", "guest_arrival")],
        "cook_mishap": [("triggered", "cooking_mishap"), ("planned", "recovery plan"), ("approved", "stocked alternative"), ("cook_briefed", "Vegetable Khichdi"), ("cooking", "recovery in progress")],
        "feedback_learning": [("triggered", "manual"), ("planned", "Paneer Bhurji"), ("approved", "confirmed"), ("cooking", "cook started"), ("completed", "outcome captured")],
        "budget_constraint": [("triggered", "budget_constraint"), ("planned", "₹137 paneer basket"), ("approval_requested", "yellow")],
    }
    session.flush()
    if scenario_loop is not None:
        assert scenario_loop.id is not None
        session.add_all([AuditEvent(household_id=household_id, meal_loop_id=scenario_loop.id, event=event, detail=detail) for event, detail in audit_traces.get(scenario, [])])
        if scenario == "preference_conflict":
            session.add(ApprovalRequest(household_id=household_id, meal_loop_id=scenario_loop.id, tier="red", action="choose allergy-safe dinner", amount_inr=0, reason="Household preference conflicts with a safety constraint"))
        elif scenario == "budget_constraint":
            session.add(ApprovalRequest(household_id=household_id, meal_loop_id=scenario_loop.id, tier="yellow", action="manual_purchase", amount_inr=137, reason="The paneer basket exceeds the ₹90 remaining budget"))
    session.commit()
    return {"scenario": scenario, "recipes": len(RECIPE_FIXTURES), "store_items": len(STORE_FIXTURES), "household_id": household_id}
