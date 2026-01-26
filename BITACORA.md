# Bitácora de desarrollo — FrictionLog

Fecha: 2026-01-26

Resumen: Registro de tareas realizadas y pendientes durante la creación del proyecto "FrictionLog".

Tareas realizadas
- Inicialización del proyecto y creación de la API básica con FastAPI (`app.py`): endpoints `/registrar-friccion` y `/fricciones`.
- Script de inicialización de base de datos: `db_init.py` (crea `frictionlog.db` y tabla `fricciones`).
- `requirements.txt` creado con dependencias mínimas: `fastapi`, `uvicorn[standard]`, `pydantic`, `requests`, `streamlit`.
- Script demo `demo.sh` que instala dependencias, inicializa la base de datos y lanza la app con un `curl` de ejemplo.
- `README.md` con instrucciones de instalación y uso básico.
- Endpoint `/analizar-con-ia` añadido en `app.py` con:
  - soporte heurístico local
  - integración opcional con LLM vía variable de entorno `LLM_API_URL` (soporta Ollama y endpoints genéricos)
  - función `call_llm()` para llamadas y parseo robusto de la respuesta
- `Dockerfile` y `docker-compose.yml` añadidos para desarrollo.
- `.env.example` para documentar `LLM_API_URL`.
- Dashboard básico con Streamlit: `streamlit_app.py` (consulta `/fricciones` y calcula `pain_score`).
- Verificación de sintaxis de los ficheros Python mediante `python -m py_compile`.

Tareas pendientes / sugeridas
- (Opcional) Integrar parseo específico de output de Ollama según formato esperado y tests unitarios para `/analizar-con-ia`.
- Añadir migraciones con Alembic y extender el esquema (campos `intensidad`, `frecuencia`, `analisis_ia` como FK hacia tabla de análisis).
- Añadir pruebas unitarias y CI (GitHub Actions) que ejecuten lint, tests y chequeo de seguridad de dependencias.
- Preparar Dockerfile multistage para producción y `Makefile` con tareas comunes (`make build`, `make run`, `make test`).
- Mejorar el dashboard: añadir filtros, heatmap y visualización de métricas (Pain Score, MVP Speed).
- Integrar almacenamiento persistente en producción (Postgres) y añadir opciones de configuración por entorno.

Commits y despliegue
- Se incluirá este fichero en el siguiente commit junto con la actualización del `README.md`.

Notas
- Si deseas que mueva aquí una bitácora ya existente, indícamela y la consolidaré en este `BITACORA.md`.
