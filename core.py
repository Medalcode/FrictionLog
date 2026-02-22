import sqlite3
import os
import httpx
import json
import re
from typing import Optional, List, Dict, Any

DB_PATH = "frictionlog.db"

def get_db_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS fricciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        description TEXT,
        severity INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        nombre_comercial TEXT,
        categoria TEXT,
        arquitectura TEXT,
        mvp_features TEXT
    )
    """)
    conn.commit()
    conn.close()

async def call_llm(prompt: str) -> Dict[str, Any]:
    llm_url = os.environ.get("LLM_API_URL")
    model = os.environ.get("LLM_MODEL", "llama3")
    
    if not llm_url:
        return {"ok": False, "error": "LLM_API_URL not set"}
        
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if "11434" in llm_url or "ollama" in llm_url:
                url = llm_url.rstrip("/") + "/api/generate"
                payload = {"model": model, "prompt": prompt, "stream": False}
                resp = await client.post(url, json=payload)
                data = resp.json()
                return {"ok": True, "text": data.get("response", "")}
            else:
                resp = await client.post(llm_url, json={"prompt": prompt})
                return {"ok": True, "text": resp.text}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def analyze_with_ai(description: str) -> Dict[str, Any]:
    text = description.strip()
    system_prompt = f"""Actúa como un Experto en Product Discovery y Arquitecto de Software. Transforma la siguiente queja en un objeto JSON con: nombre_comercial, categoria, analisis_dolor, arquitectura_sugerida, funcionalidad_clave_mvp. Sé conciso.

Problema: "{text}"
"""
    
    result = await call_llm(system_prompt)
    
    if result.get("ok"):
        raw_text = result.get("text", "")
        try:
            m = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if m:
                parsed = json.loads(m.group(0))
                return {"from": "llm", "response": parsed}
        except Exception:
            pass
        return {"from": "llm", "raw": raw_text}

    # Heuristic Fallback
    desc_lower = text.lower()
    if any(k in desc_lower for k in ["debian", "apt", "docker"]):
        return {
            "from": "heuristic",
            "nombre_comercial": "PyDeb-Shield",
            "categoria": "DevOps",
            "arquitectura_sugerida": "CLI + microservice con contenedores ligeros (Docker) y FastAPI",
            "funcionalidad_clave_mvp": "Comando único que detecte versión y levante un entorno aislado"
        }
    elif any(k in desc_lower for k in ["excel", "xls", "hoja"]):
        return {
            "from": "heuristic",
            "nombre_comercial": "SheetBridge",
            "categoria": "Small Business / Automation",
            "arquitectura_sugerida": "API de conversión de plantillas a endpoints",
            "funcionalidad_clave_mvp": "Uploader que mapea columnas y exporta CSV/JSON"
        }
    
    return {
        "from": "heuristic",
        "nombre_comercial": "IdeaLab-Core",
        "categoria": "General",
        "arquitectura_sugerida": "Microservicio REST (FastAPI) + worker",
        "funcionalidad_clave_mvp": "Endpoint que recibe problema y devuelve plan técnico"
    }
