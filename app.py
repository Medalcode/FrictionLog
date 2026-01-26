from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import Optional
import os
import requests

app = FastAPI(title="FrictionLog")
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


@app.on_event("startup")
def startup():
    ensure_tables()


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
    cur.execute("SELECT id, user_id, description, severity, created_at FROM fricciones ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "user_id": r[1], "description": r[2], "severity": r[3], "created_at": r[4]} for r in rows]


@app.post("/analizar-con-ia")
def analizar_con_ia(payload: AnalyzeInput):
    """Analiza una fricción usando una API de LLM si está disponible (LLM_API_URL en env).
    Si no hay LLM configurado, devuelve un análisis heurístico simple."""
    text = payload.description.strip()
    if not text:
        raise HTTPException(status_code=400, detail="description required")

    system_prompt = f"""Actúa como un Experto en Product Discovery y Arquitecto de Software. Transforma la siguiente queja en un objeto JSON con: nombre_comercial, categoria, analisis_dolor, arquitectura_sugerida, funcionalidad_clave_mvp. Sé conciso.

Problema: "{text}"
"""

    llm_url = os.environ.get("LLM_API_URL")
    def call_llm(prompt: str):
        llm_url = os.environ.get("LLM_API_URL")
        model = os.environ.get("LLM_MODEL", "llama3")
        if not llm_url:
            return {"ok": False, "error": "LLM_API_URL not set"}
        try:
            # Ollama local default: http://localhost:11434
            if "11434" in llm_url or "ollama" in llm_url:
                url = llm_url.rstrip("/") + "/api/generate"
                payload = {"model": model, "prompt": prompt, "stream": False}
                resp = requests.post(url, json=payload, timeout=30)
                text = resp.text
            else:
                # Generic LLM endpoint expecting {prompt: ...}
                resp = requests.post(llm_url, json={"prompt": prompt}, timeout=30)
                text = resp.text

            # Try to parse JSON from response
            try:
                return {"ok": True, "json": resp.json()}
            except Exception:
                return {"ok": True, "text": text}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # Call the LLM (if configured) and try to return structured output
    llm_result = call_llm(system_prompt)
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

