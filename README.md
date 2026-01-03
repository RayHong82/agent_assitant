# Property Agent Assistant — Minimal Prototype

Run locally (recommended):

1. Create and activate a virtualenv (macOS):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start the app:

```bash
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

3. Open on your machine or phone (same LAN):

http://<your-machine-ip>:8000

Notes:
- The app includes a simple KB, streaming simulation, and a static frontend.
- To enable real LLM calls, set `OPENAI_API_KEY` in the environment and extend `llm_client.py`.
# Project

This is a project for a property agent assistant app.