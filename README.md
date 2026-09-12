# Household Agent

Household Agent is a local-first household-orchestration prototype. It keeps
durable household memory in SQLite, produces deterministic and explainable meal
plans, routes consequential actions through a visible approval workflow, records
cook outcomes and feedback, and makes later recommendations from that memory.
It also supports review-first local inventory capture from typed entries, voice
notes, and fridge photos. No real ordering, payments, external messaging, or
cloud service is part of the product.

## Prerequisites

- Python 3.12+
- Node.js 18+
- [Ollama](https://ollama.com) for local language and optional vision models
- NVIDIA GPU is recommended, not required — the CPU fallback is verified working.
- `faster-whisper` is optional and is installed via `pip install -e '.[voice]'`.
  It is needed only for real voice transcription; typed and photo capture work
  without it.
- Qwen2.5-VL is pulled via Ollama, not pip — no extra Python dependency.
- Qwen3:4b is also pulled via ollama. not pip. 

qwen3:4b is required via Ollama for local language tasks, cook briefs, feedback parsing, and healthy-model checks.
qwen2.5vl:3b is optional via Ollama for photo capture.
faster-whisper is optional for voice transcription; it is a speech-recognition model, not an LLM.

Install the application and its frontend dependencies once:

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
# Optional: enables real local voice transcription.
.venv/bin/pip install -e '.[voice]'
cd frontend
npm install
cd ..
```

The SQLite database is local at `data/household.db`. It is intentionally
gitignored (`data/*.db`), so a judge should obtain deterministic seed data by
using `POST /api/demo/reset` (or the dashboard's **Reset selected demo** button),
not by looking for a committed database file.

## Run locally

Start the backend in one terminal:

```bash
.venv/bin/uvicorn app.main:app --app-dir backend --reload
```

Start the frontend in another terminal:

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`. The dashboard health card shows the
frontend-to-backend connection. Select a demo scenario and choose **Reset selected
demo** to replace local data with its deterministic fixture; see
[docs/demo-scenarios.md](docs/demo-scenarios.md) for what each one demonstrates.

## Verify your setup

Run these checks in the listed order. Commands that start a server remain running;
use the stated additional terminal for the next group.

```bash
# 1. Toolchain + installed frontend/backend dependencies

python3 --version
node --version
.venv/bin/python --version
.venv/bin/pytest
cd frontend && npm run build && npm test
```

Expected: version commands print their installed versions; pytest discovers and
runs the backend suite; the frontend build and test commands exit successfully.

```bash
# 2. Start backend (terminal 1)

.venv/bin/uvicorn app.main:app --app-dir backend --reload
```

Expected: Uvicorn reports that it is running on `http://127.0.0.1:8000` (or its
configured local bind address).

```bash
# 3. Confirm backend and database are reachable (terminal 2)

curl -s http://127.0.0.1:8000/api/health | python3 -m json.tool
```

Expected: top-level `"status": "ok"` and `"database": {"status": "available"}`.

```bash
# 4. Start frontend (another terminal)

cd frontend
npm run dev
```

Then open `http://localhost:5173`. The dashboard's health card confirms the
frontend-to-backend connection.

```bash
# 5. Confirm Ollama service and required chat model

ollama --version
curl -s http://127.0.0.1:11434/api/tags | python3 -m json.tool
ollama list
ollama pull qwen3:4b        # only if it is absent
ollama run qwen3:4b 'Reply with exactly: ready'
```

Re-run the backend health command afterward. Ollama is ready for this app when it
reports:

```json
"ollama": {
  "status": "available",
  "model": "qwen3:4b"
}
```

```bash
# 6. Confirm NVIDIA GPU is visible and Ollama is actually using it

nvidia-smi
ollama ps
```

While `ollama run qwen3:4b ...` is running, `ollama ps` should show the model
with a GPU processor (rather than 100% CPU). You can also watch utilization live:

```bash
watch -n 1 nvidia-smi
```

Optional, if you intend to use image capture too:

```bash
ollama pull qwen2.5vl:3b
ollama run qwen2.5vl:3b 'Reply with exactly: vision-ready'
```

The app defaults are `qwen3:4b` for language tasks and `qwen2.5vl:3b` for vision.

## Local-only operation and fallbacks

The app calls Ollama only on the local machine (`127.0.0.1`). The
`.env.example` includes `HF_HUB_OFFLINE=1`; startup also applies that setting by
default before the optional faster-whisper dependency can load. No manual flag is
needed for local-only operation. A missing cached Whisper model therefore produces
a typed-entry fallback rather than a Hugging Face network request.

Voice, vision, Ollama, and scheduler failures are explicit in the dashboard.
Typed inventory entry remains available when optional voice or vision providers are
unavailable, and every proposed voice/photo field requires explicit confirmation
before it changes inventory.

## Tests

```bash
.venv/bin/pytest
cd frontend && npm test
npm run test:e2e
```

The Playwright suite uses its own temporary SQLite database and test-only backend
and frontend ports; it does not alter `data/household.db`.
