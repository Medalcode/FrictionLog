# Technical Skills & Standards 🛠️

This document outlines the specific technical capabilities and standards required for the **FrictionLog** project. These skills are mapped to the agents defined in `agents.md`.

## 1. Full-Stack Implementation (Param: `target`) ⚡
**Agente:** Agente Generalista
-   **Si `target` = "backend" (FastAPI):**
    -   Validación estricta con `Pydantic`. Type hinting mandatorio.
    -   Arquitectura RESTful con Inyección de Dependencias.
    -   Uso de `async/await` para operaciones de E/S.
-   **Si `target` = "frontend" (Streamlit):**
    -   UI limpia "Anti-Idea-Paralysis". Estado via `st.session_state`.
    -   Separación clara entre lógica de vista y lógica de negocio.
    -   Optimización via `@st.cache_data`.

## 2. Engineering Operations (Param: `focus`) 🚢
**Agente:** Agente Generalista
-   **Si `focus` = "data" (SQLite):**
    -   **Zero-Config:** Auto-inicialización de DB. Consultas parametrizadas.
    -   Esquemas normalizados pero simples. Documentación de migraciones in-code.
-   **Si `focus` = "infra" (Docker/CLI):**
    -   Dockerfiles multi-stage. Convención de commits (Conventional Commits).
    -   Automatización via `demo.sh`. Configuración via `.env`.

## 3. Quality & Governance (Param: `type`) 🧪
**Agente:** Agente Generalista
-   **Si `type` = "testing" (Pytest):**
    -   Tests unitarios para lógica core. Integration tests con `TestClient`.
    -   Monitoreo de latencia en endpoints críticos.
-   **Si `type` = "docs":**
    -   `README.md` como fuente única de verdad.
    -   `BITACORA.md` para registro de decisiones (ADR) y progreso diario.
    -   Docstrings estilo Google para funciones complejas. explicaciones de "Por qué", no "Qué".

---

## Skill Acquisition Protocol

When a new technology or pattern is introduced:
1.  **Research:** The Tech Lead evaluates the trade-offs.
2.  **Document:** Update this `skills.md` file with the new standard.
3.  **Implement:** The Developer applies the new skill.
4.  **Verify:** The QA Engineer ensures the standard is met.
