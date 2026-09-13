from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import get_session
from app.domain.whatsapp_memory import _default_provider, process_text
from app.models import InventoryLot

router = APIRouter(prefix="/demo/whatsapp", tags=["demo"])

DEMO_WA_ID = "demo-user"

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WhatsApp Demo — Household Agent</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: "Segoe UI", system-ui, sans-serif; background: #111b21; color: #e9edef; margin: 0; }
  .app { display: flex; height: 100vh; max-width: 1400px; margin: 0 auto; }
  .phone { flex: 1; display: flex; flex-direction: column; min-width: 0; border-right: 1px solid #222d34; }
  header { background: #1f2c34; padding: 0.6rem 1rem; display: flex; align-items: center; gap: 0.8rem; }
  .avatar { width: 2.5rem; height: 2.5rem; border-radius: 50%; background: #00a884; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem; color: #06281f; flex-shrink: 0; }
  header .who b { display: block; font-size: 1rem; } header .who small { color: #8696a0; font-size: 0.8rem; }
  .banner { background: #453a12; color: #ffe082; font-size: 0.78rem; padding: 0.35rem 1rem; }
  #chat { flex: 1; overflow-y: auto; padding: 1rem 3rem; display: flex; flex-direction: column; gap: 0.4rem;
    background-color: #0b141a;
    background-image: radial-gradient(#ffffff08 1px, transparent 1px);
    background-size: 22px 22px; }
  .datechip { align-self: center; background: #1f2c34; color: #ffd279; font-size: 0.72rem; padding: 0.25rem 0.8rem; border-radius: 0.5rem; margin-bottom: 0.5rem; }
  .row { display: flex; } .row.me { justify-content: flex-end; } .row.bot { justify-content: flex-start; }
  .bubble { max-width: 65%; padding: 0.45rem 0.6rem 0.3rem; font-size: 0.95rem; line-height: 1.4; position: relative; box-shadow: 0 1px 1px #00000055; }
  .me .bubble { background: #005c4b; border-radius: 0.6rem 0 0.6rem 0.6rem; }
  .bot .bubble { background: #1f2c34; border-radius: 0 0.6rem 0.6rem 0.6rem; }
  .meta { display: block; text-align: right; font-size: 0.68rem; color: #ffffff99; margin-top: 0.15rem; }
  .ticks { color: #53bdeb; }
  .typing { font-style: italic; color: #8696a0; }
  form { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: #1f2c34; }
  .pill { flex: 1; display: flex; align-items: center; gap: 0.6rem; background: #2a3942; border-radius: 1.4rem; padding: 0.55rem 1rem; }
  .pill span { color: #8696a0; } input { flex: 1; background: none; border: none; outline: none; color: #e9edef; font-size: 1rem; }
  .send { border-radius: 50%; border: none; background: #00a884; color: white; width: 2.8rem; height: 2.8rem; font-size: 1.3rem; cursor: pointer; flex-shrink: 0; }
  aside { width: 320px; background: #111b21; padding: 1rem; overflow-y: auto; flex-shrink: 0; }
  aside h2 { font-size: 1rem; margin: 0 0 0.2rem; } aside p { font-size: 0.8rem; color: #8696a0; margin: 0 0 0.8rem; }
  aside a { color: #53bdeb; font-size: 0.85rem; }
  .lot { background: #1f2c34; border-radius: 0.5rem; padding: 0.5rem 0.7rem; margin-bottom: 0.5rem; font-size: 0.9rem; transition: background 1s; }
  .lot small { color: #8696a0; } .lot .bump { color: #00e676; font-weight: bold; }
  .lot.flash { background: #0a3d2e; }
  @media (max-width: 800px) { aside { display: none; } #chat { padding: 1rem; } }
</style>
</head>
<body>
<div class="app">
  <div class="phone">
    <header><div class="avatar">H</div><div class="who"><b>Household Agent</b><small>online &bull; WhatsApp Demo</small></div></header>
    <div class="banner">DEMO — simulated chat running the real agent pipeline. No Meta involved.</div>
    <div id="chat"><div class="datechip">TODAY</div></div>
    <form id="f">
      <div class="pill"><span>&#9786;</span><input id="t" autocomplete="off" placeholder="Type a message"><span>&#128206;</span></div>
      <button class="send" aria-label="Send">&#10148;</button>
    </form>
  </div>
  <aside>
    <h2>&#127968; Household inventory — live</h2>
    <p>Refreshes after every message. New/increased rows flash green.</p>
    <div id="inventory-live"></div>
    <a href="http://localhost:5173" target="_blank">Open dashboard &rarr;</a>
  </aside>
</div>
<script>
const chat = document.getElementById('chat');
const invBox = document.getElementById('inventory-live');
let prev = {};
const now = () => new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
function bubble(cls, text, ticks) {
  chat.insertAdjacentHTML('beforeend',
    `<div class="row ${cls}"><div class="bubble">${text.replace(/</g, '&lt;')}<span class="meta">${now()}${ticks ? ' <span class="ticks">&#10003;&#10003;</span>' : ''}</span></div></div>`);
  chat.scrollTop = chat.scrollHeight;
}
async function loadInventory(flash) {
  const r = await fetch('/demo/whatsapp/inventory');
  const data = await r.json();
  const cur = {};
  invBox.innerHTML = '';
  for (const it of data.inventory) {
    const key = it.ingredient.toLowerCase();
    cur[key] = it.quantity;
    const grew = flash && (cur[key] > (prev[key] || 0));
    const badge = it.confirmed ? '' : ' <small>(unconfirmed)</small>';
    invBox.insertAdjacentHTML('beforeend',
      `<div class="lot${grew ? ' flash' : ''}"><b>${it.ingredient}</b> — ${it.quantity} ${it.unit}${badge}${grew ? ' <span class="bump">▲ up from ' + (prev[key] || 0) + '</span>' : ''}</div>`);
  }
  if (!data.inventory.length) invBox.innerHTML = '<div class="lot"><small>Empty — try “bought 2 L milk”.</small></div>';
  prev = cur;
}
document.getElementById('f').onsubmit = async (e) => {
  e.preventDefault();
  const t = document.getElementById('t');
  const text = t.value.trim();
  if (!text) return;
  t.value = '';
  bubble('me', text, true);
  const typing = document.createElement('div');
  typing.className = 'row bot';
  typing.innerHTML = '<div class="bubble typing">typing...</div>';
  chat.appendChild(typing); chat.scrollTop = chat.scrollHeight;
  const r = await fetch('/demo/whatsapp/send', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text}),
  });
  typing.remove();
  const data = await r.json();
  bubble('bot', data.reply || '...', false);
  await loadInventory(true);
};
loadInventory(false);
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


@router.get("/inventory")
def demo_inventory(session: Session = Depends(get_session)) -> dict[str, list[dict]]:
    lots = session.exec(
        select(InventoryLot).where(InventoryLot.household_id == 1)
    ).all()
    return {
        "inventory": [
            {
                "ingredient": lot.ingredient,
                "quantity": lot.quantity,
                "unit": lot.unit,
                "confirmed": lot.confirmed,
            }
            for lot in lots
        ]
    }
