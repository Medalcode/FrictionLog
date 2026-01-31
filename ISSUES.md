# GitHub Issues Backlog for FrictionLog

Use this list to populate GitHub Issues or as a roadmap reference.

---

## 🟢 Good First Issues

### 1. [API] Validar longitud mínima en descripción de fricción

**Labels:** `good first issue`, `enhancement`, `api`
**Contexto:**
Actualmente, el endpoint `POST /registrar-friccion` acepta cadenas vacías o de 1 solo caracter si no se controlan bien, lo que genera "ruido" en la base de datos.
**Objetivo:**
Asegurar que las fricciones tengan suficiente contexto.
**Criterios de Aceptación:**

- [ ] Modificar `FrictionInput` en `app.py`.
- [ ] Implementar un validacor (Pydantic validator) que requiera mínimo 10 caracteres en `description`.
- [ ] Devolver un error 400 claro si no se cumple: "Description too short (min 10 chars)".

### 2. [Streamlit] Añadir filtro por Severidad en el Dashboard

**Labels:** `good first issue`, `dashboard`, `ui`
**Contexto:**
El dashboard muestra todas las fricciones. A medida que crezca la lista, será difícil encontrar las críticas.
**Objetivo:**
Permitir filtrar visualmente las fricciones más graves.
**Criterios de Aceptación:**

- [ ] Añadir un `st.sidebar.slider` o `selectbox` para filtrar por "Severidad Mínima" (1-5).
- [ ] La tabla de resultados debe actualizarse reactivamente según el filtro.

### 3. [Docs] Añadir diagrama de flujo y arquitectura al README

**Labels:** `good first issue`, `docs`
**Contexto:**
Los nuevos desarrolladores no ven claro cómo se conectan FastAPI, SQLite y Streamlit de un vistazo.
**Objetivo:**
Mejorar la sección de "Cómo funciona" en el README.
**Criterios de Aceptación:**

- [ ] Crear y añadir un diagrama simple (puede ser Mermaid o texto ASCII art) que muestre el flujo de datos.
- [ ] Explicar brevemente que Streamlit consume la API y no la BD directamente.

---

## 🚀 Mejoras de Producto

### 4. [Feature] Persistir resultados del análisis de IA

**Labels:** `enhancement`, `database`, `llm`
**Contexto:**
El endpoint `/analizar-con-ia` devuelve un análisis genial, pero este se pierde inmediatamente. Si quiero consultar ideas pasadas, tengo que volver a gastar tokens/tiempo en generarlas.
**Objetivo:**
Guardar el análisis enriquecido en la base de datos vinculado a la fricción original.
**Criterios de Aceptación:**

- [ ] Crear migración SQL para añadir columnas a la tabla `fricciones`: `ai_analysis_json` (TEXT) o campos separados (`nombre_comercial`, `mvp`).
- [ ] Crear un nuevo endpoint `POST /fricciones/{id}/analyze` que ejecute el análisis y guarde el resultado en la BD.

### 5. [CLI] Crear CLI wrapper simple (`fl log`)

**Labels:** `enhancement`, `dx`, `cli`
**Contexto:**
El usuario principal (Developer) vive en la terminal. Abrir Postman o escribir un `curl` largo causa... fricción.
**Objetivo:**
Capturar fricciones sin salir del flujo de trabajo en terminal.
**Criterios de Aceptación:**

- [ ] Crear un script `cli.py` (usando `typer` o `argparse`).
- [ ] Comando: `python cli.py log "Error al intentar borrar la caché de npm" --severity 3`.
- [ ] Debe hacer el POST a la API local y confirmar éxito.

### 6. [API] Soporte para 'Tags' (Etiquetas)

**Labels:** `enhancement`, `api`, `schema`
**Contexto:**
Solo tenemos "descripción". Necesitamos categorización manual básica (ej: `frontend`, `devops`, `bug`).
**Objetivo:**
Permitir enviar etiquetas al crear la fricción.
**Criterios de Aceptación:**

- [ ] Actualizar esquema de BD para soportar una columna `tags` (string separado por comas o tabla relacional simple).
- [ ] Actualizar `FrictionInput` para aceptar `tags: List[str]`.

---

## ⚙️ Issues Técnicos

### 7. [Refactor] Desacoplar capa de datos (Repository Pattern)

**Labels:** `refactor`, `technical`, `backend`
**Contexto:**
`app.py` contiene sentencias SQL crudas (`INSERT`, `SELECT`) mezcladas con la lógica HTTP. Esto dificulta los tests y futuras migraciones a Postgres.
**Objetivo:**
Mover toda la lógica SQL a un módulo `database.py` o `repository.py`.
**Criterios de Aceptación:**

- [ ] Crear funciones como `create_friction(...)`, `get_all_frictions(...)`.
- [ ] `app.py` no debe contener ninguna linea que empiece con `cur.execute`.
- [ ] La funcionalidad debe mantenerse intacta.

### 8. [LLM] Robustecer el parsing de JSON (Adiós Regex)

**Labels:** `bug`, `llm`, `reliability`
**Contexto:**
Usamos una expresión regular (`re.search`) para encontrar JSON en la respuesta del LLM. Esto es frágil y falla si el modelo añade texto extra o comillas malformadas.
**Objetivo:**
Garantizar que siempre obtenemos una estructura válida o un error controlado.
**Criterios de Aceptación:**

- [ ] Mejorar el Prompt para forzar formato JSON estricto.
- [ ] Usar librerías como `instructor` o validación con Pydantic directamente sobre la respuesta RAW, manejando excepciones de parseo (`json.JSONDecodeError`) de forma elegante con reitentos simples.
