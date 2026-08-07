# Changelog — FrictionLog

## [2026-08-06] Auditoría y Refactorización de Calidad Técnica

### Cambios
- **Inyección de Dependencias FastAPI**: Migrada la validación de autenticación a `dependencies=[Depends(_check_auth)]` en todos los endpoints de `api.py`.
- **Despachador Seguro de Red (`_safe_pb_request`)**: Implementado manejo centralizado de peticiones HTTP a PocketBase capturando fallos de red (`httpx.RequestError`).
- **Singleton Thread-Safe (`llm_client.py`)**: Protegida la inicialización de proveedores LLM con `threading.Lock()` para eliminar race conditions en cargas concurrentes.
- **Optimización de UI**: Removidas llamadas bloqueantes `time.sleep(1)` en la interfaz Streamlit para un renderizado asíncrono e instantáneo.
- **Compatibilidad Linux Docker**: Agregado `extra_hosts: ["host.docker.internal:host-gateway"]` a `docker-compose.yml`.
- **Resiliencia en CLI**: Añadido soporte de timeouts y códigos de salida `sys.exit(1)` con mensajes estandarizados a `stderr` en `cli.py`.

## [2026-06-21] Refactor mayor: abstracción LLM, auth, limpieza


### Cambios
- **Abstracción de proveedor LLM**: Nueva arquitectura con `LLMProvider` ABC.
  - `GeminiProvider`: Google Gemini 1.5 Flash (default)
  - `GrokProvider`: xAI Grok vía API compatible OpenAI
  - Selección via `LLM_PROVIDER=gemini|grok`
- **Auth**: Nuevo sistema opcional via `FRICTIONLOG_API_KEY`. Si se setea, todos los endpoints requieren `Authorization: Bearer <key>`.
- **Mapeo de claves simplificado**: Se eliminaron las capas de traducción (`nombre_comercial`, `arquitectura_sugerida`, `funcionalidad_clave_mvp`). Ahora todos los componentes usan el mismo formato canónico: `categoria`, `tipo_problema`, `impacto`, `idea_solucion`.
- **Cliente HTTP reutilizable**: `httpx.AsyncClient` ahora se crea una sola vez via lifespan de FastAPI, en vez de uno por request.
- **Eliminación de archivos muertos**: `app.py` (legacy vacío), `CHANGELOG.md` antiguo (era de PocketBase).
- **CI unificado**: Workflow único con tests en 3 versiones de Python + linting con ruff.
- **Dependencias fijas**: `requirements.txt` con versiones pinned.
- **`.env.example`**: Documentación correcta de todas las variables de entorno.
- **Tests**: Agregados tests de auth, error de LLM, + adaptados al nuevo mapeo.

### Deuda técnica
- [ ] Falta integración nativa de PocketBase en el stack (vs. HTTP externo)
- [ ] Tests de integración con PocketBase real
- [ ] CI/CD para deploy automático

## [2026-05-21] Corrección de Mapeo de Claves y Tests

### Cambios
- Corregido mapeo de claves IA en `api.py`
- Tests reescritos con mocking de `httpx.AsyncClient`
- Agregado test para endpoint `/analizar-con-ia`

## [2026-01-31] Refinamiento de Producto

### Cambios
- README reescrito orientado a value-proposition
- Roadmap v1.0 y v2.0 definido

## [2026-01-26] MVP Inicial

### Cambios
- API básica FastAPI (`/registrar-friccion`, `/fricciones`)
- Integración con Ollama/LLM
- Dockerfile de desarrollo
- Dashboard Streamlit
