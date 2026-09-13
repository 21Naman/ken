from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class OllamaHealth:
    status: str
    model: str
    detail: str | None = None


class OllamaProvider:
    """Small local-only health adapter; it never makes business decisions."""

    def __init__(self, base_url: str, model: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def health(self) -> OllamaHealth:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPError as exc:
            return OllamaHealth("unavailable", self.model, str(exc))
        except ValueError:
            return OllamaHealth("invalid_response", self.model, "Ollama returned invalid JSON")

        if not isinstance(payload, dict) or not isinstance(payload.get("models"), list):
            return OllamaHealth("invalid_response", self.model, "Ollama response lacks a models list")
        available_models = {
            entry.get("name") for entry in payload["models"] if isinstance(entry, dict) and isinstance(entry.get("name"), str)
        }
        if self.model not in available_models:
            return OllamaHealth("model_unavailable", self.model, f"Pull the local model with: ollama pull {self.model}")
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": 'Return exactly this JSON object: {"health":"ok"}',
                        "format": "json",
                        "think": False,
                        "stream": False,
                        "options": {"temperature": 0},
                    },
                )
                response.raise_for_status()
                self.validate_structured_json(response.json())
        except httpx.HTTPError as exc:
            return OllamaHealth("unavailable", self.model, f"Model verification failed: {exc}")
        except ValueError as exc:
            return OllamaHealth("invalid_response", self.model, str(exc))
        return OllamaHealth("available", self.model)

    def validate_structured_json(self, payload: Any) -> dict[str, Any]:
        """Validate the response shape used by later language-only features."""
        if not isinstance(payload, dict):
            raise ValueError("Expected a JSON object from Ollama")
        response = payload.get("response")
        if not isinstance(response, str):
            raise ValueError("Ollama JSON response must include a string response field")
        try:
            decoded = __import__("json").loads(response)
        except (TypeError, ValueError) as exc:
            raise ValueError("Ollama response field does not contain valid JSON") from exc
        if not isinstance(decoded, dict):
            raise ValueError("Structured Ollama output must be a JSON object")
        return decoded

    def generate_structured(self, prompt: str) -> dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(f"{self.base_url}/api/generate", json={"model": self.model, "prompt": prompt, "format": "json", "think": False, "stream": False, "options": {"temperature": 0}})
            response.raise_for_status()
            return self.validate_structured_json(response.json())
