# FrictionLog

FrictionLog es una API ligera para capturar "fricciones" (pain-points) detectadas por desarrolladores o usuarios, almacenarlas en SQLite y priorizarlas para generar ideas de proyectos.

## Resumen
FrictionLog permite enviar fricciones vía API, almacenarlas en una base de datos ligera y consultarlas desde endpoints REST. Ideal como backend para tu "Laboratorio de Ideas".

## Requisitos
- Python 3.11 (o 3.10+)
- pip

Variables de entorno (opcional)
- `LLM_API_URL`: URL del servicio LLM (ej. http://localhost:11434). Si se configura, el endpoint `/analizar-con-ia` intentará usarlo.
- `LLM_MODEL`: Nombre del modelo a usar (por ejemplo `llama3`). Si no se especifica, `llama3` será el valor por defecto.

## Instalación rápida
1. Clonar el repo
2. Instalar dependencias

```bash
pip install -r requirements.txt
```

3. Inicializar la base de datos

```bash
python3 db_init.py
```

## Cómo ejecutar el demo local

1) Inicia la API (uvicorn):

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

2) Registrar una fricción (ejemplo):

```bash
curl -X POST http://127.0.0.1:8000/registrar-friccion -H "Content-Type: application/json" -d '{"user_id":"demo_user","description":"Ejemplo de fricción","severity":2}'
```

3) Documentación interactiva (Swagger):

http://127.0.0.1:8000/docs

## Dashboard opcional (Streamlit)

También incluimos un dashboard rápido para visualizar y priorizar fricciones usando Streamlit.

Instalar y ejecutar:

```bash
pip install streamlit
streamlit run streamlit_app.py
```

Desde la barra lateral puedes configurar la URL base de la API (por defecto http://127.0.0.1:8000) y ajustar los parámetros de priorización.

## Estructura del repo
- app.py — API FastAPI principal
- db_init.py — inicializa `frictionlog.db`
- requirements.txt — dependencias
- demo.sh — script para instalar, inicializar y ejecutar demo

## Contribuir
- Abre issues o PRs. Añade tests y documentación para nuevas funciones.

## Licencia
- Añadir licencia (por defecto: MIT si lo deseas).

## Contacto
- Rellena con tu nombre y email.

## Bitácora

Revisa `BITACORA.md` en la raíz del proyecto para ver el registro de tareas realizadas y pendientes.

# FrictionLog