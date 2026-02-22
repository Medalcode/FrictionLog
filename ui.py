import streamlit as st
import requests
import pandas as pd
import time

API_URL_DEFAULT = "http://127.0.0.1:8000"

st.set_page_config(page_title="FrictionLog - Hub de Innovación", layout="wide")
st.title("🚀 FrictionLog")
st.write("Registra fricciones del día a día y deja que la IA proponga soluciones de arquitectura.")

api_base = st.sidebar.text_input("API Base URL", API_URL_DEFAULT)
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
    st.error(f"Error de conexión con la API: {data.get('error')}")
else:
    df = pd.DataFrame(data)
    
    # Sidebar: Registro
    st.sidebar.subheader("Nueva Fricción")
    with st.sidebar.form("new_friction_form"):
        new_desc = st.text_area("¿Qué te causó fricción hoy?")
        new_severity = st.slider("Severidad", 1, 5, 3)
        submitted = st.form_submit_button("Registrar 🚀")
        
        if submitted:
            if len(new_desc) < 10:
                st.error("La descripción debe tener al menos 10 caracteres.")
            else:
                ok, res = register_friction(api_base, new_desc, new_severity)
                if ok:
                    st.success("¡Fricción registrada!")
                    time.sleep(1)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Error: {res}")

    # Main Content
    if df.empty:
        st.info("No hay fricciones. ¡Captura la primera en la barra lateral!")
    else:
        st.subheader("Oportunidades de Innovación")
        
        # Simple priority calculation
        df["severity"] = df["severity"].fillna(1).astype(int)
        df = df.sort_values("severity", ascending=False)

        for _, row in df.iterrows():
            is_analyzed = row.get("nombre_comercial") is not None and row.get("nombre_comercial") != "N/A"
            
            label = f"#{row['id']} | Sev: {row['severity']} | {row['description'][:50]}..."
            if is_analyzed:
                label += f" ✅ {row['nombre_comercial']}"
            
            with st.expander(label):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"**Problema:** {row['description']}")
                    if is_analyzed:
                        st.markdown("---")
                        st.markdown("### 🧠 Propuesta de la IA")
                        st.write(f"**Producto:** {row.get('nombre_comercial')}")
                        st.write(f"**Categoría:** {row.get('categoria')}")
                        st.write(f"**Arquitectura:** {row.get('arquitectura')}")
                        st.success(f"**MVP Features:** {row.get('mvp_features')}")
                
                with c2:
                    if not is_analyzed:
                        if st.button("Analizar ⚡", key=f"ai_{row['id']}"):
                            with st.spinner("Generando arquitectura..."):
                                try:
                                    resp = requests.post(f"{api_base}/fricciones/{row['id']}/analizar")
                                    if resp.status_code == 200:
                                        st.rerun()
                                    else:
                                        st.error("Error en análisis")
                                except Exception as e:
                                    st.error(f"Error: {e}")
