from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import asyncio
import core
from llm_client import analizar_friccion, API_KEY
@asynccontextmanager
async def lifespan(app: FastAPI):
    core.init_db()
    yield

app = FastAPI(title="FrictionLog API", lifespan=lifespan)

class FrictionInput(BaseModel):
    user_id: str = "anonymous"
    description: str = Field(..., min_length=10, description="Descripción del problema, obligatoria y al menos de 10 caracteres")
    severity: int = Field(1, ge=1, le=5)

class AnalyzeInput(BaseModel):
    description: str = Field(..., min_length=5, description="El problema o fricción a analizar")

# Pydantic Models para la validación de la salida (Response Data)
class IAAnalysisData(BaseModel):
    categoria: str
    tipo_problema: str
    impacto: str
    idea_solucion: str

class IAResponseWrapper(BaseModel):
    analisis: IAAnalysisData

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
    res = analysis.get("response", {})
    
    cat = res.get("categoria", "Unknown")
    tipo = res.get("tipo_problema", "Desconocido")
    imp = res.get("impacto", "Desconocido")
    idea = res.get("idea_solucion", "Sin idea general")

    try:
        cur.execute("""
            UPDATE fricciones 
            SET categoria = ?, tipo_problema = ?, impacto = ?, idea_solucion = ?
            WHERE id = ?
        """, (cat, tipo, imp, idea, friction_id))
        conn.commit()
        return {"status": "ok", "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.post("/analizar-con-ia", response_model=IAResponseWrapper)
async def api_analize_friction_endpoint(input_data: AnalyzeInput):
    """
    Endpoint directo y agnóstico a la DB para analizar texto libre usando IA Gen.
    """
    # Manejo de error si no hay API KEY
    if not API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="La configuración de GOOGLE_API_KEY no existe en el entorno del servidor."
        )
        
    try:
        # Se ejecuta en un thread para evitar bloquear el Event Loop de tu app asíncrona (FastAPI)
        resultado_ia = await asyncio.to_thread(analizar_friccion, input_data.description)
        
        # Como llm_client devuelve un dict con valores defaults de error, verificamos si falló la IA
        if "Error" in resultado_ia.get("tipo_problema", ""):
            raise HTTPException(
                status_code=502, 
                detail=f"Fallo en la inferencia del modelo Gemini: {resultado_ia.get('tipo_problema')}"
            )
            
        # Pydantic (IAResponseWrapper) validará automáticamente que el dict encaje en la salida
        return {"analisis": resultado_ia}
        
    except HTTPException:
        # Relanzamos si es nuestro propio error controlado
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado en el servidor: {str(e)}")
