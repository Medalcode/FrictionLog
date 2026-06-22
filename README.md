# FrictionLog

**Convierte la frustración en tu próximo proyecto.**
FrictionLog es una API ligera que captura "puntos de dolor" (fricciones) diarios, los analiza con IA y los prioriza para que construyas soluciones que la gente realmente necesita.

### "Odio hacer esto manualmente..."

¿Cuántas veces has pensado eso y luego lo has olvidado?
Como desarrolladores o Indie Hackers, a menudo buscamos ideas "revolucionarias" mientras ignoramos los problemas reales que tenemos delante. **FrictionLog** actúa como un buzón de quejas inteligente:

1. **Captura** la molestia en el momento (vía CLI o API).
2. **Centraliza** tus frustraciones.
3. **Genera** especificaciones técnicas automáticas (MVP) usando LLMs.

---

### Proveedores de IA

| Proveedor | Variable | Modelo |
|-----------|----------|--------|
| Google Gemini (default) | `GOOGLE_API_KEY` | `gemini-1.5-flash` |
| xAI Grok | `XAI_API_KEY` | `grok-4.20` |

Selecciona el proveedor con `LLM_PROVIDER=gemini` o `LLM_PROVIDER=grok`.

### Quickstart

#### Docker + PocketBase (Recomendado)

1. Descarga y ejecuta [PocketBase](https://pocketbase.io/). Importa `pocketbase_schema.json` desde `http://127.0.0.1:8090/_/`.

2. Clona y levanta:

   ```bash
   git clone https://github.com/Medalcode/FrictionLog.git && cd FrictionLog
   export LLM_PROVIDER=grok
   export XAI_API_KEY="tu-api-key"
   docker-compose up --build -d
   ```

3. Servicios:
   - **Dashboard:** http://localhost:8501
   - **API:** http://localhost:8000/docs

#### Local (Python)

```bash
git clone https://github.com/Medalcode/FrictionLog.git && cd FrictionLog
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

export LLM_PROVIDER=grok
export XAI_API_KEY="tu-api-key"
export POCKETBASE_URL="http://127.0.0.1:8090"

uvicorn api:app --reload        # terminal 1
streamlit run ui.py             # terminal 2
```

#### Registrar una fricción

```bash
curl -X POST http://127.0.0.1:8000/registrar-friccion \
     -H "Content-Type: application/json" \
     -d '{"description": "Odio copiar datos de facturas PDF a Excel manualmente", "severity": 4}'

python cli.py log "Odio copiar datos de facturas PDF a Excel manualmente"
```

### Auth (opcional)

Si seteas `FRICTIONLOG_API_KEY`, todos los endpoints requieren:

```
Authorization: Bearer <tu-api-key>
```

### Despliegue en Vercel

1. Sube el código a GitHub.
2. Crea un proyecto en Vercel e importa el repositorio.
3. Añade las Environment Variables necesarias (`GOOGLE_API_KEY` o `XAI_API_KEY`, `POCKETBASE_URL`, etc.).

### Stack

- **`api.py`**: FastAPI async con `httpx.AsyncClient` reutilizable (lifespan).
- **`llm_client.py`**: Abstracción de proveedor LLM (Gemini + Grok).
- **`core.py`**: Orquestador del análisis IA.
- **`ui.py`**: Dashboard Streamlit.
- **`cli.py`**: CLI con `httpx`.
- **`main.py`**: Entrypoint Vercel (re-exporta `api.app`).
- **DB:** PocketBase.
- **IA:** Gemini 1.5 Flash o Grok 4.20+.

### Desarrollo

```bash
pip install -r requirements.txt
ruff check . && ruff format --check .
pytest tests/ -v
```

### Roadmap

- [x] Persistencia IA en base de datos
- [x] CRUD completo + UI
- [x] CLI wrapper
- [x] CI/CD (lint + test matrix)
- [x] Abstracción de proveedor LLM (Gemini + Grok)
- [x] Auth opcional via API Key
- [ ] Smart Grouping: detectar fricciones duplicadas semánticamente
