from __future__ import annotations

from app.providers.ollama import OllamaProvider
from app.settings import get_settings


def run_whatsapp_agent(text: str, wa_id: str) -> str:
    """Thin conversational wrapper around the existing local Ollama model.

    Existing planner/discovery/brief logic is unchanged; this only adds a
    plain-text chat entrypoint for WhatsApp, scoped to default household 1.
    """
    settings = get_settings()
    provider = OllamaProvider(
        settings.ollama_base_url,
        settings.ollama_model,
        settings.whatsapp_agent_timeout_seconds,
    )
    prompt = (
        "You are the household assistant for household 1. "
        "Reply concisely in the user's language (English/Hindi/Hinglish). "
        f"WhatsApp user {wa_id} says: {text}"
    )
    reply = provider.generate_text(prompt).strip()
    return reply or "Sorry, I could not generate a reply right now."
