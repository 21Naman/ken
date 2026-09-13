"""Minimal Streamable-HTTP MCP adapter for Zepto.

The live server's OAuth client metadata is deployment-specific, so credentials
and OAuth endpoints are supplied through local environment settings. This keeps
tokens out of the browser and makes mocked tests deterministic.
"""
from __future__ import annotations

import base64
import hashlib
import json
import secrets
from typing import Any
from urllib.parse import urlencode

from cryptography.fernet import Fernet, InvalidToken
import httpx

from app.settings import Settings


class ZeptoMCPError(RuntimeError):
    pass


class ZeptoMCPProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    def _cipher(self) -> Fernet:
        if not self.settings.zepto_token_encryption_key:
            raise ZeptoMCPError("Zepto is not configured. Add OAuth settings and HOUSEHOLD_ZEPTO_TOKEN_ENCRYPTION_KEY to .env.")
        try:
            return Fernet(self.settings.zepto_token_encryption_key.encode())
        except (TypeError, ValueError) as exc:
            raise ZeptoMCPError("Zepto token encryption key is invalid.") from exc

    def encrypt_token(self, token: str) -> str:
        return self._cipher().encrypt(token.encode()).decode()

    def decrypt_token(self, token: str) -> str:
        try:
            return self._cipher().decrypt(token.encode()).decode()
        except InvalidToken as exc:
            raise ZeptoMCPError("The stored Zepto connection is invalid. Reconnect your account.") from exc

    def is_connected(self, household_id: int, encrypted_token: str | None = None) -> bool:
        """The route supplies the household-scoped stored token; no global token exists."""
        return bool(household_id and encrypted_token)

    @staticmethod
    def pkce_verifier() -> str:
        return secrets.token_urlsafe(48)

    @staticmethod
    def pkce_challenge(verifier: str) -> str:
        return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()

    def get_auth_url(self, household_id: int, redirect_uri: str, state: str | None = None, code_verifier: str | None = None) -> str:
        state = state or secrets.token_urlsafe(24)
        code_verifier = code_verifier or self.pkce_verifier()
        if self.settings.zepto_mock_enabled:
            return f"{redirect_uri}?{urlencode({'code': 'mock-zepto-token', 'state': state, 'mock': '1'})}"
        if not (self.settings.zepto_client_id and self.settings.zepto_oauth_authorization_url):
            raise ZeptoMCPError("Zepto OAuth is not configured. Add HOUSEHOLD_ZEPTO_CLIENT_ID and HOUSEHOLD_ZEPTO_OAUTH_AUTHORIZATION_URL to .env.")
        return f"{self.settings.zepto_oauth_authorization_url}?{urlencode({'client_id': self.settings.zepto_client_id, 'redirect_uri': redirect_uri, 'response_type': 'code', 'state': state, 'code_challenge': self.pkce_challenge(code_verifier), 'code_challenge_method': 'S256'})}"

    def exchange_code(self, code: str, code_verifier: str) -> tuple[str, str | None]:
        if self.settings.zepto_mock_enabled:
            return self.encrypt_token("mock-zepto-token"), "XXXXXX1234"
        if not (self.settings.zepto_client_id and self.settings.zepto_oauth_token_url):
            raise ZeptoMCPError("Zepto OAuth token exchange is not configured.")
        body: dict[str, str] = {"client_id": self.settings.zepto_client_id, "code": code, "redirect_uri": self.settings.zepto_redirect_uri, "grant_type": "authorization_code", "code_verifier": code_verifier}
        if self.settings.zepto_client_secret:
            body["client_secret"] = self.settings.zepto_client_secret
        try:
            response = httpx.post(self.settings.zepto_oauth_token_url, data=body, timeout=self.settings.request_timeout_seconds)
            response.raise_for_status()
            payload = response.json()
            token = payload.get("access_token")
            if not isinstance(token, str):
                raise ZeptoMCPError("Zepto OAuth did not return an access token.")
            return self.encrypt_token(token), payload.get("phone_number") if isinstance(payload.get("phone_number"), str) else None
        except (httpx.HTTPError, ValueError) as exc:
            raise ZeptoMCPError("Zepto OAuth token exchange failed.") from exc

    def _mock_product(self, query: str) -> dict[str, Any]:
        return {"id": f"mock-{query.casefold().replace(' ', '-')}", "name": f"Fresh {query.title()}", "price_inr": 30, "pack_size": "1 pack", "image": None, "in_stock": True}

    def _tool_call(self, token: str, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if self.settings.zepto_mock_enabled:
            if name == "search_products": return {"products": [self._mock_product(str(arguments.get("query", "item")))]}
            if name == "cart_management": return {"cart": {"items": arguments.get("items", []), "delivery_charges": 0}}
            if name == "place_order": return {"payment_url": "upi://pay?pa=mock@zepto", "checkout_url": "https://www.zeptonow.com/cart"}
            return {"items": [], "total_amount_inr": 0, "delivery_charges": 0}
        request = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
        try:
            response = httpx.post(self.settings.zepto_mcp_url, json=request, headers={"Authorization": f"Bearer {token}", "Accept": "application/json, text/event-stream"}, timeout=self.settings.request_timeout_seconds)
            response.raise_for_status()
            text = response.text
            if text.startswith("data:"):
                text = next((line.removeprefix("data:").strip() for line in text.splitlines() if line.startswith("data:")), "{}")
            payload = json.loads(text)
            if payload.get("error"):
                raise ZeptoMCPError(str(payload["error"]))
            result = payload.get("result", {})
            if isinstance(result.get("structuredContent"), dict): return result["structuredContent"]
            for block in result.get("content", []):
                if isinstance(block, dict) and block.get("type") == "text":
                    try: return json.loads(block.get("text", "{}"))
                    except json.JSONDecodeError: continue
            return result if isinstance(result, dict) else {}
        except (httpx.HTTPError, ValueError) as exc:
            raise ZeptoMCPError("Zepto MCP request failed. Reconnect your account or try again.") from exc

    def search_product(self, encrypted_token: str, query: str) -> list[dict[str, Any]]:
        result = self._tool_call(self.decrypt_token(encrypted_token), "search_products", {"query": query})
        products = result.get("products", result.get("items", []))
        return [item for item in products if isinstance(item, dict)] if isinstance(products, list) else []

    def add_items_to_cart(self, encrypted_token: str, items: list[dict[str, Any]]) -> dict[str, Any]:
        return self._tool_call(self.decrypt_token(encrypted_token), "cart_management", {"action": "add", "items": items})

    def get_cart(self, encrypted_token: str) -> dict[str, Any]:
        return self._tool_call(self.decrypt_token(encrypted_token), "cart_management", {"action": "get"})

    def create_order_payment(self, encrypted_token: str, payment_method: str = "upi") -> dict[str, Any]:
        return self._tool_call(self.decrypt_token(encrypted_token), "place_order", {"payment_method": payment_method})
