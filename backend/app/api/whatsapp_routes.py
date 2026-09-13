from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.domain.whatsapp_agent import run_whatsapp_agent
from app.providers.whatsapp import send_whatsapp_message
from app.settings import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/whatsapp", tags=["whatsapp"])

# In-process duplicate protection so Meta retries don't double-reply.
_seen_message_ids: set[str] = set()


@router.get("")
@router.get("/")
def verify(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
) -> PlainTextResponse:
    settings = get_settings()
    if (
        hub_mode == "subscribe"
        and hub_verify_token
        and hub_verify_token == settings.whatsapp_verify_token
        and hub_challenge is not None
    ):
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="WhatsApp verification failed")


@router.post("")
@router.post("/")
async def receive(request: Request, background: BackgroundTasks) -> dict[str, str]:
    try:
        payload: Any = await request.json()
    except ValueError:
        logger.warning("whatsapp: invalid JSON payload")
        return {"status": "ok"}
    if not isinstance(payload, dict):
        return {"status": "ok"}

    try:
        for entry in payload.get("entry", []) or []:
            for change in (entry or {}).get("changes", []) or []:
                value = (change or {}).get("value", {}) or {}
                for message in value.get("messages", []) or []:
                    # Reply in the background so Meta gets its 200 instantly,
                    # even when the local model needs a minute to think.
                    background.add_task(_handle_message, message)
    except Exception:  # noqa: BLE001 - never let a webhook crash into Meta retries
        logger.exception("whatsapp: failed to process payload")
    return {"status": "ok"}


def _handle_message(message: dict[str, Any]) -> None:
    msg_id = str(message.get("id", ""))
    if msg_id and msg_id in _seen_message_ids:
        return
    if msg_id:
        _seen_message_ids.add(msg_id)

    if message.get("type") != "text":
        return
    text = ((message.get("text") or {}).get("body") or "").strip()
    wa_id = str(message.get("from", "")).strip()
    if not text or not wa_id:
        return

    try:
        reply = run_whatsapp_agent(text, wa_id)
        send_whatsapp_message(wa_id, reply)
    except Exception:  # noqa: BLE001 - Meta expects 200; log and swallow
        logger.exception("whatsapp: agent or send failed for %s", wa_id)
