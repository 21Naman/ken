"""Demo WhatsApp console: same pipeline, no Meta needed."""

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.database import get_session
from app.main import app
from app.models import Household, PreferenceSignal


class FakeProvider:
    def __init__(self, structured=None, text="demo reply"):
        self.structured = structured
        self.text = text

    def generate_structured(self, prompt):
        if isinstance(self.structured, Exception):
            raise self.structured
        return self.structured

    def generate_text(self, prompt):
        return self.text


def make_client(monkeypatch, provider):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(Household(name="Demo"))
        session.commit()

    def session_override():
        with Session(engine) as session:
            yield session

    monkeypatch.setattr(
        "app.domain.whatsapp_memory._default_provider", lambda: provider
    )
    app.dependency_overrides[get_session] = session_override
    return TestClient(app), engine


def test_demo_page_loads(monkeypatch):
    client, _ = make_client(monkeypatch, FakeProvider())
    try:
        resp = client.get("/demo/whatsapp")
    finally:
        app.dependency_overrides.clear()
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "WhatsApp Demo" in resp.text
    assert "inventory-live" in resp.text


def test_demo_send_feedback_saves_and_replies(monkeypatch):
    provider = FakeProvider(structured={"intent": "feedback", "sentiment": "positive"})
    client, engine = make_client(monkeypatch, provider)
    try:
        resp = client.post("/demo/whatsapp/send", json={"text": "loved the pizza"})
    finally:
        app.dependency_overrides.clear()
    assert resp.status_code == 200
    assert "saved" in resp.json()["reply"].lower()
    with Session(engine) as session:
        signals = session.exec(select(PreferenceSignal)).all()
    assert len(signals) == 1
    assert signals[0].sentiment == "positive"


def test_demo_send_chat_replies_without_writes(monkeypatch):
    provider = FakeProvider(structured={"intent": "chat"}, text="hey!")
    client, engine = make_client(monkeypatch, provider)
    try:
        resp = client.post("/demo/whatsapp/send", json={"text": "hello"})
    finally:
        app.dependency_overrides.clear()
    assert resp.status_code == 200
    assert resp.json()["reply"] == "hey!"
    with Session(engine) as session:
        assert session.exec(select(PreferenceSignal)).all() == []


def test_demo_send_rejects_empty(monkeypatch):
    client, _ = make_client(monkeypatch, FakeProvider())
    try:
        resp = client.post("/demo/whatsapp/send", json={"text": "   "})
    finally:
        app.dependency_overrides.clear()
    assert resp.status_code == 422


def test_demo_inventory_returns_lots(monkeypatch):
    from app.models import InventoryLot

    client, engine = make_client(monkeypatch, FakeProvider())
    with Session(engine) as session:
        session.add(
            InventoryLot(household_id=1, ingredient="milk", quantity=2, unit="L")
        )
        session.commit()
    try:
        resp = client.get("/demo/whatsapp/inventory")
    finally:
        app.dependency_overrides.clear()
    assert resp.status_code == 200
    items = resp.json()["inventory"]
    assert {"ingredient": "milk", "quantity": 2, "unit": "L"} == {
        k: items[0][k] for k in ("ingredient", "quantity", "unit")
    }
