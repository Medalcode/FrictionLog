# FrictionLog ⚡

**Convierte la frustración en tu próximo proyecto.**  
FrictionLog es una API ligera que captura "puntos de dolor" (fricciones) diarios, los analiza con IA y los prioriza para que construyas soluciones que la gente realmente necesita.

---

### "Odio hacer esto manualmente..."

¿Cuántas veces has pensado eso y luego lo has olvidado?  
Como desarrolladores o Indie Hackers, a menudo buscamos ideas "revolucionarias" mientras ignoramos los problemas reales que tenemos delante. **FrictionLog** actúa como un buzón de quejas inteligente:

1. **Captura** la molestia en el momento (vía CLI o API).
2. **Centraliza** tus frustraciones.
3. **Genera** especificaciones técnicas automáticas (MVP) usando LLMs.

---

### 🚀 Quickstart

#### Opción A: Docker (Recomendado)

1. **Clona y levanta**

   ```bash
   git clone https://github.com/Medalcode/FrictionLog.git && cd FrictionLog
   docker-compose up --build -d
   ```

2. **Servicios**
   - **Dashboard:** [http://localhost:8501](http://localhost:8501)
   - **API:** [http://localhost:8000/docs](http://localhost:8000/docs)

#### Opción B: Local (Python)

1. **Instala y ejecuta**

   ```bash
   # Clona
   git clone https://github.com/Medalcode/FrictionLog.git && cd FrictionLog
   
   # Setup entorno
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Ejecuta API y Dashboard (en terminales separadas)
   uvicorn app:app --reload
   streamlit run streamlit_app.py
   ```

2. **Registra una fricción (tu primer pain-point)**

   ```bash
   curl -X POST http://127.0.0.1:8000/registrar-friccion \
        -H "Content-Type: application/json" \
        -d '{"description": "Odio copiar datos de facturas PDF a Excel manualmente", "severity": 4}'
   ```

3. **Visualiza y Prioriza**  
   Abre el dashboard en `http://localhost:8501` para ver qué deberías construir primero.

---

### 💡 Casos de Uso

- **Para Indie Hackers:** Valida ideas basándote en quejas recurrentes, no en suposiciones.
- **Para equipos de Plataforma/DevOps:** Detecta qué herramientas internas están frenando al equipo.
- **Para DevRel:** Recolecta feedback crudo y prioriza fixes en tu librería.

---

### 🛠 Stack Técnico

Simple, hackeable y sin dependencias pesadas.

- **Core:** FastAPI (Python)
- **DB:** SQLite (cero configuración)
- **UI:** Streamlit (Dashboard instantáneo)
- **Infra:** Docker & Docker Compose
- **IA (Opcional):** Soporte para Ollama, Llama 3 o cualquier API compatible.

---

### 🤝 Desarrollo

Consulta nuestras guías internas para contribuir:
- [Roles de Agentes](./agents.md): Estructura del equipo simulado.
- [Skills y Estándares](./skills.md): Guías técnicas y mejores prácticas.

---

### 🔮 Roadmap

- [ ] **CLI Wrapper:** `fl log "esto apesta"` para registro instantáneo.
- [ ] **Persistencia IA:** Guardar los análisis generados automáticamente en base de datos.
- [ ] **Smart Grouping:** Detectar fricciones duplicadas semánticamente.

---

_Hecho con ❤️ para constructores._
