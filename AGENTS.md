# FrictionLog — Agent Guide

## Commands
```bash
# Local dev (no Docker):
pip install -r requirements.txt
export GOOGLE_API_KEY="..." && export POCKETBASE_URL="http://127.0.0.1:8090"
uvicorn api:app --reload                    # API (terminal 1)
streamlit run ui.py                         # Dashboard (terminal 2)

# Docker (recommended):
docker-compose up --build -d                # starts api + dashboard
docker-compose run --rm test                # run tests in container

# Tests:
pytest tests/ -v                            # 5 API tests (mocked PocketBase)
```

## Critical Quirks

- **5 entry points**, not one: `api.py` (FastAPI), `ui.py` (Streamlit), `core.py` (orchestrator), `llm_client.py` (Gemini), `main.py` (Vercel serverless entry — empty file!). The active entry points are `api.py` and `ui.py`. **Do NOT use `main.py` for local dev.**
- **PocketBase is a hard dependency** — the API communicates with it via `httpx`. Without PocketBase running at `POCKETBASE_URL`, all endpoints return errors. Tests mock it via `monkeypatch` on `httpx.AsyncClient`.
- **Schema must be pre-loaded**: import `pocketbase_schema.json` in PocketBase admin panel (`http://127.0.0.1:8090/_/`), or run `python pb_setup.py` to create it programmatically.
- **Google Gemini** (`gemini-1.5-flash`) requires `GOOGLE_API_KEY` env var. Without it, AI analysis endpoints (`/fricciones/{id}/analizar`, `/analizar-con-ia`) return error responses.
- **`app.py` is empty** (0 lines) — legacy placeholder, not used for anything. Ignore it.
- **`CHANGELOG.md` is PocketBase's changelog** (945 lines), not FrictionLog's. See `docs/BITACORA.md` for real project history.
- **Tests mock both PocketBase AND Gemini** — `test_analizar_con_ia` and `test_analyze_friction_persistence` monkeypatch `api_module.core.analizar_friccion` to avoid real LLM calls.
- **`descripcion` field minimum length**: 10 characters (enforced by Pydantic in `api.py`). POST with shorter text returns 422.
