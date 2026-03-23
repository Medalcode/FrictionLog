import os
import json
import logging
from typing import Dict, Any

import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError, RetryError

# Configuración de logging para mantener la observabilidad
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración inicial de las credenciales
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    logger.warning("La variable de entorno GOOGLE_API_KEY no está configurada. Las llamadas a la API fallarán.")
else:
    genai.configure(api_key=API_KEY)


def analizar_friccion(description: str) -> Dict[str, Any]:
    """
    Analiza una descripción de fricción utilizando la API de Google Gemini.
    
    Args:
        description (str): La descripción del problema o fricción a analizar.
        
    Returns:
        dict: Diccionario parseado a partir del JSON devuelto por el modelo,
              con las claves 'categoria', 'tipo_problema', 'impacto', 'idea_solucion'.
    """
    if not API_KEY:
        logger.error("Intento de llamada a la API de Gemini sin GOOGLE_API_KEY configurada.")
        return _default_error_response("Configuración de credenciales faltante")

    prompt = f"""INSTRUCCIÓN:
Eres un sistema experto en Product Discovery. Analiza la siguiente fricción y clasifícala. Tu única salida debe ser un JSON estricto, sin bloques de código Markdown u otros textos adicionales.

FRICCIÓN:
"{description}"

REGLAS ESTRICTAS:
1. "categoria": DEBE ser estrictamente UNA SOLA palabra relacionada al dominio (ej: "UX", "DevOps", "Finanzas").
2. "tipo_problema": Breve descripción de la raíz del problema (máximo 5-8 palabras).
3. "impacto": DEBE ser estrictamente uno de los siguientes valores exactos (en minúscula): "alto", "medio" o "bajo".
4. "idea_solucion": Una sola oración corta y accionable proponiendo una solución técnica o MVP (1 frase).

ESQUEMA EJEMPLO ESPERADO:
{{
  "categoria": "DevOps",
  "tipo_problema": "latencia alta en base de datos",
  "impacto": "alto",
  "idea_solucion": "implementar caché con redis para endpoints de lectura"
}}"""

    try:
        # Usamos gemini-1.5-flash: Recomendado para operaciones rápidas JSON y baja latencia en backends
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # GenerationConfig: Fuerza la salida requerida explícitamente a application/json
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.2, # Temperatura baja para un formateo esquemático y determinista
        )

        # Usamos request_options para gestionar un timeout razonable y no bloquear el request de FastAPI
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            request_options={"timeout": 15.0} 
        )

        if not response.text:
            logger.error("La respuesta de Gemini fue devuelta vacía (posiblemente interceptada por bloqueos de seguridad).")
            return _default_error_response("Respuesta vacía o bloqueada por seguridad")

        # Parseo robusto del contenido
        parsed_data = json.loads(response.text)
        return parsed_data

    except json.JSONDecodeError as json_err:
        logger.error(f"Error parseando el JSON generado por Gemini: {json_err}. Respuesta cruda: {response.text}")
        return _default_error_response("Respuesta no parseable (Invalid JSON)")

    except (GoogleAPIError, RetryError) as api_err:
        logger.error(f"Error de red o comunicación con la API de Google: {api_err}")
        return _default_error_response("Falla de red o de la API de Google")

    except Exception as exc:
        logger.exception(f"Error interno inesperado al procesar la fricción: {exc}")
        return _default_error_response("Error interno inesperado del servidor")


def _default_error_response(motivo: str = "Error desconocido") -> Dict[str, Any]:
    """
    Retorna un diccionario de fallback para evitar excepciones no controladas
    que rompan nuestros endpoints (Fail-safe pattern).
    """
    return {
        "categoria": "Sin clasificar",
        "tipo_problema": f"Error de clasificación ({motivo})",
        "impacto": "Desconocido",
        "idea_solucion": "No se pudo generar una solución técnica en este momento por fallas en la integración de IA."
    }
