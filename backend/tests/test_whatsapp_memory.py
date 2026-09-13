"""WhatsApp -> household memory: feedback, plans, inventory land on the website."""

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.domain.whatsapp_memory import process_text as process_whatsapp_message
from app.models import AuditEvent, Household, InventoryLot, MealLoopRecord, PreferenceSignal


class FakeProvider:
    def __init__(self, structured=None, text="chat reply"):
        self.structured = structured
        self.text = text

    def generate_structured(self, prompt):
        if isinstance(self.structured, Exception):
            raise self.structured
        return self.structured

    def generate_text(self, prompt):
        return self.text


def make_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    session = Session(engine)
    session.add(Household(name="Test"))
    session.commit()
    return session


def test_feedback_saves_preference_signal():
    session = make_session()
    provider = FakeProvider(
        structured={"intent": "feedback", "sentiment": "positive", "items": []}
    )
    reply = process_whatsapp_message(session, provider, "loved the pizza", "9191")
    signals = session.exec(select(PreferenceSignal)).all()
    assert len(signals) == 1
    assert signals[0].sentiment == "positive"
    assert "whatsapp" in (signals[0].context or "")
    assert "saved" in reply.lower()


def test_plan_creates_meal_loop():
    session = make_session()
    provider = FakeProvider(structured={"intent": "plan", "items": []})
    reply = process_whatsapp_message(session, provider, "plan dinner for tonight", "9191")
    loops = session.exec(select(MealLoopRecord)).all()
    assert len(loops) == 1
    assert loops[0].trigger_type == "whatsapp"
    assert loops[0].status == "triggered"
    assert session.exec(select(AuditEvent)).all()
    assert reply


def test_inventory_staged_unconfirmed():
    session = make_session()
    provider = FakeProvider(
        structured={
            "intent": "inventory",
            "items": [{"ingredient": "milk", "quantity": 2, "unit": "L"}],
        }
    )
    reply = process_whatsapp_message(session, provider, "bought 2L milk", "9191")
    lots = session.exec(select(InventoryLot)).all()
    assert len(lots) == 1
    assert lots[0].ingredient == "milk"
    assert lots[0].confirmed is False
    assert "milk" in reply.lower()


def test_chat_writes_nothing():
    session = make_session()
    provider = FakeProvider(structured={"intent": "chat"}, text="hi!")
    reply = process_whatsapp_message(session, provider, "hey there", "9191")
    assert reply == "hi!"
    assert session.exec(select(PreferenceSignal)).all() == []
    assert session.exec(select(MealLoopRecord)).all() == []
    assert session.exec(select(InventoryLot)).all() == []


def test_classifier_failure_falls_back_to_chat():
    session = make_session()
    provider = FakeProvider(structured=ValueError("bad json"), text="fallback reply")
    reply = process_whatsapp_message(session, provider, "blah", "9191")
    assert reply == "fallback reply"
    assert session.exec(select(PreferenceSignal)).all() == []
    assert session.exec(select(MealLoopRecord)).all() == []
    assert session.exec(select(InventoryLot)).all() == []


def test_missing_household_falls_back_to_chat():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    session = Session(engine)
    provider = FakeProvider(structured={"intent": "feedback"}, text="chat only")
    reply = process_whatsapp_message(session, provider, "loved it", "9191")
    assert reply == "chat only"
    assert session.exec(select(PreferenceSignal)).all() == []
