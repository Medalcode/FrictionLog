from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from contextlib import asynccontextmanager
import core

@asynccontextmanager
async def lifespan(app: FastAPI):
    core.init_db()
    yield

app = FastAPI(title="FrictionLog API", lifespan=lifespan)

class FrictionInput(BaseModel):
    user_id: str = "anonymous"
    description: str = Field(..., min_length=10)
    severity: int = Field(1, ge=1, le=5)

class AnalyzeInput(BaseModel):
    description: str

@app.post("/registrar-friccion")
def registrar_friccion(f: FrictionInput):
    conn = core.get_db_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO fricciones (user_id, description, severity) VALUES (?,?,?)",
            (f.user_id, f.description, f.severity)
        )
        conn.commit()
        last_id = cur.lastrowid
        return {"status": "ok", "id": last_id}
    finally:
        conn.close()

@app.get("/fricciones")
def list_fricciones(limit: int = 50):
    conn = core.get_db_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, user_id, description, severity, created_at, 
                   nombre_comercial, categoria, arquitectura, mvp_features 
            FROM fricciones ORDER BY created_at DESC LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
        return [{
            "id": r[0], "user_id": r[1], "description": r[2], "severity": r[3],
            "created_at": r[4], "nombre_comercial": r[5], "categoria": r[6],
            "arquitectura": r[7], "mvp_features": r[8]
        } for r in rows]
    finally:
        conn.close()

@app.post("/fricciones/{friction_id}/analizar")
async def analyze_friction(friction_id: int):
    conn = core.get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT description FROM fricciones WHERE id = ?", (friction_id,))
    row = cur.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Friction not found")
        
    analysis = await core.analyze_with_ai(row[0])
    
    # Extract data from analysis result
    res = analysis.get("response", {}) if "response" in analysis else analysis
    nombre = res.get("nombre_comercial", "N/A")
    cat = res.get("categoria", "Unknown")
    arch = res.get("arquitectura_sugerida", "")
    mvp = res.get("funcionalidad_clave_mvp", "")

    try:
        cur.execute("""
            UPDATE fricciones 
            SET nombre_comercial = ?, categoria = ?, arquitectura = ?, mvp_features = ?
            WHERE id = ?
        """, (nombre, cat, arch, mvp, friction_id))
        conn.commit()
        return {"status": "ok", "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
