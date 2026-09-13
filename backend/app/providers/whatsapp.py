from __future__ import annotations

import httpx

from app.settings import get_settings

import logging

logger = logging.getLogger(__name__)


def send_whatsapp_message(to: str, body: str) -> None:
    """Send a text reply via Meta WhatsApp Cloud API. Raises on HTTP failure."""
    settings = get_settings()
    if not settings.whatsapp_access_token or not settings.whatsapp_phone_number_id:
        raise RuntimeError("WhatsApp is not configured: set access token and phone number ID")
    url = (
        f"https://graph.facebook.com/{settings.whatsapp_api_version}"
        f"/{settings.whatsapp_phone_number_id}/messages"
    )
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            url,
            headers={
                "Authorization": f"Bearer {settings.whatsapp_access_token}",
                "Content-Type": "application/json",
            },
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": body[:4096]},
            },
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.warning("whatsapp send to %s failed: %s", to, response.text[:500])
            raise
