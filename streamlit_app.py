import streamlit as st
import requests
import pandas as pd
import time

API_URL_DEFAULT = "http://127.0.0.1:8000"

st.set_page_config(page_title="Laboratorio de Ideas - FrictionLog", layout="wide")
st.title("🚀 Laboratorio de Ideas — FrictionLog")
st.write("Visualiza las fricciones registradas y calcula un `pain_score` simple para priorizar ideas.")

api_base = st.sidebar.text_input("API base URL", API_URL_DEFAULT)
st.sidebar.markdown("---")



@st.cache_data
def fetch_fricciones(api_url):
    try:
        r = requests.get(f"{api_url}/fricciones")
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def register_friction(api_url, description, severity):
    try:
        r = requests.post(
            f"{api_url}/registrar-friccion", 
            json={"description": description, "severity": severity}
        )
        if r.status_code == 200:
            return True, r.json()
        return False, r.text
    except Exception as e:
        return False, str(e)



data = fetch_fricciones(api_base)
if isinstance(data, dict) and data.get("error"):
    st.error(f"Error al obtener fricciones: {data.get('error')}")
else:
    df = pd.DataFrame(data)
    if df.empty:
        st.info("No hay fricciones registradas. Usa demo.sh o el endpoint /registrar-friccion para crear datos de prueba.")
    else:
        st.sidebar.header("Parámetros de priorización")
        freq_map = {"Diario": 5, "Semanal": 3, "Única vez": 1}
        default_freq = st.sidebar.selectbox("Frecuencia por defecto", list(freq_map.keys()), index=1)
        multiplier = freq_map[default_freq]

        st.sidebar.markdown("---")
        st.sidebar.subheader("Registrar Fricción")
        with st.sidebar.form("new_friction_form"):
            new_desc = st.text_area("Descripción del problema")
            new_severity = st.slider("Severidad (1-5)", 1, 5, 3)
            submitted = st.form_submit_button("Registrar 🚀")
            
            if submitted:
                if not new_desc:
                    st.error("¡Falta la descripción!")
                else:
                    ok, res = register_friction(api_base, new_desc, new_severity)
                    if ok:
                        st.success(f"Registrado ID: {res.get('id')}")
                        time.sleep(1) # Give time to show success
                        st.cache_data.clear() # Invalidate cache
                        st.rerun()
                    else:
                        st.error(f"Error: {res}")


        df["severity"] = df["severity"].fillna(1).astype(int)
        df["pain_score"] = df["severity"] * multiplier
        df = df.sort_values("pain_score", ascending=False)

        st.subheader("Oportunidades detectadas")
        st.subheader("Oportunidades detectadas")
        
        for index, row in df.iterrows():
            # Check if analyzed
            is_analyzed = row.get("nombre_comercial") is not None and row.get("nombre_comercial") != "N/A"
            
            title = f"#{row['id']} - {row['description'][:60]}..."
            if is_analyzed:
                title += f" ✅ {row['nombre_comercial']}"
            
            with st.expander(title):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Problema:** {row['description']}")
                    st.write(f"**Severidad:** {row['severity']} | **Pain Score:** {row['pain_score']}")
                    
                    if is_analyzed:
                        st.markdown("### 🧠 Análisis de IA")
                        st.write(f"**Categoría:** {row.get('categoria', 'N/A')}")
                        st.write(f"**Arquitectura:** {row.get('arquitectura', 'N/A')}")
                        st.info(f"**MVP:** {row.get('mvp_features', 'N/A')}")
                    else:
                        st.warning("Aún no analizado por IA.")
                
                with col2:
                    if not is_analyzed:
                        if st.button(f"Analizar con IA ⚡", key=f"btn_{row['id']}"):
                            with st.spinner("Consultando al oráculo..."):
                                try:
                                    resp = requests.post(f"{api_base}/fricciones/{row['id']}/analizar")
                                    if resp.status_code == 200:
                                        st.success("¡Analizado!")
                                        st.rerun()
                                    else:
                                        st.error(f"Error: {resp.text}")
                                except Exception as e:
                                    st.error(f"Fallo de conexión: {e}")
