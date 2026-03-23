from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import httpx
import asyncio
import core
from llm_client import analizar_friccion, API_KEY

# Ya no usamos asynccontextmanager ni init_db local, PocketBase persiste
app = FastAPI(title="FrictionLog API")

class FrictionInput(BaseModel):
    user_id: str = "anonymous"
    description: str = Field(..., min_length=10, description="Descripción del problema")
    severity: int = Field(1, ge=1, le=5)

class AnalyzeInput(BaseModel):
    description: str = Field(..., min_length=5)

class IAAnalysisData(BaseModel):
    categoria: str
    tipo_problema: str
    impacto: str
    idea_solucion: str

class IAResponseWrapper(BaseModel):
    analisis: IAAnalysisData

@app.post("/registrar-friccion")
async def registrar_friccion(f: FrictionInput):
    """Guarda directamente en PocketBase usando su API REST"""
    async with httpx.AsyncClient() as client:
        payload = {
            "user_id": f.user_id,
            "description": f.description,
            "severity": f.severity
        }
        res = await client.post(f"{core.PB_URL}/api/collections/fricciones/records", json=payload)
        
        if res.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Error en PocketBase: {res.text}")
            
        return {"status": "ok", "id": res.json().get("id")}

@app.get("/fricciones")
async def list_fricciones(limit: int = 50):
    """Recupera la lista de ficciones directo de PocketBase, ordenadas por más recientes"""
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{core.PB_URL}/api/collections/fricciones/records?sort=-created&perPage={limit}")
        if res.status_code != 200:
            raise HTTPException(status_code=502, detail="Error al buscar en PocketBase")
            
        # PocketBase devuelve la lista bajo la clave "items"
        items = res.json().get("items", [])
        
        # Mapeamos para mantener compatibilidad total con ui.py (ej. "created_at", etc)
        # Nota: Pocketbase devuelve el timestamp en el campo 'created'
        return [{
            "id": item.get("id"),
            "user_id": item.get("user_id", "anonymous"),
            "description": item.get("description", ""),
            "severity": item.get("severity", 1),
            "created_at": item.get("created", ""),
            "categoria": item.get("categoria"),
            "tipo_problema": item.get("tipo_problema"),
            "impacto": item.get("impacto"),
            "idea_solucion": item.get("idea_solucion"),
            "nombre_comercial": item.get("tipo_problema"), # Compatibilidad hacia atrás
            "arquitectura": item.get("impacto"),           
            "mvp_features": item.get("idea_solucion")
        } for item in items]

@app.post("/fricciones/{friction_id}/analizar")
async def analyze_friction(friction_id: str):
    """
    Obtiene la fricción de PocketBase, la analiza con Gemini,
    y guarda el resultado (PATCH) de vuelta en PocketBase.
    Notar que PocketBase usa hashes (cadenas alfanuméricas) como friction_id, no int.
    """
    async with httpx.AsyncClient() as client:
        # 1. Traer texto
        get_res = await client.get(f"{core.PB_URL}/api/collections/fricciones/records/{friction_id}")
        if get_res.status_code != 200:
            raise HTTPException(status_code=404, detail="Fricción no encontrada en PocketBase")
            
        description = get_res.json().get("description", "")
        
        # 2. Analizar con Gemini
        analysis = await core.analyze_with_ai(description)
        res_ia = analysis.get("response", {})
        
        # 3. Guardar el resultado en la misma fila en PocketBase (UPDATE / PATCH)
        patch_payload = {
            "categoria": res_ia.get("categoria", "Desconocida"),
            "tipo_problema": res_ia.get("tipo_problema", "Desconocido"),
            "impacto": res_ia.get("impacto", "Desconocido"),
            "idea_solucion": res_ia.get("idea_solucion", "Sin sugerencia")
        }
        
        patch_res = await client.patch(f"{core.PB_URL}/api/collections/fricciones/records/{friction_id}", json=patch_payload)
        if patch_res.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Error al actualizar IA: {patch_res.text}")
            
        return {"status": "ok", "analysis": analysis}

@app.post("/analizar-con-ia", response_model=IAResponseWrapper)
async def api_analize_friction_endpoint(input_data: AnalyzeInput):
    """ Endpoint Ad-hoc/Live: Sigue funcionando igual """
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API KEY de Google no configurada.")
        
    try:
        resultado_ia = await asyncio.to_thread(analizar_friccion, input_data.description)
        if "Error" in resultado_ia.get("tipo_problema", ""):
            raise HTTPException(status_code=502, detail=f"Fallo Gemini: {resultado_ia.get('tipo_problema')}")
            
        return {"analisis": resultado_ia}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
