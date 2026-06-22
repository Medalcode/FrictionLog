import asyncio
import os
from typing import Any

from llm_client import analizar_friccion

PB_URL = os.getenv("POCKETBASE_URL", "http://127.0.0.1:8090")


async def analyze_with_ai(description: str) -> dict[str, Any]:
    resultado = await asyncio.to_thread(analizar_friccion, description)
    return {
        "from": "llm",
        "response": resultado,
    }
