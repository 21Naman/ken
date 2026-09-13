"""Deterministic local fixtures for household records across diverse dietary and regional profiles."""

from __future__ import annotations

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


def _seed_iyer_household(session: Session, today: date) -> None:
    """Seed Iyer Household (Chennai / Tamil Brahmin - Satvik & South Indian)."""
    household = Household(name="Iyer Household", default_language="Tamil")
    session.add(household)
    session.flush()
    hid = household.id
    assert hid is not None

    m_subbu = HouseholdMember(household_id=hid, name="Subramanian", language="Tamil", dietary_preferences=["satvik", "vegetarian"], allergies=["mustard excess"], health_constraints=["satvik", "no onion garlic"], likes=["curd rice", "soft idlis", "rasam sadam"], dislikes=["garlic", "deep-fried items"])
    m_lakshmi = HouseholdMember(household_id=hid, name="Lakshmi", language="Tamil", dietary_preferences=["vegetarian"], likes=["avial", "kootu", "filter coffee", "dosas"], dislikes=["stale food", "western food"])
    m_karthik = HouseholdMember(household_id=hid, name="Karthik", language="English", dietary_preferences=["vegan"], allergies=["dairy"], health_constraints=["lactose-free"], likes=["lemon rice", "poriyal", "coconut podi"], dislikes=["curd", "ghee", "butter"])
    m_ananya = HouseholdMember(household_id=hid, name="Ananya", language="English", dietary_preferences=["vegetarian"], likes=["podi idli", "curd rice", "appam"], dislikes=["bitter gourd"])
    session.add_all([m_subbu, m_lakshmi, m_karthik, m_ananya])

    session.add(CookProfile(household_id=hid, name="Murugan", language="Tamil", skill_level="expert", available_hours=["07:00-09:00", "18:30-20:30"], confident_dishes=["sambar", "rasam", "avial", "lemon rice", "kootu"]))
    session.add(Budget(household_id=hid, monthly_limit=12500, spent_amount=3100, planned_amount=0, category_allocations={"groceries": 8000, "dairy": 2500, "fresh_produce": 2000}))

    session.add_all([
        InventoryLot(household_id=hid, ingredient="toor dal", quantity=1, unit="kg", expiry_date=today + timedelta(days=120), storage_location="pantry", confirmed=True),
        InventoryLot(household_id=hid, ingredient="drumstick", quantity=3, unit="piece", expiry_date=today + timedelta(days=3), storage_location="fridge", confirmed=True),
        InventoryLot(household_id=hid, ingredient="fresh coconut", quantity=2, unit="piece", expiry_date=today + timedelta(days=2), storage_location="fridge", confirmed=True),
        InventoryLot(household_id=hid, ingredient="curry leaves", quantity=1, unit="bunch", expiry_date=today + timedelta(days=5), storage_location="fridge", confirmed=True),
        InventoryLot(household_id=hid, ingredient="idli batter", quantity=1, unit="kg", expiry_date=today + timedelta(days=3), storage_location="fridge", confirmed=True),
        InventoryLot(household_id=hid, ingredient="raw banana", quantity=2, unit="piece", expiry_date=today + timedelta(days=4), storage_location="pantry", confirmed=True),
    ])

    session.add(Leftover(household_id=hid, dish_name="Tomato Rasam", portions=2, stored_on=today - timedelta(days=1), expiry_date=today + timedelta(days=1), storage_location="fridge", reuse_suggestions=["Warm soup shot", "Serve with hot rice & ghee"]))

    dish_sambar = Dish(household_id=hid, name="Drumstick Sambar Sadam", ingredients=[{"name": "toor dal", "quantity": 1, "unit": "cup"}, {"name": "drumstick", "quantity": 2, "unit": "piece"}, {"name": "tamarind", "quantity": 1, "unit": "tbsp"}], prep_minutes=30, servings=4, nutrition_notes=["protein", "digestive"], tags=["vegetarian", "south-indian", "satvik-option"], cook_skill_required="intermediate")
    dish_avial = Dish(household_id=hid, name="Avial with Red Rice", ingredients=[{"name": "raw banana", "quantity": 1, "unit": "piece"}, {"name": "fresh coconut", "quantity": 0.5, "unit": "piece"}, {"name": "curd", "quantity": 1, "unit": "cup"}], prep_minutes=35, servings=4, nutrition_notes=["fiber", "rich in vitamins"], tags=["vegetarian", "kerala-tamil"], cook_skill_required="intermediate")
    dish_vazhakkai = Dish(household_id=hid, name="Vazhakkai Poriyal & Rasam", ingredients=[{"name": "raw banana", "quantity": 2, "unit": "piece"}, {"name": "tomato", "quantity": 2, "unit": "piece"}], prep_minutes=25, servings=3, nutrition_notes=["potassium", "light"], tags=["vegetarian", "satvik"], cook_skill_required="beginner")
    session.add_all([dish_sambar, dish_avial, dish_vazhakkai])
    session.flush()

    session.add(DishHistory(household_id=hid, dish_id=dish_sambar.id, dish_name="Drumstick Sambar Sadam", served_on=today - timedelta(days=3), accepted=True, rating=5, feedback="Aromatic and comforting", leftovers_portions=0))
    session.add(PreferenceSignal(household_id=hid, member_id=m_subbu.id, signal="Strictly no onion or garlic in grandfather's portion on festival days", sentiment="positive", context="festival", confidence=1.0))
    session.add(PreferenceSignal(household_id=hid, signal="Less oil on weeknights", sentiment="positive", context="dinner", confidence=0.85))
    session.add(MealLoopRecord(household_id=hid, trigger_type="manual", context_note="Tamil traditional dinner routine", status="recorded"))


def _seed_mukherjee_household(session: Session, today: date) -> None:
    """Seed Mukherjee Household (Kolkata / Bengali Pescatarian)."""
    household = Household(name="Mukherjee Household", default_language="Bengali")
    session.add(household)
    session.flush()
    hid = household.id
    assert hid is not None

    m_deba = HouseholdMember(household_id=hid, name="Debabrata", language="Bengali", dietary_preferences=["pescatarian"], health_constraints=["low sodium", "hypertension"], likes=["rohu macher jhol", "shukto", "posto"], dislikes=["heavy spices", "excess salt"])
    m_sharmila = HouseholdMember(household_id=hid, name="Sharmila", language="Bengali", dietary_preferences=["pescatarian"], allergies=["eggplant"], likes=["chholar dal", "luchi", "bhetki paturi"], dislikes=["very sweet curries"])
    m_arindam = HouseholdMember(household_id=hid, name="Arindam", language="English", dietary_preferences=["flexitarian"], allergies=["dairy"], health_constraints=["lactose-free"], likes=["kosha dim", "rui fish", "basmati rice"], dislikes=["karela"])
    session.add_all([m_deba, m_sharmila, m_arindam])

    session.add(CookProfile(household_id=hid, name="Bipul Da", language="Bengali", skill_level="intermediate", available_hours=["11:00-13:00", "19:00-21:00"], confident_dishes=["macher jhol", "shukto", "kosha mangsho", "chholar dal", "aloo posto"]))
    session.add(Budget(household_id=hid, monthly_limit=16000, spent_amount=5400, planned_amount=0, category_allocations={"fish_meat": 6500, "groceries": 6500, "dairy_sweets": 3000}))

    session.add_all([
        InventoryLot(household_id=hid, ingredient="rohu fish", quantity=500, unit="g", expiry_date=today + timedelta(days=2), storage_location="freezer", confirmed=True),
        InventoryLot(household_id=hid, ingredient="mustard oil", quantity=1, unit="L", expiry_date=today + timedelta(days=180), storage_location="pantry", confirmed=True),
        InventoryLot(household_id=hid, ingredient="potato", quantity=2, unit="kg", expiry_date=today + timedelta(days=20), storage_location="pantry", confirmed=True),
        InventoryLot(household_id=hid, ingredient="potol pointed gourd", quantity=400, unit="g", expiry_date=today + timedelta(days=3), storage_location="fridge", confirmed=True),
        InventoryLot(household_id=hid, ingredient="basmati rice", quantity=3, unit="kg", expiry_date=today + timedelta(days=90), storage_location="pantry", confirmed=True),
        InventoryLot(household_id=hid, ingredient="eggs", quantity=6, unit="piece", expiry_date=today + timedelta(days=7), storage_location="fridge", confirmed=True),
    ])

    session.add(Leftover(household_id=hid, dish_name="Shukto", portions=1, stored_on=today - timedelta(days=1), expiry_date=today, storage_location="fridge", reuse_suggestions=["Starter course for lunch"]))

    dish_fish = Dish(household_id=hid, name="Rui Macher Patla Jhol", ingredients=[{"name": "rohu fish", "quantity": 400, "unit": "g"}, {"name": "potato", "quantity": 2, "unit": "piece"}, {"name": "mustard oil", "quantity": 2, "unit": "tbsp"}], prep_minutes=30, servings=3, nutrition_notes=["omega-3", "lean protein"], tags=["pescatarian", "bengali", "comfort"], cook_skill_required="intermediate")
    dish_dalna = Dish(household_id=hid, name="Aloo Potol Dalna", ingredients=[{"name": "potol pointed gourd", "quantity": 300, "unit": "g"}, {"name": "potato", "quantity": 2, "unit": "piece"}], prep_minutes=25, servings=3, nutrition_notes=["fiber", "light"], tags=["vegetarian", "bengali"], cook_skill_required="beginner")
    dish_egg = Dish(household_id=hid, name="Dim Kosha", ingredients=[{"name": "eggs", "quantity": 4, "unit": "piece"}, {"name": "potato", "quantity": 2, "unit": "piece"}], prep_minutes=30, servings=2, nutrition_notes=["high protein"], tags=["eggitarian", "bengali"], cook_skill_required="beginner")
    session.add_all([dish_fish, dish_dalna, dish_egg])
    session.flush()

    session.add(DishHistory(household_id=hid, dish_id=dish_fish.id, dish_name="Rui Macher Patla Jhol", served_on=today - timedelta(days=2), accepted=True, rating=5, feedback="Perfect light broth with cumin & ginger", leftovers_portions=0))
    session.add(PreferenceSignal(household_id=hid, signal="Light cumin-ginger broth for weekday fish curry rather than heavy mustard", sentiment="positive", context="weekday", confidence=0.95))
    session.add(MealLoopRecord(household_id=hid, trigger_type="manual", context_note="Bengali lunch and dinner planner", status="recorded"))


def _seed_patel_household(session: Session, today: date) -> None:
    """Seed Patel Household (Ahmedabad / Gujarati & Jain-friendly)."""
    household = Household(name="Patel Household", default_language="Gujarati")
    session.add(household)
    session.flush()
    hid = household.id
    assert hid is not None

    m_hitesh = HouseholdMember(household_id=hid, name="Hiteshbhai", language="Gujarati", dietary_preferences=["vegetarian"], allergies=["garlic"], health_constraints=["jain fasts on tuesdays"], likes=["gujarati dal", "bhakri", "undhiyu"], dislikes=["extra hot chili"])
    m_bhavna = HouseholdMember(household_id=hid, name="Bhavnaben", language="Gujarati", dietary_preferences=["vegetarian"], likes=["methi thepla", "sev tameta", "handvo"], dislikes=["egg", "meat"])
    m_yash = HouseholdMember(household_id=hid, name="Yash", language="English", dietary_preferences=["gluten-free"], allergies=["wheat", "gluten"], likes=["bajra rotla", "rice poha", "khichdi"], dislikes=["maida", "bakery bread"])
    m_diya = HouseholdMember(household_id=hid, name="Diya", language="Gujarati", dietary_preferences=["vegetarian"], allergies=["peanuts"], likes=["cheese sev tameta", "dhokla", "shrikhand"], dislikes=["boiled vegetables"])
    session.add_all([m_hitesh, m_bhavna, m_yash, m_diya])

    session.add(CookProfile(household_id=hid, name="Ramila Ben", language="Gujarati", skill_level="expert", available_hours=["08:00-10:00", "18:00-19:30"], confident_dishes=["gujarati dal", "sev tameta", "thepla", "handvo", "dudhi shaak"]))
    session.add(Budget(household_id=hid, monthly_limit=13000, spent_amount=3900, planned_amount=0, category_allocations={"groceries": 8000, "dairy_farsan": 3500, "fresh_produce": 1500}))

    session.add_all([
        InventoryLot(household_id=hid, ingredient="besan gram flour", quantity=1, unit="kg", expiry_date=today + timedelta(days=90), storage_location="pantry", confirmed=True),
        InventoryLot(household_id=hid, ingredient="bajra millet flour", quantity=1, unit="kg", expiry_date=today + timedelta(days=30), storage_location="pantry", confirmed=True),
        InventoryLot(household_id=hid, ingredient="jaggery", quantity=500, unit="g", expiry_date=today + timedelta(days=180), storage_location="pantry", confirmed=True),
        InventoryLot(household_id=hid, ingredient="fresh methi", quantity=2, unit="bunch", expiry_date=today + timedelta(days=2), storage_location="fridge", confirmed=True),
        InventoryLot(household_id=hid, ingredient="bottle gourd dudhi", quantity=1, unit="piece", expiry_date=today + timedelta(days=3), storage_location="fridge", confirmed=True),
        InventoryLot(household_id=hid, ingredient="tomato", quantity=1, unit="kg", expiry_date=today + timedelta(days=5), storage_location="fridge", confirmed=True),
        InventoryLot(household_id=hid, ingredient="sev", quantity=200, unit="g", expiry_date=today + timedelta(days=30), storage_location="pantry", confirmed=True),
    ])

    session.add(Leftover(household_id=hid, dish_name="Gujarati Kadhi", portions=2, stored_on=today - timedelta(days=1), expiry_date=today + timedelta(days=1), storage_location="fridge", reuse_suggestions=["Serve with hot Khichdi tonight"]))

    dish_sev = Dish(household_id=hid, name="Sev Tameta Nu Shaak with Thepla", ingredients=[{"name": "tomato", "quantity": 4, "unit": "piece"}, {"name": "sev", "quantity": 100, "unit": "g"}, {"name": "fresh methi", "quantity": 1, "unit": "bunch"}], prep_minutes=25, servings=4, nutrition_notes=["sweet and savory", "quick"], tags=["vegetarian", "gujarati", "kathiyawadi"], cook_skill_required="beginner")
    dish_dal = Dish(household_id=hid, name="Khatti Meethi Gujarati Dal & Rice", ingredients=[{"name": "toor dal", "quantity": 1, "unit": "cup"}, {"name": "jaggery", "quantity": 2, "unit": "tbsp"}], prep_minutes=30, servings=4, nutrition_notes=["protein", "sweet and sour"], tags=["vegetarian", "gujarati"], cook_skill_required="intermediate")
    dish_bajra = Dish(household_id=hid, name="Bajra Rotla with Baingan Bharta", ingredients=[{"name": "bajra millet flour", "quantity": 200, "unit": "g"}, {"name": "eggplant", "quantity": 1, "unit": "piece"}], prep_minutes=35, servings=3, nutrition_notes=["gluten-free", "fiber", "rustic"], tags=["vegetarian", "gluten-free", "traditional"], cook_skill_required="intermediate")
    session.add_all([dish_sev, dish_dal, dish_bajra])
    session.flush()

    session.add(DishHistory(household_id=hid, dish_id=dish_sev.id, dish_name="Sev Tameta Nu Shaak with Thepla", served_on=today - timedelta(days=4), accepted=True, rating=5, feedback="Delicious tangy tomato gravy with crispy sev", leftovers_portions=0))
    session.add(PreferenceSignal(household_id=hid, member_id=m_hitesh.id, signal="Tuesdays dinner must be root-vegetable free (Jain) for Hiteshbhai, and Bajra Rotla for Yash", sentiment="positive", context="tuesday", confidence=1.0))
    session.add(MealLoopRecord(household_id=hid, trigger_type="manual", context_note="Gujarati satvik and farsan rotation", status="recorded"))


def _seed_fernandes_household(session: Session, today: date) -> None:
    """Seed Fernandes Household (Goa / Coastal Seafood & Mild Curries)."""
    household = Household(name="Fernandes Household", default_language="English")
    session.add(household)
    session.flush()
    hid = household.id
    assert hid is not None

    m_anthony = HouseholdMember(household_id=hid, name="Anthony", language="English", dietary_preferences=["non-vegetarian"], likes=["kingfish curry", "vindaloo", "poi bread"], dislikes=["bland boiled food"])
    m_maria = HouseholdMember(household_id=hid, name="Maria", language="English", dietary_preferences=["pescatarian", "gluten-free"], allergies=["wheat", "gluten"], health_constraints=["gluten-free"], likes=["coconut fish curry", "goan red rice", "xacuti"], dislikes=["refined flour"])
    m_jude = HouseholdMember(household_id=hid, name="Jude", language="English", dietary_preferences=["flexitarian"], likes=["prawn balchao", "roast chicken", "boiled eggs"], dislikes=["karela", "okra"])
    m_chloe = HouseholdMember(household_id=hid, name="Chloe", language="English", dietary_preferences=["flexitarian"], allergies=["egg yolk"], likes=["mushroom caldine", "mild coconut curries"], dislikes=["overly spicy chili paste"])
    session.add_all([m_anthony, m_maria, m_jude, m_chloe])

    session.add(CookProfile(household_id=hid, name="Francis", language="English", skill_level="intermediate", available_hours=["12:00-14:00", "19:00-21:00"], confident_dishes=["fish caldine", "mushroom xacuti", "eggplant vindaloo", "prawn balchao"]))
    session.add(Budget(household_id=hid, monthly_limit=17500, spent_amount=6200, planned_amount=0, category_allocations={"seafood_meat": 7500, "groceries": 7000, "bakery_dairy": 3000}))

    session.add_all([
        InventoryLot(household_id=hid, ingredient="kingfish steaks", quantity=400, unit="g", expiry_date=today + timedelta(days=2), storage_location="freezer", confirmed=True),
        InventoryLot(household_id=hid, ingredient="coconut milk", quantity=3, unit="can", expiry_date=today + timedelta(days=120), storage_location="pantry", confirmed=True),
        InventoryLot(household_id=hid, ingredient="goan red rice", quantity=2, unit="kg", expiry_date=today + timedelta(days=90), storage_location="pantry", confirmed=True),
        InventoryLot(household_id=hid, ingredient="kokum", quantity=1, unit="pack", expiry_date=today + timedelta(days=180), storage_location="pantry", confirmed=True),
        InventoryLot(household_id=hid, ingredient="fresh mushrooms", quantity=200, unit="g", expiry_date=today + timedelta(days=2), storage_location="fridge", confirmed=True),
        InventoryLot(household_id=hid, ingredient="goan vinegar", quantity=1, unit="bottle", expiry_date=today + timedelta(days=180), storage_location="pantry", confirmed=True),
    ])

    session.add(Leftover(household_id=hid, dish_name="Mushroom & Green Pea Xacuti", portions=1.5, stored_on=today - timedelta(days=1), expiry_date=today + timedelta(days=1), storage_location="fridge", reuse_suggestions=["Sandwich spread or rice side-dish"]))

    dish_cald = Dish(household_id=hid, name="Goan Fish Caldine with Red Rice", ingredients=[{"name": "kingfish steaks", "quantity": 350, "unit": "g"}, {"name": "coconut milk", "quantity": 1, "unit": "can"}, {"name": "goan red rice", "quantity": 1, "unit": "cup"}], prep_minutes=30, servings=3, nutrition_notes=["omega-3", "coconut fats", "gluten-free"], tags=["pescatarian", "goan", "mild"], cook_skill_required="intermediate")
    dish_xac = Dish(household_id=hid, name="Mushroom & Green Pea Xacuti", ingredients=[{"name": "fresh mushrooms", "quantity": 200, "unit": "g"}, {"name": "coconut milk", "quantity": 0.5, "unit": "can"}], prep_minutes=35, servings=3, nutrition_notes=["plant protein", "aromatic spices"], tags=["vegetarian", "goan"], cook_skill_required="intermediate")
    dish_vin = Dish(household_id=hid, name="Tangy Eggplant Vindaloo", ingredients=[{"name": "eggplant", "quantity": 2, "unit": "piece"}, {"name": "goan vinegar", "quantity": 2, "unit": "tbsp"}], prep_minutes=30, servings=3, nutrition_notes=["antioxidants", "tangy spicy"], tags=["vegetarian", "spicy", "portuguese-goan"], cook_skill_required="intermediate")
    session.add_all([dish_cald, dish_xac, dish_vin])
    session.flush()

    session.add(DishHistory(household_id=hid, dish_id=dish_cald.id, dish_name="Goan Fish Caldine with Red Rice", served_on=today - timedelta(days=5), accepted=True, rating=5, feedback="Creamy mild coconut broth, loved by everyone", leftovers_portions=0))
    session.add(PreferenceSignal(household_id=hid, signal="Use coconut-based mild gravies for Chloe; provide extra spiced peri-peri on the side for Anthony", sentiment="positive", context="dinner", confidence=0.9))
    session.add(MealLoopRecord(household_id=hid, trigger_type="manual", context_note="Goan coastal curry cycle", status="recorded"))


def _seed_kapoor_household(session: Session, today: date) -> None:
    """Seed Kapoor Household (Gurgaon / Fitness, Low-Carb & Mediterranean Bowls)."""
    household = Household(name="Kapoor Household", default_language="English")
    session.add(household)
    session.flush()
    hid = household.id
    assert hid is not None

    m_vikram = HouseholdMember(household_id=hid, name="Vikram", language="English", dietary_preferences=["high-protein", "low-carb"], allergies=["refined sugar"], health_constraints=["keto-leaning", "intermittent fasting"], likes=["grilled herb chicken", "broccoli stir-fry", "black coffee"], dislikes=["rice", "potatoes", "heavy oily curries"])
    m_ritu = HouseholdMember(household_id=hid, name="Ritu", language="English", dietary_preferences=["mediterranean", "flexitarian"], allergies=["excess lactose"], health_constraints=["calorie-conscious"], likes=["quinoa bowls", "tofu stir-fry", "avocado salads"], dislikes=["deep-fried snacks", "maida"])
    m_kabir = HouseholdMember(household_id=hid, name="Kabir", language="English", dietary_preferences=["high-protein"], likes=["paneer wraps", "egg bhurji with paratha", "pasta"], dislikes=["plain boiled greens"])
    session.add_all([m_vikram, m_ritu, m_kabir])

    session.add(CookProfile(household_id=hid, name="Rajesh", language="Hindi", skill_level="expert", available_hours=["07:30-09:30", "19:30-21:30"], confident_dishes=["quinoa rainbow bowls", "grilled chicken breast", "air-fryer tofu", "moong dal cheela", "stir-fry paneer"]))
    session.add(Budget(household_id=hid, monthly_limit=22000, spent_amount=8100, planned_amount=0, category_allocations={"organic_proteins": 12000, "superfoods_dairy": 6000, "pantry": 4000}))

    session.add_all([
        InventoryLot(household_id=hid, ingredient="chicken breast", quantity=600, unit="g", expiry_date=today + timedelta(days=3), storage_location="freezer", confirmed=True),
        InventoryLot(household_id=hid, ingredient="organic quinoa", quantity=1, unit="kg", expiry_date=today + timedelta(days=180), storage_location="pantry", confirmed=True),
        InventoryLot(household_id=hid, ingredient="broccoli", quantity=500, unit="g", expiry_date=today + timedelta(days=3), storage_location="fridge", confirmed=True),
        InventoryLot(household_id=hid, ingredient="firm tofu", quantity=250, unit="g", expiry_date=today + timedelta(days=5), storage_location="fridge", confirmed=True),
        InventoryLot(household_id=hid, ingredient="eggs", quantity=12, unit="piece", expiry_date=today + timedelta(days=10), storage_location="fridge", confirmed=True),
        InventoryLot(household_id=hid, ingredient="bell peppers", quantity=3, unit="piece", expiry_date=today + timedelta(days=4), storage_location="fridge", confirmed=True),
        InventoryLot(household_id=hid, ingredient="olive oil", quantity=1, unit="bottle", expiry_date=today + timedelta(days=180), storage_location="pantry", confirmed=True),
    ])

    session.add(Leftover(household_id=hid, dish_name="Air-Fried Tofu Stir Fry", portions=1, stored_on=today - timedelta(days=1), expiry_date=today, storage_location="fridge", reuse_suggestions=["Add to lunch salad bowl"]))

    dish_chicken = Dish(household_id=hid, name="Grilled Lemon Herb Chicken & Broccoli", ingredients=[{"name": "chicken breast", "quantity": 400, "unit": "g"}, {"name": "broccoli", "quantity": 250, "unit": "g"}, {"name": "olive oil", "quantity": 1, "unit": "tbsp"}], prep_minutes=25, servings=2, nutrition_notes=["high protein", "low carb", "keto-friendly"], tags=["high-protein", "keto", "dinner"], cook_skill_required="beginner")
    dish_quinoa = Dish(household_id=hid, name="Quinoa Mediterranean Rainbow Bowl", ingredients=[{"name": "organic quinoa", "quantity": 150, "unit": "g"}, {"name": "bell peppers", "quantity": 2, "unit": "piece"}, {"name": "firm tofu", "quantity": 150, "unit": "g"}], prep_minutes=20, servings=2, nutrition_notes=["complete protein", "superfood", "fiber"], tags=["vegan", "clean-eating", "mediterranean"], cook_skill_required="beginner")
    dish_cheela = Dish(household_id=hid, name="Moong Dal Cheela with Mint Chutney", ingredients=[{"name": "moong dal", "quantity": 1, "unit": "cup"}, {"name": "paneer", "quantity": 100, "unit": "g"}], prep_minutes=20, servings=3, nutrition_notes=["plant protein", "low glycemic index"], tags=["vegetarian", "fitness", "breakfast"], cook_skill_required="beginner")
    session.add_all([dish_chicken, dish_quinoa, dish_cheela])
    session.flush()

    session.add(DishHistory(household_id=hid, dish_id=dish_chicken.id, dish_name="Grilled Lemon Herb Chicken & Broccoli", served_on=today - timedelta(days=1), accepted=True, rating=5, feedback="Juicy chicken and perfectly crisp broccoli, fit macros ideally", leftovers_portions=0))
    session.add(PreferenceSignal(household_id=hid, signal="Dinner must be under 550 kcal for Vikram & Ritu, with high-carb options for Kabir", sentiment="positive", context="dinner", confidence=0.95))
    session.add(MealLoopRecord(household_id=hid, trigger_type="manual", context_note="Fitness & calorie counted meal loop", status="recorded"))


def reset_demo_data(session: Session, scenario: str = "default") -> dict[str, int | str]:
    """Replace all demo data with deterministic scenario fixtures across households."""
    if scenario not in DEMO_SCENARIOS:
        choices = ", ".join(DEMO_SCENARIOS)
        raise ValueError(f"Unknown demo scenario '{scenario}'. Choose one of: {choices}")

    for model in (AuditEvent, ApprovalRequest, LocalTask, DishHistory, PreferenceSignal, MealLoopRecord, InventoryLot, Leftover, HouseholdMember, CookProfile, Budget, Dish, Household, DemoRecipe, DemoStoreItem):
        session.exec(delete(model))

    session.add_all([DemoRecipe.model_validate(item) for item in RECIPE_FIXTURES])
    session.add_all([DemoStoreItem.model_validate(item) for item in STORE_FIXTURES])

    # 1. Primary Household (Sharma Household)
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
        inventory[2].quantity = 0
        session.add(InventoryLot(household_id=household_id, ingredient="moong dal", quantity=0.5, unit="cup", expiry_date=today + timedelta(days=90), storage_location="pantry", confirmed=True))
        scenario_loop = MealLoopRecord(household_id=household_id, trigger_type="cooking_mishap", context_note="Paneer was spoiled during prep; recover with stocked khichdi", status="cooking")
        session.add(scenario_loop)
    elif scenario == "feedback_learning":
        baseline_preference.signal = "Keep dinner familiar"
        session.add_all([
            DishHistory(household_id=household_id, dish_id=paneer.id, dish_name="Paneer Bhurji", served_on=today - timedelta(days=1), accepted=False, rating=2, feedback="Too heavy", leftovers_portions=1),
            PreferenceSignal(household_id=household_id, signal="Prefer light dinners after paneer felt too heavy", sentiment="positive", context="completed meal feedback", confidence=1),
        ])
        scenario_loop = MealLoopRecord(household_id=household_id, trigger_type="manual", context_note="Completed Paneer Bhurji loop: too heavy", status="completed")
        session.add(scenario_loop)
    elif scenario == "budget_constraint":
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

    # Seed the remaining 5 households
    _seed_iyer_household(session, today)
    _seed_mukherjee_household(session, today)
    _seed_patel_household(session, today)
    _seed_fernandes_household(session, today)
    _seed_kapoor_household(session, today)

    session.commit()
    return {"scenario": scenario, "recipes": len(RECIPE_FIXTURES), "store_items": len(STORE_FIXTURES), "household_id": household_id}
