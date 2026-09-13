from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

from sqlmodel import Session

from app.database import engine
from app.models import AuditEvent, Household, InventoryLot, MealLoopRecord, PreferenceSignal
from app.providers.ollama import OllamaProvider
from app.settings import get_settings

logger = logging.getLogger(__name__)

HOUSEHOLD_ID = 1

CLASSIFY_PROMPT = (
    "Classify this WhatsApp message for a household assistant. Return JSON only: "
    '{"intent": one of feedback|plan|inventory|chat, '
    '"sentiment": positive|negative|neutral, '
    '"items": [{"ingredient": string, "quantity": number, "unit": string}]}. '
    "feedback = an opinion about food or dishes. "
    "plan = wants a meal planned, cooked, or ordered. "
    "inventory = bought or added groceries. Otherwise chat. Message: "
)


def _default_provider() -> OllamaProvider:
    settings = get_settings()
    return OllamaProvider(
        settings.ollama_base_url,
        settings.ollama_model,
        settings.whatsapp_agent_timeout_seconds,
    )


def classify(text: str, provider: Any) -> dict[str, Any]:
    """Best-effort intent classification; anything unexpected means chat."""
    try:
        result = provider.generate_structured(CLASSIFY_PROMPT + text)
    except Exception:  # noqa: BLE001 - local model may be slow or malformed
        return {"intent": "chat"}
    if not isinstance(result, dict):
        return {"intent": "chat"}
    if result.get("intent") not in {"feedback", "plan", "inventory", "chat"}:
        return {"intent": "chat"}
    return result


def _chat(text: str, wa_id: str, provider: Any) -> str:
    try:
        reply = provider.generate_text(
            "You are the household assistant for household 1. "
            "Reply concisely in the user's language (English/Hindi/Hinglish). "
            f"WhatsApp user {wa_id} says: {text}"
        ).strip()
    except Exception:  # noqa: BLE001 - never break the webhook on model errors
        logger.exception("whatsapp: chat reply failed for %s", wa_id)
        return "Sorry, I could not generate a reply right now."
    return reply or "Sorry, I could not generate a reply right now."


def _save_feedback(
    session: Session, text: str, wa_id: str, data: dict[str, Any]
) -> str:
    sentiment = str(data.get("sentiment") or "neutral").strip().lower()
    if sentiment not in {"positive", "negative", "neutral"}:
        sentiment = "neutral"
    session.add(
        PreferenceSignal(
            household_id=HOUSEHOLD_ID,
            signal=text[:1000],
            sentiment=sentiment,
            context=f"whatsapp:{wa_id}",
        )
    )
    session.commit()
    return (
        f"Saved your feedback ({sentiment}) — you'll see it reflected "
        "in preferences on the dashboard."
    )


def _start_plan(session: Session, text: str, wa_id: str) -> str:
    loop = MealLoopRecord(
        household_id=HOUSEHOLD_ID,
        trigger_type="whatsapp",
        context_note=text[:1000],
        status="triggered",
    )
    session.add(loop)
    session.flush()
    assert loop.id is not None
    session.add(
        AuditEvent(
            household_id=HOUSEHOLD_ID,
            meal_loop_id=loop.id,
            event="triggered",
            detail=f"whatsapp:{wa_id}",
        )
    )
    session.commit()
    return (
        "Noted — created a meal request. Continue it from meal-loops on the dashboard."
    )


def _stage_inventory(
    session: Session, text: str, wa_id: str, data: dict[str, Any]
) -> str:
    raw_items = data.get("items")
    items: list[dict[str, Any]] = []
    if isinstance(raw_items, list):
        for raw in raw_items:
            if not isinstance(raw, dict):
                continue
            name = str(raw.get("ingredient", "")).strip()
            try:
                quantity = float(raw.get("quantity", 0))
            except (TypeError, ValueError):
                continue
            if not name or quantity <= 0:
                continue
            items.append(
                {
                    "ingredient": name[:120],
                    "quantity": quantity,
                    "unit": str(raw.get("unit", "item")).strip()[:32] or "item",
                }
            )
    if not items:
        return (
            "I couldn't pick out grocery items — try like 'bought 2 L milk'."
        )
    today = date.today()
    for item in items:
        session.add(
            InventoryLot(
                household_id=HOUSEHOLD_ID,
                ingredient=item["ingredient"],
                quantity=item["quantity"],
                unit=item["unit"],
                purchased_on=today,
                expiry_date=today + timedelta(days=7),
                freshness="fresh",
                storage_location="pantry",
                confirmed=False,
            )
        )
    session.commit()
    staged = ", ".join(f'{item["quantity"]:g} {item["unit"]} {item["ingredient"]}' for item in items)
    _ = (text, wa_id)
    return (
        f"Staged for review: {staged}. Confirm them on the dashboard inventory page."
    )


def process_text(
    session: Session, provider: Any, text: str, wa_id: str
) -> str:
    """Classify a message and persist feedback/plans/inventory. Never raises."""
    if session.get(Household, HOUSEHOLD_ID) is None:
        return _chat(text, wa_id, provider)
    data = classify(text, provider)
    try:
        if data["intent"] == "feedback":
            return _save_feedback(session, text, wa_id, data)
        if data["intent"] == "plan":
            return _start_plan(session, text, wa_id)
        if data["intent"] == "inventory":
            return _stage_inventory(session, text, wa_id, data)
    except Exception:  # noqa: BLE001 - writes are best-effort; reply must survive
        logger.exception("whatsapp: memory write failed for %s", wa_id)
        session.rollback()
    return _chat(text, wa_id, provider)


def process_whatsapp_message(text: str, wa_id: str) -> str:
    """Entry point for the webhook: own session, local model, reply text."""
    session = Session(engine)
    try:
        return process_text(session, _default_provider(), text, wa_id)
    finally:
        session.close()
