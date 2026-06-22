import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import core

FRICTIONLOG_API_KEY = os.getenv("FRICTIONLOG_API_KEY")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient() as client:
        app.state.http_client = client
        yield


app = FastAPI(title="FrictionLog API", lifespan=lifespan)


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


async def _check_auth(request: Request):
    if FRICTIONLOG_API_KEY:
        auth = request.headers.get("Authorization", "")
        if auth != f"Bearer {FRICTIONLOG_API_KEY}":
            raise HTTPException(status_code=401, detail="API Key inválida o ausente")


@app.post("/registrar-friccion")
async def registrar_friccion(f: FrictionInput, request: Request):
    await _check_auth(request)
    client: httpx.AsyncClient = request.app.state.http_client
    payload = {
        "user_id": f.user_id,
        "description": f.description,
        "severity": f.severity,
    }
    res = await client.post(f"{core.PB_URL}/api/collections/fricciones/records", json=payload)
    if res.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Error en PocketBase: {res.text}")
    return {"status": "ok", "id": res.json().get("id")}


@app.get("/fricciones")
async def list_fricciones(request: Request, limit: int = 50):
    await _check_auth(request)
    client: httpx.AsyncClient = request.app.state.http_client
    res = await client.get(
        f"{core.PB_URL}/api/collections/fricciones/records?sort=-created&perPage={limit}"
    )
    if res.status_code != 200:
        raise HTTPException(status_code=502, detail="Error al buscar en PocketBase")

    items = res.json().get("items", [])
    return [
        {
            "id": item.get("id"),
            "user_id": item.get("user_id", "anonymous"),
            "description": item.get("description", ""),
            "severity": item.get("severity", 1),
            "created_at": item.get("created", ""),
            "categoria": item.get("categoria"),
            "tipo_problema": item.get("tipo_problema"),
            "impacto": item.get("impacto"),
            "idea_solucion": item.get("idea_solucion"),
        }
        for item in items
    ]


@app.post("/fricciones/{friction_id}/analizar")
async def analyze_friction(friction_id: str, request: Request):
    await _check_auth(request)
    client: httpx.AsyncClient = request.app.state.http_client

    get_res = await client.get(f"{core.PB_URL}/api/collections/fricciones/records/{friction_id}")
    if get_res.status_code != 200:
        raise HTTPException(status_code=404, detail="Fricción no encontrada")

    description = get_res.json().get("description", "")
    analysis = await core.analyze_with_ai(description)
    res_ia = analysis.get("response", {})

    if "error" in res_ia:
        raise HTTPException(status_code=502, detail=res_ia.get("idea_solucion", "Error de IA"))

    patch_payload = {
        "categoria": res_ia.get("categoria", "Desconocida"),
        "tipo_problema": res_ia.get("tipo_problema", "Desconocido"),
        "impacto": res_ia.get("impacto", "Desconocido"),
        "idea_solucion": res_ia.get("idea_solucion", "Sin sugerencia"),
    }

    patch_res = await client.patch(
        f"{core.PB_URL}/api/collections/fricciones/records/{friction_id}",
        json=patch_payload,
    )
    if patch_res.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Error al actualizar IA: {patch_res.text}")

    return {"status": "ok", "analysis": res_ia}


@app.post("/analizar-con-ia", response_model=IAResponseWrapper)
async def api_analize_friction_endpoint(input_data: AnalyzeInput, request: Request):
    await _check_auth(request)
    try:
        resultado_ia = await core.analyze_with_ai(input_data.description)
        res = resultado_ia.get("response", {})
        if "error" in res:
            raise HTTPException(status_code=502, detail=res.get("idea_solucion", "Error de IA"))
        return {"analisis": res}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e!s}") from e


@app.delete("/fricciones/{friction_id}")
async def delete_friction(friction_id: str, request: Request):
    await _check_auth(request)
    client: httpx.AsyncClient = request.app.state.http_client
    res = await client.delete(f"{core.PB_URL}/api/collections/fricciones/records/{friction_id}")
    if res.status_code not in (200, 204):
        raise HTTPException(status_code=502, detail=f"Error al eliminar en PocketBase: {res.text}")
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(_request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})
