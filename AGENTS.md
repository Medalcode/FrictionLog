# FrictionLog — Agent Guide

## Commands
```bash
pip install -r requirements.txt

# Google Gemini (default)
export LLM_PROVIDER=gemini
export GOOGLE_API_KEY="..."

# xAI Grok (alternative)
export LLM_PROVIDER=grok
export XAI_API_KEY="..."

# Common
export POCKETBASE_URL="http://127.0.0.1:8090"
export FRICTIONLOG_API_KEY="..."       # optional auth

uvicorn api:app --reload               # API (terminal 1)
streamlit run ui.py                    # Dashboard (terminal 2)

# Docker (recommended):
docker-compose up --build -d
docker-compose run --rm test           # tests

# Lint & tests:
ruff check . && ruff format --check .
pytest tests/ -v
```

## Key Architecture

- **`api.py`**: FastAPI async. Single `httpx.AsyncClient` via FastAPI lifespan.
- **`llm_client.py`**: Provider abstraction (`LLMProvider` ABC). Supports Gemini and Grok. Selected via `LLM_PROVIDER` env var.
- **`core.py`**: Thin orchestrator. Calls `llm_client.analizar_friccion` via `asyncio.to_thread`.
- **`ui.py`**: Streamlit dashboard. Calls API endpoints.
- **`cli.py`**: CLI tool using `httpx` (sync).
- **`main.py`**: Vercel entrypoint — re-exports `api.app`.

## LLM Providers

| Provider | Env var | Model | Library |
|----------|---------|-------|---------|
| Gemini (default) | `GOOGLE_API_KEY` | `gemini-1.5-flash` | `google-generativeai` |
| Grok | `XAI_API_KEY` | `grok-4.20` (configurable via `XAI_MODEL`) | `httpx` direct |

## Auth

If `FRICTIONLOG_API_KEY` is set, all endpoints require `Authorization: Bearer <key>`.

## Key Fields (canonical format)

All components use the same keys: `categoria`, `tipo_problema`, `impacto`, `idea_solucion`.

## Tests

- 10 tests, mock PocketBase (`httpx.AsyncClient`) + LLM responses
- Run: `pytest tests/ -v`
- CI runs lint (ruff) + test matrix (3.10, 3.11, 3.12)
