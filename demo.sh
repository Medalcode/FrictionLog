#!/usr/bin/env bash
set -e
echo "Instalando dependencias..."
python3 -m pip install --upgrade pip
pip install -r requirements.txt
echo "Inicializando base de datos..."
python3 db_init.py
echo "Corriendo la app en http://127.0.0.1:8000 ..."
uvicorn app:app --reload --host 127.0.0.1 --port 8000 &
UVICORN_PID=$!
sleep 1
echo "Ejemplo: registrar una fricción (curl)"
curl -s -X POST http://127.0.0.1:8000/registrar-friccion -H "Content-Type: application/json" -d '{"user_id":"demo_user","description":"Ejemplo de fricción","severity":2}'
echo
echo "Docs: http://127.0.0.1:8000/docs"
echo "Para detener uvicorn: kill $UVICORN_PID"
