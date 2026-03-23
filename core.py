import sqlite3
import os
import asyncio
from typing import Optional, List, Dict, Any

from llm_client import analizar_friccion

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

async def analyze_with_ai(description: str) -> Dict[str, Any]:
    """
    Delega de forma asíncrona la ejecución de la llamada a la API de Gemini
    mediante asyncio.to_thread para no bloquear el worker de FastAPI.
    """
    try:
        resultado = await asyncio.to_thread(analizar_friccion, description)
        
        # Mapeamos la salida de Gemini al formato esperado por la tabla y la UI
        # para no tener que regenerar toda la db / UI
        return {
            "from": "gemini",
            "response": {
                "nombre_comercial": resultado.get("tipo_problema", "Desconocido"),
                "categoria": resultado.get("categoria", "General"),
                "arquitectura_sugerida": f"Impacto: {resultado.get('impacto', 'Bajo')}",
                "funcionalidad_clave_mvp": resultado.get("idea_solucion", "Sin funcionalidad clara")
            }
        }
    except Exception as e:
        return {"from": "error", "error": str(e)}
