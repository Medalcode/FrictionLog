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

#### Opción A: Docker + PocketBase (Recomendado)

1. **Configura tu Base de Datos**
   Descarga y ejecuta [PocketBase](https://pocketbase.io/). Importa el archivo `pocketbase_schema.json` desde su panel de administrador (`http://127.0.0.1:8090/_/`).

2. **Clona y levanta**

   ```bash
   git clone https://github.com/Medalcode/FrictionLog.git && cd FrictionLog
   export GOOGLE_API_KEY="tu_clave_aqui" # Necesario para Gemini
   docker-compose up --build -d
   ```

3. **Servicios**
   - **Dashboard:** [http://localhost:8501](http://localhost:8501)
   - **API:** [http://localhost:8000/docs](http://localhost:8000/docs)

#### Opción B: Local (Python)

1. **Instala y ejecuta**

   ```bash
   # Clona
   git clone https://github.com/Medalcode/FrictionLog.git && cd FrictionLog
   
   # Setup entorno y dependencias
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Configurar Entorno e IPs
   export GOOGLE_API_KEY="tu_clave_aqui" # En Windows usa: $env:GOOGLE_API_KEY="tu_clave"
   export POCKETBASE_URL="http://127.0.0.1:8090"
   
   # Ejecuta API y Dashboard (en terminales separadas)
   uvicorn api:app --reload
   streamlit run ui.py
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

### 🛠 Estructura Lean & Stack

Arquitectura desacoplada para máxima hackeabilidad.

- **`api.py`**: Interfaz RESTful ligera asíncrona con FastAPI.
- **`core.py`**: Motor de lógica y orquestador hacia la BD.
- **`llm_client.py`**: Cliente estricto Pydantic + Google Gemini (1.5 Flash).
- **`ui.py`**: Dashboard visual con Streamlit (Maneja Live Analytics y persistencia base).
- **`docs/`**: Documentación técnica y bitácora.
- **DB:** PocketBase (Reemplaza a SQLite para soportar persistencia distribuida y Serverless en Vercel/Cloud Run).
- **IA:** Google AI Studio (Gemini) vía SDK oficial.

---

### 🤝 Desarrollo

Consulta nuestras guías internas para contribuir (ahora en `/docs`):
- [Roles de Agentes](./docs/agents.md): Estructura del equipo simulado.
- [Skills y Estándares](./docs/skills.md): Guías técnicas y mejores prácticas.
- [Bitácora](./docs/BITACORA.md): Registro de decisiones arquitectónicas.

---

### 🔮 Roadmap

- [x] **Persistencia IA:** Guardar los análisis generados automáticamente en base de datos.
- [ ] **CLI Wrapper:** `fl log "esto apesta"` para registro instantáneo.
- [ ] **Smart Grouping:** Detectar fricciones duplicadas semánticamente.

---

_Hecho con ❤️ para constructores._
