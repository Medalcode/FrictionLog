from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import Optional
import os
from contextlib import asynccontextmanager
import httpx

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_tables()
    migrate_tables()
    yield

app = FastAPI(title="FrictionLog", lifespan=lifespan)
DB_PATH = "frictionlog.db"


class FrictionInput(BaseModel):
    user_id: Optional[str] = "anonymous"
    description: str
    severity: int = 1


class AnalyzeInput(BaseModel):
    description: str


def get_db_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


def ensure_tables():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS fricciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        description TEXT,
        severity INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def migrate_tables():
    """Simple migration to add new columns if they don't exist."""
    conn = get_db_conn()
    cur = conn.cursor()
    columns = [
        ("nombre_comercial", "TEXT"),
        ("categoria", "TEXT"),
        ("arquitectura", "TEXT"),
        ("mvp_features", "TEXT")
    ]
    for col_name, col_type in columns:
        try:
            cur.execute(f"ALTER TABLE fricciones ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            # Column likely exists
            pass
    conn.commit()
    conn.close()





@app.post("/registrar-friccion")
def registrar_friccion(f: FrictionInput):
    if not f.description:
        raise HTTPException(status_code=400, detail="description required")
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO fricciones (user_id, description, severity) VALUES (?,?,?)",
                (f.user_id, f.description, f.severity))
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return {"status": "ok", "id": last_id}


@app.get("/fricciones")
def list_fricciones(limit: int = 50):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, description, severity, created_at, nombre_comercial, categoria, arquitectura, mvp_features FROM fricciones ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [{
        "id": r[0], 
        "user_id": r[1], 
        "description": r[2], 
        "severity": r[3], 
        "created_at": r[4],
        "nombre_comercial": r[5],
        "categoria": r[6],
        "arquitectura": r[7],
        "mvp_features": r[8]
    } for r in rows]


@app.post("/analizar-con-ia")
async def analizar_con_ia(payload: AnalyzeInput):
    """Analiza una fricción usando una API de LLM si está disponible (LLM_API_URL en env).
    Si no hay LLM configurado, devuelve un análisis heurístico simple."""
    text = payload.description.strip()
    if not text:
        raise HTTPException(status_code=400, detail="description required")

    system_prompt = f"""Actúa como un Experto en Product Discovery y Arquitecto de Software. Transforma la siguiente queja en un objeto JSON con: nombre_comercial, categoria, analisis_dolor, arquitectura_sugerida, funcionalidad_clave_mvp. Sé conciso.

Problema: "{text}"
"""

    llm_url = os.environ.get("LLM_API_URL")
    model = os.environ.get("LLM_MODEL", "llama3")

    async def call_llm(prompt: str):
        if not llm_url:
            return {"ok": False, "error": "LLM_API_URL not set"}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Ollama local default: http://localhost:11434
                if "11434" in llm_url or "ollama" in llm_url:
                    url = llm_url.rstrip("/") + "/api/generate"
                    payload = {"model": model, "prompt": prompt, "stream": False}
                    resp = await client.post(url, json=payload)
                    text = resp.text
                else:
                    # Generic LLM endpoint expecting {prompt: ...}
                    resp = await client.post(llm_url, json={"prompt": prompt})
                    text = resp.text

                # Try to parse JSON from response
                try:
                    return {"ok": True, "json": resp.json()}
                except Exception:
                    return {"ok": True, "text": text}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # Call the LLM (if configured) and try to return structured output
    llm_result = await call_llm(system_prompt)
    if llm_result.get("ok"):
        if "json" in llm_result:
            return {"from": "llm", "response": llm_result["json"]}
        else:
            text = llm_result.get("text")
            # Try to extract JSON object from text
            try:
                import json, re

                # find first '{' ... '}' block
                m = re.search(r"\{.*\}", text, re.DOTALL)
                if m:
                    parsed = json.loads(m.group(0))
                    return {"from": "llm", "response": parsed}
            except Exception:
                pass
            return {"from": "llm", "raw": text}
    # else fall through to heuristic

    # Heurística simple si no hay LLM
    desc_lower = text.lower()
    if "debian" in desc_lower or "apt" in desc_lower or "docker" in desc_lower:
        categoria = "DevOps"
        arquitectura = "CLI + microservice con contenedores ligeros (Docker) y FastAPI para orchestration"
        mvp = "Comando único que detecte versión y levante un entorno aislado para ejecutar el script"
        nombre = "PyDeb-Shield"
    elif "excel" in desc_lower or "xls" in desc_lower or "hoja" in desc_lower:
        categoria = "Small Business / Automation"
        arquitectura = "API que convierte plantillas de Excel a endpoints y automatiza importaciones"
        mvp = "Uploader que mapea columnas y exporta CSV/JSON automatizado"
        nombre = "SheetBridge"
    else:
        categoria = "General"
        arquitectura = "Microservicio REST (FastAPI) + worker para tasks pesados"
        mvp = "Endpoint que recibe el problema y devuelve un plan técnico breve"
        nombre = "IdeaLab-Core"

    return {
        "from": "heuristic",
        "nombre_comercial": nombre,
        "categoria": categoria,
        "analisis_dolor": text,
        "arquitectura_sugerida": arquitectura,
        "funcionalidad_clave_mvp": mvp,
    }


@app.post("/fricciones/{friction_id}/analizar")
async def analyze_friction(friction_id: int):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT description FROM fricciones WHERE id = ?", (friction_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Friction not found")
        
    description = row[0]
    
    # Reuse existing analyze logic
    payload = AnalyzeInput(description=description)
    # We call the function directly. Since it is async now, we await it.
    analysis = await analizar_con_ia(payload)
    
    nombre = "N/A"
    categoria = "Unknown"
    arquitectura = ""
    mvp = ""

    if "response" in analysis:
        resp = analysis["response"]
        nombre = resp.get("nombre_comercial", "N/A")
        categoria = resp.get("categoria", "Unknown")
        arquitectura = resp.get("arquitectura_sugerida", "")
        mvp = resp.get("funcionalidad_clave_mvp", "")
    elif analysis.get("from") == "heuristic":
        nombre = analysis.get("nombre_comercial", "N/A")
        categoria = analysis.get("categoria", "Unknown")
        arquitectura = analysis.get("arquitectura_sugerida", "")
        mvp = analysis.get("funcionalidad_clave_mvp", "")

    conn = get_db_conn()
    cur = conn.cursor()
    # Ensure columns exist (migrated)
    try:
        cur.execute("""
            UPDATE fricciones 
            SET nombre_comercial = ?, categoria = ?, arquitectura = ?, mvp_features = ?
            WHERE id = ?
        """, (nombre, categoria, arquitectura, mvp, friction_id))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    conn.close()
    
    return {"status": "ok", "id": friction_id, "analysis": analysis}

