from fastapi.testclient import TestClient
from datetime import date, timedelta
import json
from pathlib import Path
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.database import create_database_engine, get_session, initialize_database
from app.main import app
from app.models import DemoRecipe, DemoStoreItem, Household, InventoryLot, ZeptoConnection
from app.providers.ollama import OllamaHealth, OllamaProvider
from app.providers.whisper import WhisperProvider
from app.providers.vision import VisionProvider
from app.seed import DEMO_SCENARIOS
from app.settings import get_settings

FIXTURES = Path(__file__).parent / "fixtures"


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


class FakeOllamaClient:
    def __init__(self, responses):
        self.responses = iter(responses)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def get(self, *_):
        return next(self.responses)

    def post(self, *_ , **__):
        return next(self.responses)


def make_client(monkeypatch, ollama_health: OllamaHealth):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def session_override():
        with Session(engine) as session:
            yield session

    monkeypatch.setattr(OllamaProvider, "health", lambda _: ollama_health)
    app.dependency_overrides[get_session] = session_override
    get_settings.cache_clear()
    return TestClient(app), engine


def test_startup_creates_database_tables(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        assert client.get("/api/health").status_code == 200
    app.dependency_overrides.clear()


def test_health_reports_ollama_availability(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["database"] == {"status": "available"}
    assert body["ollama"] == {"status": "available", "model": "qwen3:4b", "detail": None}
    assert body["scheduler"]["status"] in {"available", "unavailable"}
    app.dependency_overrides.clear()


def test_health_surfaces_ollama_model_and_response_failures(monkeypatch):
    for status in ("unavailable", "model_unavailable", "invalid_response"):
        client, _ = make_client(monkeypatch, OllamaHealth(status, "qwen3:4b", "test detail"))
        with client:
            assert client.get("/api/health").json()["ollama"]["status"] == status
    app.dependency_overrides.clear()


def test_scheduler_unavailability_is_visible_in_health_and_schedule_api(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    monkeypatch.setattr("app.api.routes.scheduler_status", lambda: ("unavailable", "Automatic local triggers are unavailable; use the manual trigger instead."))
    monkeypatch.setattr("app.api.routes.add_daily_trigger", lambda *_: (_ for _ in ()).throw(RuntimeError("Automatic local triggers are unavailable; use the manual trigger instead.")))
    with client:
        assert client.get("/api/health").json()["scheduler"] == {"status": "unavailable", "detail": "Automatic local triggers are unavailable; use the manual trigger instead."}
        household_id = client.post("/api/demo/reset").json()["household_id"]
        response = client.put(f"/api/households/{household_id}/schedule")
        assert response.status_code == 503
        assert "manual trigger" in response.json()["detail"]
    app.dependency_overrides.clear()


def test_application_default_enables_hugging_face_offline_mode(monkeypatch):
    from app.settings import enable_local_only_defaults

    monkeypatch.delenv("HF_HUB_OFFLINE", raising=False)
    enable_local_only_defaults()
    assert __import__("os").environ["HF_HUB_OFFLINE"] == "1"


def test_reset_replaces_seed_fixtures(monkeypatch):
    client, engine = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        first = client.post("/api/demo/reset")
        second = client.post("/api/demo/reset")
    assert first.json() == second.json() == {"status": "reset", "scenario": "default", "recipes": 2, "store_items": 3, "household_id": 1}
    with Session(engine) as session:
        assert len(session.exec(select(DemoRecipe)).all()) == 2
        assert len(session.exec(select(DemoStoreItem)).all()) == 3
    app.dependency_overrides.clear()


def _scenario_snapshot(client: TestClient, household_id: int) -> dict[str, object]:
    ignored = {"id", "household_id", "member_id", "dish_id", "created_at", "updated_at"}

    def normalize(value):
        if isinstance(value, dict):
            return {key: normalize(item) for key, item in value.items() if key not in ignored}
        if isinstance(value, list):
            return [normalize(item) for item in value]
        return value

    paths = ("members", "cook-profile", "budget", "inventory", "leftovers", "history", "preferences", "meal-loops")
    return {path: normalize(client.get(f"/api/households/{household_id}/{path}").json()) for path in paths}


def test_named_scenario_resets_are_repeatable(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        for scenario in DEMO_SCENARIOS:
            first = client.post("/api/demo/reset", params={"scenario": scenario}).json()
            first_snapshot = _scenario_snapshot(client, first["household_id"])
            second = client.post("/api/demo/reset", params={"scenario": scenario}).json()
            assert first == second
            assert _scenario_snapshot(client, second["household_id"]) == first_snapshot
    app.dependency_overrides.clear()


def test_scenario_fixtures_expose_the_expected_existing_audit_sequences(monkeypatch):
    expected = {
        "expiry_routine": ["triggered", "planned", "local_task_created", "completed"],
        "preference_conflict": ["triggered", "planned", "approval_requested"],
        "guests": ["triggered"],
        "cook_mishap": ["triggered", "planned", "approved", "cook_briefed", "cooking"],
        "feedback_learning": ["triggered", "planned", "approved", "cooking", "completed"],
        "budget_constraint": ["triggered", "planned", "approval_requested"],
    }
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        for scenario, events in expected.items():
            household_id = _reset_scenario(client, scenario)
            assert [item["event"] for item in client.get(f"/api/households/{household_id}/audit").json()] == events
    app.dependency_overrides.clear()


def _reset_scenario(client: TestClient, scenario: str) -> int:
    response = client.post("/api/demo/reset", params={"scenario": scenario})
    assert response.status_code == 200
    assert response.json()["scenario"] == scenario
    return response.json()["household_id"]


def _plan_for_demo(client: TestClient, household_id: int, **changes) -> dict:
    request = {"servings": 2, "available_minutes": 45, **changes}
    response = client.post(f"/api/households/{household_id}/plan", json=request)
    assert response.status_code == 200
    return response.json()


def _recommendation(result: dict, dish_name: str) -> dict:
    return next(item for item in result["recommendations"] if item["dish"] == dish_name)


def test_expiry_fixture_prioritizes_an_expiring_ingredient(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        household_id = _reset_scenario(client, "expiry_routine")
        result = _plan_for_demo(client, household_id)
        assert result["recommendations"][0]["dish"] == "Vegetable Khichdi"
        assert result["recommendations"][0]["score_explanation"]["expiry_use"] == ["carrot"]
    app.dependency_overrides.clear()


def test_preference_conflict_fixture_keeps_health_safety_over_a_taste_request(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        household_id = _reset_scenario(client, "preference_conflict")
        preferences = client.get(f"/api/households/{household_id}/preferences").json()
        assert {item["signal"] for item in preferences} >= {"Avoid paneer tonight", "Paneer for dinner"}
        result = _plan_for_demo(client, household_id)
        paneer = next(item for item in result["exclusions"] if item["dish"] == "Paneer Bhurji")
        assert paneer["reasons"] == ["allergen present: paneer"]
    app.dependency_overrides.clear()


def test_guest_fixture_uses_guest_trigger_servings_and_approval_path(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        household_id = _reset_scenario(client, "guests")
        guest_loop = next(item for item in client.get(f"/api/households/{household_id}/meal-loops").json() if item["trigger_type"] == "guest_arrival")
        assert guest_loop["status"] == "triggered"
        assert client.post(f"/api/households/{household_id}/loops/{guest_loop['id']}/transition", json={"target_status": "planned"}).status_code == 200
        result = _plan_for_demo(client, household_id, guests=4, urgency="unexpected guests")
        assert result["context"]["servings"] == 6
        proposal = client.post(f"/api/households/{household_id}/loops/{guest_loop['id']}/propose", json={"action": "manual_purchase", "amount_inr": 137, "details": "Guest-serving ingredient gaps"})
        assert proposal.json()["tier"] == "yellow"
        assert proposal.json()["approval_id"] is not None
    app.dependency_overrides.clear()


def test_mishap_fixture_recovers_an_active_cooking_loop_with_stocked_alternative(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        household_id = _reset_scenario(client, "cook_mishap")
        mishap_loop = next(item for item in client.get(f"/api/households/{household_id}/meal-loops").json() if item["trigger_type"] == "cooking_mishap")
        assert mishap_loop["status"] == "cooking"
        result = _plan_for_demo(client, household_id)
        assert _recommendation(result, "Vegetable Khichdi")["procurement"]["route"] == "use_stock"
        outcome = client.post(f"/api/households/{household_id}/loops/{mishap_loop['id']}/outcome", json={"dish_name": "Vegetable Khichdi", "mishap": True})
        assert outcome.json() == {"status": "recovered"}
    app.dependency_overrides.clear()


def test_feedback_fixture_visibly_changes_the_later_light_dish_score(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        household_id = _reset_scenario(client, "feedback_learning")
        history = client.get(f"/api/households/{household_id}/history").json()
        assert any(item["feedback"] == "Too heavy" and item["accepted"] is False for item in history)
        learned = _plan_for_demo(client, household_id)
        learned_score = _recommendation(learned, "Vegetable Khichdi")["score"]
        learned_preference = next(item for item in client.get(f"/api/households/{household_id}/preferences").json() if "felt too heavy" in item["signal"])
        assert client.delete(f"/api/households/{household_id}/preferences/{learned_preference['id']}").status_code == 204
        without_learning = _plan_for_demo(client, household_id)
        assert learned_score == _recommendation(without_learning, "Vegetable Khichdi")["score"] + 7
    app.dependency_overrides.clear()


def test_budget_fixture_routes_the_over_cap_basket_to_manual_purchase(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        household_id = _reset_scenario(client, "budget_constraint")
        budget = client.get(f"/api/households/{household_id}/budget").json()
        assert budget["monthly_limit"] - budget["spent_amount"] - budget["planned_amount"] == 90
        result = _plan_for_demo(client, household_id)
        paneer = _recommendation(result, "Paneer Bhurji")
        khichdi = _recommendation(result, "Vegetable Khichdi")
        assert result["recommendations"][0]["dish"] == "Paneer Bhurji"
        assert paneer["procurement"]["estimated_cost_inr"] == 137
        assert paneer["procurement"]["route"] == "manual_purchase"
        assert khichdi["procurement"]["estimated_cost_inr"] == 88
        assert khichdi["procurement"]["route"] == "simulated_order"
    app.dependency_overrides.clear()


def test_invalid_demo_scenario_fails_without_resetting_existing_state(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        household_id = client.post("/api/demo/reset", params={"scenario": "guests"}).json()["household_id"]
        before = _scenario_snapshot(client, household_id)
        invalid = client.post("/api/demo/reset", params={"scenario": "does-not-exist"})
        assert invalid.status_code == 422
        assert "Unknown demo scenario" in invalid.json()["detail"]
        assert _scenario_snapshot(client, household_id) == before
    app.dependency_overrides.clear()


def test_household_profile_and_budget_crud_persist(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        household = client.post("/api/households", json={"name": "Test Home", "default_language": "Hindi"}).json()
        household_id = household["id"]
        member = client.post(f"/api/households/{household_id}/members", json={
            "name": "Mina", "language": "Hindi", "dietary_preferences": ["vegetarian"],
            "allergies": ["peanuts"], "health_constraints": ["low sodium"],
            "likes": ["dal"], "dislikes": ["mushroom"],
        })
        assert member.status_code == 201
        profile = client.put(f"/api/households/{household_id}/cook-profile", json={
            "name": "Kavita", "language": "Hindi", "skill_level": "advanced",
            "available_hours": ["18:00-20:00"], "confident_dishes": ["dal"],
        })
        budget = client.put(f"/api/households/{household_id}/budget", json={
            "monthly_limit": 10000, "spent_amount": 1200, "planned_amount": 300,
            "category_allocations": {"groceries": 8000},
        })
        assert profile.json()["skill_level"] == "advanced"
        assert budget.json()["monthly_limit"] == 10000
        assert client.get(f"/api/households/{household_id}/members").json()[0]["allergies"] == ["peanuts"]
    app.dependency_overrides.clear()


def test_inventory_and_leftover_expiry_and_update(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        household_id = client.post("/api/households", json={"name": "Expiry Home"}).json()["id"]
        inventory = client.post(f"/api/households/{household_id}/inventory", json={
            "ingredient": "spinach", "quantity": 2, "unit": "bunch", "expiry_date": str(date.today() - timedelta(days=1)),
            "storage_location": "fridge", "confirmed": True,
        }).json()
        assert inventory["expiry_status"] == "expired"
        updated = client.put(f"/api/households/{household_id}/inventory/{inventory['id']}", json={
            "ingredient": "spinach", "quantity": 1, "unit": "bunch", "expiry_date": str(date.today() + timedelta(days=1)),
            "storage_location": "fridge", "confirmed": True,
        }).json()
        assert updated["quantity"] == 1 and updated["expiry_status"] == "expiring_soon"
        leftover = client.post(f"/api/households/{household_id}/leftovers", json={
            "dish_name": "Dal", "portions": 1, "expiry_date": str(date.today()), "reuse_suggestions": ["Serve with rice"],
        }).json()
        assert leftover["expiry_status"] == "expires_today"
    app.dependency_overrides.clear()


def test_memory_records_are_retrievable_after_seed(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        household_id = client.post("/api/demo/reset").json()["household_id"]
        history = client.get(f"/api/households/{household_id}/history").json()
        preferences = client.get(f"/api/households/{household_id}/preferences").json()
        assert history[0]["dish_name"] == "Vegetable Khichdi"
        assert preferences[0]["signal"] == "Prefer light dinners on weekdays"
    app.dependency_overrides.clear()


def test_household_memory_persists_across_database_reopen(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'memory.db'}"
    first_engine = create_database_engine(type("Settings", (), {"database_url": database_url, "database_path": tmp_path / "memory.db"})())
    initialize_database(first_engine)
    with Session(first_engine) as session:
        home = Household(name="Persistent Home")
        session.add(home)
        session.commit()
        session.refresh(home)
        session.add(InventoryLot(household_id=home.id, ingredient="lentils", quantity=1, unit="kg", confirmed=True))
        session.commit()
    first_engine.dispose()
    second_engine = create_database_engine(type("Settings", (), {"database_url": database_url, "database_path": tmp_path / "memory.db"})())
    with Session(second_engine) as session:
        saved_home = session.exec(select(Household).where(Household.name == "Persistent Home")).one()
        saved_inventory = session.exec(select(InventoryLot).where(InventoryLot.household_id == saved_home.id)).one()
        assert saved_inventory.ingredient == "lentils"


def test_loop_approval_task_and_timeout_flow(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        household_id = client.post("/api/demo/reset").json()["household_id"]
        loop = client.post(f"/api/households/{household_id}/loops", json={"trigger_type": "manual"}).json()
        loop_id = loop["id"]
        assert client.post(f"/api/households/{household_id}/loops/{loop_id}/transition", json={"target_status": "planned"}).status_code == 200
        proposed = client.post(f"/api/households/{household_id}/loops/{loop_id}/propose", json={"action": "simulated_order", "amount_inr": 90}).json()
        assert proposed["tier"] == "yellow" and proposed["approval_id"]
        approved = client.post(f"/api/households/{household_id}/approvals/{proposed['approval_id']}/decision", json={"approved": True}).json()
        assert approved["status"] == "approved"
        assert client.post(f"/api/households/{household_id}/loops/{loop_id}/timeout").json()["status"] == "unclosed"
        assert len(client.get(f"/api/households/{household_id}/audit").json()) >= 4
    app.dependency_overrides.clear()


def test_outcome_closes_loop_and_updates_memory(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        household_id = client.post("/api/demo/reset").json()["household_id"]
        loop_id = client.post(f"/api/households/{household_id}/loops", json={}).json()["id"]
        client.post(f"/api/households/{household_id}/loops/{loop_id}/transition", json={"target_status": "planned"})
        client.post(f"/api/households/{household_id}/loops/{loop_id}/transition", json={"target_status": "approved"})
        outcome = client.post(f"/api/households/{household_id}/loops/{loop_id}/outcome", json={"dish_name": "Khichdi", "rating": 4, "feedback": "too heavy", "leftovers_portions": 1, "consumed": [{"ingredient": "carrot", "quantity": 1}]}).json()
        assert outcome["status"] == "completed"
        assert any(x["feedback"] == "too heavy" for x in client.get(f"/api/households/{household_id}/history").json())
        assert any(x["signal"] == "too heavy" for x in client.get(f"/api/households/{household_id}/preferences").json())
        assert client.get(f"/api/households/{household_id}/reflection").json()["meals_recorded"] >= 2
    app.dependency_overrides.clear()


def test_feedback_parser_malformed_model_output_fails_safely(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    monkeypatch.setattr(OllamaProvider, "generate_structured", lambda *_: (_ for _ in ()).throw(ValueError("bad JSON")))
    with client:
        household_id = client.post("/api/demo/reset").json()["household_id"]
        response = client.post(f"/api/households/{household_id}/feedback/parse", json={"text": "too heavy"})
        assert response.status_code == 503
        assert "manual entry" in response.json()["detail"]
    app.dependency_overrides.clear()


def test_unconfirmed_capture_is_rejected_without_inventory_mutation(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        household_id = client.post("/api/demo/reset").json()["household_id"]
        payload = {"ingredient": "coriander", "quantity": 1, "unit": "bunch", "storage_location": "fridge"}
        before = len(client.get(f"/api/households/{household_id}/inventory").json())
        rejected = client.post(f"/api/households/{household_id}/capture/confirm", json={**payload, "confirmed": False})
        assert rejected.status_code == 409
        assert len(client.get(f"/api/households/{household_id}/inventory").json()) == before
    app.dependency_overrides.clear()


def test_confirmed_capture_commits_the_expected_inventory_row(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        household_id = client.post("/api/demo/reset").json()["household_id"]
        payload = {"ingredient": "coriander", "quantity": 1, "unit": "bunch", "storage_location": "fridge", "confirmed": True}
        before = len(client.get(f"/api/households/{household_id}/inventory").json())
        captured = client.post(f"/api/households/{household_id}/capture/confirm", json={**payload, "confirmed": True}).json()
        typed = client.post(f"/api/households/{household_id}/inventory", json={**payload, "confirmed": True}).json()
        inventory = client.get(f"/api/households/{household_id}/inventory").json()
        assert len(inventory) == before + 2
        assert (captured["ingredient"], captured["quantity"], captured["unit"]) == (typed["ingredient"], typed["quantity"], typed["unit"])
    app.dependency_overrides.clear()


def test_freshness_estimates_expiry_for_typed_and_confirmed_capture(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        household_id = client.post("/api/demo/reset").json()["household_id"]
        fresh = client.post(f"/api/households/{household_id}/inventory", json={"ingredient": "tomato", "quantity": 2, "unit": "piece", "freshness": "fresh"}).json()
        soon = client.post(f"/api/households/{household_id}/capture/confirm", json={"ingredient": "onion", "quantity": 2, "unit": "piece", "freshness": "expiring_soon", "confirmed": True}).json()
        now = client.post(f"/api/households/{household_id}/capture/confirm", json={"ingredient": "coriander", "quantity": 1, "unit": "bunch", "freshness": "use_immediately", "confirmed": True}).json()
    assert fresh["freshness"] == "fresh" and fresh["expiry_date"] == str(date.today() + timedelta(days=7))
    assert soon["expiry_status"] == "expiring_soon" and soon["expiry_date"] == str(date.today() + timedelta(days=2))
    assert now["expiry_status"] == "expires_today" and now["expiry_date"] == str(date.today())
    app.dependency_overrides.clear()


def test_discover_dishes_marks_existing_recipes_and_returns_new_recipes(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    response = {"dishes": [
        {"name": "Vegetable Khichdi", "ingredients": [{"name": "rice", "quantity": 1, "unit": "cup"}], "prep_minutes": 35, "servings": 2, "nutrition_notes": ["light"], "cook_skill_required": "beginner", "rationale": "Uses rice."},
        {"name": "Homestyle Margherita Pizza", "ingredients": [{"name": "pizza dough", "quantity": 1, "unit": "piece"}, {"name": "mozzarella cheese", "quantity": 200, "unit": "g"}, {"name": "tomato sauce", "quantity": 3, "unit": "tbsp"}], "prep_minutes": 20, "servings": 2, "nutrition_notes": ["vegetarian"], "cook_skill_required": "beginner", "rationale": "Uses pizza ingredients."},
    ]}
    monkeypatch.setattr(OllamaProvider, "generate_structured", lambda *_: response)
    with client:
        household_id = client.post("/api/demo/reset").json()["household_id"]
        discovered = client.post(f"/api/households/{household_id}/discover-dishes").json()["dishes"]
        saved = client.post(f"/api/households/{household_id}/dishes", json={key: value for key, value in discovered[1].items() if key in {"name", "ingredients", "prep_minutes", "servings", "nutrition_notes", "cook_skill_required"}})
    assert discovered[0]["is_new"] is False and discovered[0]["dish_id"] is not None
    assert discovered[1]["is_new"] is True and discovered[1]["dish_id"] is None
    assert saved.status_code == 201
    app.dependency_overrides.clear()


def test_empty_inventory_discovery_returns_a_zepto_ready_starter_basket(monkeypatch):
    client, engine = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    captured_prompt: list[str] = []
    response = {"dishes": [
        {"name": "Dal Tadka", "ingredients": [{"name": "toor dal", "quantity": 1, "unit": "cup"}, {"name": "tomato", "quantity": 2, "unit": "piece"}], "prep_minutes": 30, "servings": 2, "nutrition_notes": ["vegetarian"], "cook_skill_required": "beginner", "rationale": "A healthy family staple."},
        {"name": "Paneer Bhurji", "ingredients": [{"name": "paneer", "quantity": 250, "unit": "g"}, {"name": "onion", "quantity": 1, "unit": "piece"}], "prep_minutes": 20, "servings": 2, "nutrition_notes": ["vegetarian"], "cook_skill_required": "beginner", "rationale": "Protein-rich and quick."},
        {"name": "Sambar Rice", "ingredients": [{"name": "rice", "quantity": 1, "unit": "cup"}, {"name": "sambar powder", "quantity": 2, "unit": "tbsp"}], "prep_minutes": 35, "servings": 2, "nutrition_notes": ["vegetarian"], "cook_skill_required": "beginner", "rationale": "A balanced comfort meal."},
    ]}

    def discover(*args):
        captured_prompt.append(args[1])
        return response

    monkeypatch.setattr(OllamaProvider, "generate_structured", discover)
    with client:
        household_id = client.post("/api/demo/reset").json()["household_id"]
        with Session(engine) as session:
            for lot in session.exec(select(InventoryLot).where(InventoryLot.household_id == household_id)):
                session.delete(lot)
            session.commit()
        discovered = client.post(f"/api/households/{household_id}/discover-dishes").json()["dishes"]
    assert len(discovered) == 3
    assert all(dish["missing_ingredients"] for dish in discovered)
    assert "When inventory is empty" in captured_prompt[0]
    app.dependency_overrides.clear()


def test_discovered_recipe_reports_gaps_price_estimate_and_can_request_approval(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    pizza = {"dishes": [{"name": "Pan Pizza", "ingredients": [{"name": "flour", "quantity": 300, "unit": "g"}, {"name": "tomato sauce", "quantity": 3, "unit": "tbsp"}, {"name": "cheese", "quantity": 200, "unit": "g"}, {"name": "yeast", "quantity": 1, "unit": "packet"}], "prep_minutes": 30, "servings": 2, "nutrition_notes": ["vegetarian"], "cook_skill_required": "beginner", "rationale": "Uses flour, sauce, and cheese."}]}
    monkeypatch.setattr(OllamaProvider, "generate_structured", lambda *_: pizza)
    with client:
        household_id = client.post("/api/demo/reset").json()["household_id"]
        for item in (("flour", 1, "kg"), ("tomato sauce", 3, "tbsp"), ("cheese", 200, "g")):
            client.post(f"/api/households/{household_id}/inventory", json={"ingredient": item[0], "quantity": item[1], "unit": item[2]})
        discovered = client.post(f"/api/households/{household_id}/discover-dishes").json()["dishes"][0]
        approval = client.post(f"/api/households/{household_id}/discover-dishes/approval", json={"name": discovered["name"], "ingredients": discovered["ingredients"], "servings": discovered["servings"]}).json()
        approvals = client.get(f"/api/households/{household_id}/approvals").json()
    assert discovered["missing_ingredients"] == [{"ingredient": "yeast", "needed": 1.0, "available": 0, "shortfall": 1.0, "unit": "packet", "substitution": None}]
    assert discovered["procurement"]["estimated_cost_inr"] == 25
    assert approval["status"] == "approval_requested" and approvals[-1]["amount_inr"] == 25
    app.dependency_overrides.clear()


def test_pizza_pantry_set_uses_fast_validated_recipe_and_requests_yeast_approval(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    monkeypatch.setattr(OllamaProvider, "generate_structured", lambda *_: (_ for _ in ()).throw(AssertionError("Pizza hint should not call Ollama")))
    with client:
        household_id = client.post("/api/demo/reset").json()["household_id"]
        for name, quantity, unit in (("flour", 1, "kg"), ("tomato sauce", 200, "ml"), ("cheese", 200, "g"), ("oregano", 10, "g")):
            client.post(f"/api/households/{household_id}/inventory", json={"ingredient": name, "quantity": quantity, "unit": unit})
        pizza = client.post(f"/api/households/{household_id}/discover-dishes").json()["dishes"][0]
        approval = client.post(f"/api/households/{household_id}/discover-dishes/approval", json={"name": pizza["name"], "ingredients": pizza["ingredients"], "servings": pizza["servings"]}).json()
    assert pizza["name"] == "Homestyle Margherita Pizza"
    assert [gap["ingredient"] for gap in pizza["missing_ingredients"]] == ["yeast"]
    assert pizza["procurement"]["estimated_cost_inr"] == 25
    assert approval["status"] == "approval_requested"
    app.dependency_overrides.clear()


def test_malformed_ollama_quantity_is_ignored_instead_of_causing_500(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    monkeypatch.setattr(OllamaProvider, "generate_structured", lambda *_: {"dishes": [{"name": "Rice Bowl", "ingredients": [{"name": "egg", "quantity": ": ", "unit": "piece"}, {"name": "rice", "quantity": 1, "unit": "cup"}], "prep_minutes": "20", "servings": "2"}]})
    with client:
        household_id = client.post("/api/demo/reset").json()["household_id"]
        response = client.post(f"/api/households/{household_id}/discover-dishes")
    assert response.status_code == 200
    assert response.json()["dishes"][0]["ingredients"] == [{"name": "rice", "quantity": 1.0, "unit": "cup"}]
    app.dependency_overrides.clear()


def test_zepto_status_cart_audit_and_inventory_sync_use_local_provider_contract(monkeypatch):
    client, engine = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    monkeypatch.setattr("app.api.routes.ZeptoMCPProvider.search_product", lambda *_args: [{"id": "carrot-500", "name": "Fresh Carrots 500g", "price_inr": 28, "in_stock": True}])
    monkeypatch.setattr("app.api.routes.ZeptoMCPProvider.add_items_to_cart", lambda *_args: {})
    monkeypatch.setattr("app.api.routes.ZeptoMCPProvider.get_cart", lambda *_args: {"total_amount_inr": 28, "checkout_url": "https://www.zeptonow.com/cart"})
    with client:
        household_id = client.post("/api/demo/reset").json()["household_id"]
        assert client.get(f"/api/households/{household_id}/zepto/status").json() == {"connected": False, "phone_number": None}
        with Session(engine) as session:
            session.add(ZeptoConnection(household_id=household_id, encrypted_access_token="test-token", phone_number="XXXXXX1234")); session.commit()
        cart = client.post(f"/api/households/{household_id}/zepto/cart", json={"dish_name": "Vegetable Khichdi", "missing_ingredients": [{"ingredient": "carrot", "shortfall": 2, "unit": "piece"}]}).json()
        synced = client.post(f"/api/households/{household_id}/zepto/sync-inventory", json={"items_added": cart["items_added"]}).json()
        audit = client.get(f"/api/households/{household_id}/audit").json()
    assert cart["status"] == "cart_updated" and cart["items_added"][0]["matched_product"] == "Fresh Carrots 500g"
    assert synced["items"][0]["ingredient"] == "carrot"
    assert audit[-1]["event"] == "zepto_cart_created"
    app.dependency_overrides.clear()


def test_audio_preview_supports_english_hindi_hinglish_and_manual_confirmation(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    transcript_fixtures = json.loads((FIXTURES / "capture_transcripts.json").read_text())
    responses = iter([{"transcript": item["transcript"], "language": item["language"]} for item in transcript_fixtures])
    monkeypatch.setattr(WhisperProvider, "transcribe", lambda *_args, **_kwargs: next(responses))
    monkeypatch.setattr(OllamaProvider, "generate_structured", lambda *_: {"items": [{"ingredient": "tomato", "estimated_quantity": 2, "unit": "piece", "storage_hint": "fridge", "readability_confidence": 0.6}]})
    with client:
        household_id = client.post("/api/demo/reset").json()["household_id"]
        for fixture in transcript_fixtures:
            response = client.post(f"/api/households/{household_id}/capture/audio", files={"audio": (fixture["audio_filename"], b"\x1aE\xdf\xa3" + fixture["audio_content"].encode(), "audio/webm")})
            assert response.status_code == 200
            assert response.json()["requires_confirmation"] is True
            assert response.json()["candidates"][0]["readability_confidence"] == 0.6
        corrected = client.post(f"/api/households/{household_id}/capture/confirm", json={"ingredient": "coriander", "quantity": 1, "unit": "bunch", "storage_location": "fridge", "confirmed": True})
        assert corrected.status_code == 201
        assert corrected.json()["ingredient"] == "coriander"
    app.dependency_overrides.clear()


def test_image_preview_requires_review_without_inventory_mutation(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    monkeypatch.setattr(VisionProvider, "extract_inventory", lambda *_: {"items": [{"ingredient": "milk", "estimated_quantity": 1, "unit": "packet", "expiry_date": None, "storage_hint": "fridge", "readability_confidence": 0.2}]})
    with client:
        household_id = client.post("/api/demo/reset").json()["household_id"]
        before = len(client.get(f"/api/households/{household_id}/inventory").json())
        photo = client.post(f"/api/households/{household_id}/capture/image", files={"image": ("fridge-photo.ppm", (FIXTURES / "fridge-photo.ppm").read_bytes(), "image/x-portable-pixmap")})
        assert photo.status_code == 200
        assert photo.json()["candidates"][0]["readability_confidence"] == 0.2
        assert len(client.get(f"/api/households/{household_id}/inventory").json()) == before
    app.dependency_overrides.clear()


def test_unavailable_providers_return_typed_fallback_without_ai_candidates(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    monkeypatch.setattr(WhisperProvider, "transcribe", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("faster-whisper is unavailable; use typed inventory entry")))
    monkeypatch.setattr(VisionProvider, "extract_inventory", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("Local vision model is unavailable; use typed inventory entry")))
    with client:
        household_id = client.post("/api/demo/reset").json()["household_id"]
        before = len(client.get(f"/api/households/{household_id}/inventory").json())
        audio = client.post(f"/api/households/{household_id}/capture/audio", files={"audio": ("note.aac", (FIXTURES / "audi_test.aac").read_bytes(), "audio/aac")}).json()
        image = client.post(f"/api/households/{household_id}/capture/image", files={"image": ("fridge-photo.ppm", (FIXTURES / "fridge-photo.ppm").read_bytes(), "image/x-portable-pixmap")}).json()
        for preview, source in ((audio, "audio"), (image, "image")):
            assert preview["source"] == source
            assert "typed inventory" in preview["fallback"]
            assert preview["candidates"] == []
        assert len(client.get(f"/api/households/{household_id}/inventory").json()) == before
    app.dependency_overrides.clear()


def test_whisper_provider_loads_models_from_local_cache_only(monkeypatch):
    import sys
    from types import SimpleNamespace

    captured: dict[str, object] = {}

    class FakeWhisperModel:
        def __init__(self, *_args, **kwargs):
            captured.update(kwargs)

        def transcribe(self, *_args, **_kwargs):
            return iter([SimpleNamespace(text="local transcript")]), SimpleNamespace(language="en")

    monkeypatch.setitem(sys.modules, "faster_whisper", SimpleNamespace(WhisperModel=FakeWhisperModel))
    assert WhisperProvider("small").transcribe(b"audio", suffix=".aac")["transcript"] == "local transcript"
    assert captured["local_files_only"] is True


def test_bad_capture_inputs_return_4xx_without_inventory_mutation(monkeypatch):
    client, _ = make_client(monkeypatch, OllamaHealth("available", "qwen3:4b"))
    with client:
        household_id = client.post("/api/demo/reset").json()["household_id"]
        before = len(client.get(f"/api/households/{household_id}/inventory").json())
        cases = [
            (f"/api/households/{household_id}/capture/image", "image", ("bad.txt", b"x", "text/plain"), 415),
            (f"/api/households/{household_id}/capture/image", "image", ("corrupt.jpg", b"not-a-photo", "image/jpeg"), 422),
            (f"/api/households/{household_id}/capture/audio", "audio", ("empty.webm", b"", "audio/webm"), 422),
            (f"/api/households/{household_id}/capture/audio", "audio", ("malformed.aac", b"not-audio", "audio/aac"), 422),
            (f"/api/households/{household_id}/capture/audio", "audio", ("oversized.aac", b"0" * (25 * 1024 * 1024 + 1), "audio/aac"), 422),
        ]
        for path, field, file, status in cases:
            assert client.post(path, files={field: file}).status_code == status
            assert len(client.get(f"/api/households/{household_id}/inventory").json()) == before
    app.dependency_overrides.clear()


def test_structured_json_validation_rejects_malformed_output():
    provider = OllamaProvider("http://unused", "qwen3:4b")
    assert provider.validate_structured_json({"response": '{"language":"hi"}'}) == {"language": "hi"}
    for payload in ({}, {"response": "not json"}, {"response": "[]"}):
        try:
            provider.validate_structured_json(payload)
        except ValueError:
            pass
        else:
            raise AssertionError("Malformed structured output should be rejected")


def test_ollama_provider_handles_missing_model_and_invalid_generated_json(monkeypatch):
    from app.providers import ollama

    missing_model = FakeOllamaClient([FakeResponse({"models": []})])
    monkeypatch.setattr(ollama.httpx, "Client", lambda **_: missing_model)
    assert OllamaProvider("http://unused", "qwen3:4b").health().status == "model_unavailable"

    invalid_json = FakeOllamaClient([
        FakeResponse({"models": [{"name": "qwen3:4b"}]}),
        FakeResponse({"response": "not JSON"}),
    ])
    monkeypatch.setattr(ollama.httpx, "Client", lambda **_: invalid_json)
    assert OllamaProvider("http://unused", "qwen3:4b").health().status == "invalid_response"
