import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """INSTRUCCIÓN:
Eres un sistema experto en Product Discovery. Analiza la siguiente fricción y clasifícala.
Tu única salida debe ser un JSON estricto, sin bloques de código Markdown.
FRICCIÓN:
"{description}"

REGLAS ESTRICTAS:
1. "categoria": UNA SOLA palabra del dominio (ej: "UX", "DevOps", "Finanzas").
2. "tipo_problema": Breve descripción raíz del problema (máx 5-8 palabras).
3. "impacto": DEBE ser "alto", "medio" o "bajo" (minúscula).
4. "idea_solucion": Una oración corta proponiendo solución técnica o MVP.

ESQUEMA ESPERADO:
{{
  "categoria": "DevOps",
  "tipo_problema": "latencia alta en base de datos",
  "impacto": "alto",
  "idea_solucion": "implementar caché con redis para endpoints de lectura"
}}"""


class LLMProvider(ABC):
    @abstractmethod
    def analyze(self, description: str) -> dict[str, Any]: ...


class GeminiProvider(LLMProvider):
    def __init__(self):
        import google.generativeai as genai

        self._genai = genai
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY no configurada")
        self._genai.configure(api_key=api_key)

    def analyze(self, description: str) -> dict[str, Any]:
        model = self._genai.GenerativeModel("gemini-1.5-flash")
        generation_config = self._genai.types.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.2,
        )
        response = model.generate_content(
            PROMPT_TEMPLATE.format(description=description),
            generation_config=generation_config,
            request_options={"timeout": 15.0},
        )
        if not response.text:
            raise ValueError("Respuesta vacía de Gemini")
        return json.loads(response.text)


class GrokProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("XAI_API_KEY no configurada")
        self.base_url = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
        self.model = os.getenv("XAI_MODEL", "grok-4.20")

    def analyze(self, description: str) -> dict[str, Any]:
        import httpx

        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Eres experto en Product Discovery. Responde solo con JSON.",
                    },
                    {"role": "user", "content": PROMPT_TEMPLATE.format(description=description)},
                ],
                "temperature": 0.2,
                "max_tokens": 500,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)


_provider: LLMProvider | None = None


def _get_provider() -> LLMProvider:
    global _provider
    if _provider is None:
        provider_name = os.getenv("LLM_PROVIDER", "gemini").lower()
        _provider = GrokProvider() if provider_name == "grok" else GeminiProvider()
    return _provider


def analizar_friccion(description: str) -> dict[str, Any]:
    try:
        return _get_provider().analyze(description)
    except Exception as e:
        logger.exception("Error analizando fricción con IA")
        return {
            "categoria": "Sin clasificar",
            "tipo_problema": "Error de clasificación",
            "impacto": "Desconocido",
            "idea_solucion": "No se pudo generar una solución técnica en este momento.",
            "error": str(e),
        }


def reset_provider():
    global _provider
    _provider = None
