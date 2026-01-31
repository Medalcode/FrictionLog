# Bitácora de Ingeniería — FrictionLog

Este documento registra la evolución del proyecto, no solo como lista de tareas, sino como historial de decisiones arquitectónicas y lecciones aprendidas.

## Estructura de Entradas

Cada entrada significativa debe seguir este formato:

- **[Fecha] Contexto**: Breve descripción del estado o sprint.
- **Decisiones (ADR simplificado)**: Por qué elegimos X tecnología o patrón.
- **Cambios Realizados**: Log técnico conciso.
- **Aprendizajes/Deuda**: Qué descubrimos y qué dejamos para después.

---

## Historial

### [2026-01-31] Refinamiento de Producto y Documentación

**Contexto**: Pivote hacia mejorar la claridad del producto y la experiencia del desarrollador (DX), enfocándose en el valor "Anti-Idea-Paralysis".

**Decisiones Técnicas**:

- **README orientado a Value-Prop**: Se reescribió la documentación para vender el problema primero, no la tecnología. El usuario debe entender "para qué sirve" en 5 segundos.
- **Separación Conceptual**: Se definió claramente que Streamlit es solo un "visor" y la lógica reside en FastAPI.
- **Estrategia de IA Pragmática**: Se decidió limitar el uso de LLM a tareas de "enriquecimiento" y "generación creativa", prohibiendo su uso para lógica determinista (validaciones) para evitar costes y latencia innecesaria.

**Cambios Realizados**:

- Reescriptura completa del `README.md` (Ver commit).
- Definición de Roadmap v1.0 y v2.0.
- Creación de issues estandarizados para GitHub (Labels: `good first issue`, `enhancement`).

**Deuda Identificada**:

- Faltan tests unitarios (`pytest`).
- El endpoint de IA es síncrono y bloqueante.
- No hay persistencia de los análisis generados por IA.

### [2026-01-26] MVP Inicial y Fundación

**Contexto**: Bootstrapping del proyecto. Objetivo: tener algo funcionando en < 2 horas.

**Decisiones Técnicas**:

- **SQLite vs Postgres**: Se eligió SQLite para `db_init.py` para permitir "Zero-Config" deployment. Prioridad: Hackeabilidad > Escalabilidad inmediata.
- **Streamlit**: Se usó para el dashboard para evitar escribir JS/React en la fase de prototipo.
- **Heurística de Fallback**: Se implementó lógica `if/else` simple si el LLM falla, garantizando robustez.

**Cambios Realizados**:

- API básica FastAPI (`/registrar-friccion`, `/fricciones`).
- Integración básica con Ollama/LLM genérico.
- Dockerfile de desarrollo.

---

## Backlog de Decisiones Pendientes (To-Decide)

- **Persistencia de vectores**: ¿Usar `pgvector` en el futuro o una librería ligera como `ChromaDB` local para deduplicación semántica?
- **Auth**: ¿Implementar API Keys simples o OAuth completo? (Tendencia: API Keys simples por ahora).
