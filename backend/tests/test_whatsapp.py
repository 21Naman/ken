from fastapi.testclient import TestClient

from app.main import app
from app.settings import get_settings


def _client_with_whatsapp(monkeypatch):
    settings = get_settings()
    settings.whatsapp_verify_token = "test-verify"
    settings.whatsapp_access_token = "test-token"
    settings.whatsapp_phone_number_id = "12345"
    settings.whatsapp_api_version = "v22.0"
    monkeypatch.setattr("app.api.whatsapp_routes.get_settings", lambda: settings)
    # clear dedupe between tests
    from app.api import whatsapp_routes

    whatsapp_routes._seen_message_ids.clear()
    return TestClient(app)


def _payload(msg_id="wamid.1", body="hello", from_wa="919999999999"):
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": msg_id,
                                    "from": from_wa,
                                    "type": "text",
                                    "text": {"body": body},
                                }
                            ]
                        }
                    }
                ]
            }
        ],
    }


def test_verify_success(monkeypatch):
    client = _client_with_whatsapp(monkeypatch)
    resp = client.get(
        "/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "test-verify",
            "hub.challenge": "12345",
        },
    )
    assert resp.status_code == 200
    assert resp.text == "12345"


def test_verify_forbidden(monkeypatch):
    client = _client_with_whatsapp(monkeypatch)
    resp = client.get(
        "/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong",
            "hub.challenge": "12345",
        },
    )
    assert resp.status_code == 403


def test_post_text_calls_agent_and_sender(monkeypatch):
    client = _client_with_whatsapp(monkeypatch)
    calls = {}

    def fake_agent(text, wa_id):
        calls["agent"] = (text, wa_id)
        return "hi there"

    sent = []

    def fake_send(to, body):
        sent.append((to, body))

    monkeypatch.setattr("app.api.whatsapp_routes.run_whatsapp_agent", fake_agent)
    monkeypatch.setattr("app.api.whatsapp_routes.send_whatsapp_message", fake_send)

    resp = client.post("/webhooks/whatsapp", json=_payload())
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
    assert calls["agent"] == ("hello", "919999999999")
    assert sent == [("919999999999", "hi there")]


def test_post_duplicate_ignored(monkeypatch):
    client = _client_with_whatsapp(monkeypatch)
    monkeypatch.setattr(
        "app.api.whatsapp_routes.run_whatsapp_agent", lambda text, wa_id: "reply"
    )
    sent = []
    monkeypatch.setattr(
        "app.api.whatsapp_routes.send_whatsapp_message",
        lambda to, body: sent.append((to, body)),
    )

    assert client.post("/webhooks/whatsapp", json=_payload(msg_id="dup-1")).status_code == 200
    assert client.post("/webhooks/whatsapp", json=_payload(msg_id="dup-1")).status_code == 200
    assert len(sent) == 1


def test_post_status_update_ignored(monkeypatch):
    client = _client_with_whatsapp(monkeypatch)
    called = []
    monkeypatch.setattr(
        "app.api.whatsapp_routes.run_whatsapp_agent",
        lambda text, wa_id: called.append((text, wa_id)) or "x",
    )
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{"changes": [{"value": {"statuses": [{"id": "wamid.1"}]}}]}],
    }
    resp = client.post("/webhooks/whatsapp", json=payload)
    assert resp.status_code == 200
    assert called == []
