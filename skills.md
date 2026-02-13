# Technical Skills & Standards 🛠️

This document outlines the specific technical capabilities and standards required for the **FrictionLog** project. These skills are mapped to the agents defined in `agents.md`.

## 1. Backend Development (FastAPI) ⚡
**Primary Agent:** Developer, Tech Lead

-   **Framework:** FastAPI
-   **Standards:**
    -   Use `Pydantic` models for all request/response validation.
    -   Type hinting is **mandatory** for all function signatures.
    -   Follow RESTful API design principles.
    -   Use `Dependency Injection` for database sessions and services.
    -   Async/Await: Use `async def` for I/O bound operations.
-   **Libraries:** `fastapi`, `pydantic`, `uvicorn`, `httpx`.

## 2. Frontend Development (Streamlit) 📊
**Primary Agent:** Developer, PM (for review)

-   **Framework:** Streamlit
-   **Standards:**
    -   Keep the UI simple, clean, and responsive ("Anti-Idea-Paralysis").
    -   Use `st.session_state` for state management carefully.
    -   Separate UI logic from business logic (View vs Controller).
    -   Use caching (`@st.cache_data`, `@st.cache_resource`) to optimize performance.
    -   Interactive elements should provide immediate feedback.
-   **Libraries:** `streamlit`, `pandas`, `altair` (charts).

## 3. Database Management (SQLite) 🗄️
**Primary Agent:** Developer, Tech Lead

-   **Technology:** SQLite (via standard Python `sqlite3` or lightweight ORM).
-   **Standards:**
    -   **Zero-Config:** The DB should initialize automatically if missing.
    -   Use parameterized queries to prevent SQL Injection.
    -   Schema changes should be documented (migrations).
    -   Keep it relational; normalize where appropriate but prioritize simplicity.
-   **Key Files:** `db_init.py`, schema definitions.

## 4. Testing & Quality Assurance 🧪
**Primary Agent:** QA Engineer, Developer

-   **Framework:** Pytest
-   **Standards:**
    -   **Unit Tests:** Test individual functions and logic in isolation.
    -   **Integration Tests:** Test API endpoints using `TestClient`.
    -   **Coverage:** Aim for high coverage on core business logic.
    -   **Benchmarks:** Monitor latency for critical endpoints.
-   **Libraries:** `pytest`, `pytest-asyncio`, `httpx`.

## 5. DevOps & Infrastructure 🚢
**Primary Agent:** Tech Lead, Developer

-   **Tools:** Docker, Git, Bash.
-   **Standards:**
    -   **Dockerfile:** Multi-stage builds for smaller images (if applicable).
    -   **Git:** Conventional Commits (e.g., `feat:`, `fix:`, `docs:`).
    -   **Environment:** Use `.env` files for configuration (never commit secrets).
    -   **Scripts:** Use `demo.sh` or `Makefile` for easy local setup.

## 6. Documentation & Process 📄
**Primary Agent:** PM, Tech Lead

-   **Standards:**
    -   **README.md:** Must be the single source of truth for setup and usage.
    -   **BITACORA.md:** Log all major architectural decisions and daily progress.
    -   **Code Comments:** Explain "Why", not just "What".
    -   **Docstrings:** Google or NumPy style for complex functions.

---

## Skill Acquisition Protocol

When a new technology or pattern is introduced:
1.  **Research:** The Tech Lead evaluates the trade-offs.
2.  **Document:** Update this `skills.md` file with the new standard.
3.  **Implement:** The Developer applies the new skill.
4.  **Verify:** The QA Engineer ensures the standard is met.
