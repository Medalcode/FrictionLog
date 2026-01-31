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

1. **Clona y levanta**

   ```bash
   git clone https://github.com/Medalcode/FrictionLog.git && cd FrictionLog
   bash demo.sh
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
- **IA (Opcional):** Soporte para Ollama, Llama 3 o cualquier API compatible.

---

### 🔮 Roadmap

- [ ] **CLI Wrapper:** `fl log "esto apesta"` para registro instantáneo.
- [ ] **Persistencia IA:** Guardar los análisis generados automáticamente en base de datos.
- [ ] **Smart Grouping:** Detectar fricciones duplicadas semánticamente.

---

_Hecho con ❤️ para constructores._
