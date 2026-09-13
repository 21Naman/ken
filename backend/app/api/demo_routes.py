from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlmodel import Session

from app.database import get_session
from app.domain.whatsapp_memory import _default_provider, process_text

router = APIRouter(prefix="/demo/whatsapp", tags=["demo"])

DEMO_WA_ID = "demo-user"

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WhatsApp Demo — Household Agent</title>
<style>
  body { font-family: system-ui, sans-serif; background: #0b141a; color: #e9edef; margin: 0; display: flex; justify-content: center; }
  .phone { width: min(480px, 100vw); height: 100vh; display: flex; flex-direction: column; background: #0b141a; }
  header { background: #075e54; padding: 0.8rem 1rem; }
  header b { display: block; } header small { color: #cfd8dc; }
  .banner { background: #453a12; color: #ffe082; font-size: 0.8rem; padding: 0.4rem 1rem; }
  #chat { flex: 1; overflow-y: auto; padding: 1rem; display: flex; flex-direction: column; gap: 0.5rem; }
  .me { align-self: flex-end; background: #005c4b; padding: 0.5rem 0.8rem; border-radius: 0.6rem; max-width: 80%; }
  .bot { align-self: flex-start; background: #1f2c34; padding: 0.5rem 0.8rem; border-radius: 0.6rem; max-width: 80%; }
  form { display: flex; padding: 0.6rem; gap: 0.5rem; }
  input { flex: 1; border-radius: 1.2rem; border: none; padding: 0.6rem 1rem; font-size: 1rem; }
  button { border-radius: 50%; border: none; background: #00a884; color: white; width: 2.6rem; height: 2.6rem; font-size: 1.2rem; }
</style>
</head>
<body>
<div class="phone">
  <header><b>Household Agent</b><small>WhatsApp Demo — simulated, same pipeline as the Meta webhook</small></header>
  <div class="banner">DEMO: messages here run the real agent and write to household memory. No Meta involved.</div>
  <div id="chat"></div>
  <form id="f"><input id="t" autocomplete="off" placeholder="Type a message"><button>&#10148;</button></form>
</div>
<script>
const chat = document.getElementById('chat');
document.getElementById('f').onsubmit = async (e) => {
  e.preventDefault();
  const t = document.getElementById('t');
  const text = t.value.trim();
  if (!text) return;
  t.value = '';
  chat.innerHTML += `<div class="me">${text.replace(/</g, '&lt;')}</div>`;
  chat.scrollTop = chat.scrollHeight;
  const r = await fetch('/demo/whatsapp/send', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text}),
  });
  const data = await r.json();
  chat.innerHTML += `<div class="bot">${(data.reply || '...').replace(/</g, '&lt;')}</div>`;
  chat.scrollTop = chat.scrollHeight;
};
</script>
</body>
</html>
"""


class DemoSend(BaseModel):
    text: str


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def demo_page() -> HTMLResponse:
    return HTMLResponse(PAGE)


@router.post("/send")
def demo_send(
    payload: DemoSend, session: Session = Depends(get_session)
) -> dict[str, str]:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Message text is required")
    reply = process_text(session, _default_provider(), text, DEMO_WA_ID)
    return {"reply": reply, "from": DEMO_WA_ID}
