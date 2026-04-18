#!/usr/bin/env bash
# Ejecuta las pruebas unitarias e integración en el entorno de Docker y limpia el contenedor temporal
docker-compose run --rm test
