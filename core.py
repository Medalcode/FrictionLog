import asyncio
import os
from typing import Dict, Any

from llm_client import analizar_friccion

# Pocketbase endpoint por defecto
PB_URL = os.getenv("POCKETBASE_URL", "http://127.0.0.1:8090")

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
