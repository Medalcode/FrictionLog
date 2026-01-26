import streamlit as st
import requests
import pandas as pd

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

        df["severity"] = df["severity"].fillna(1).astype(int)
        df["pain_score"] = df["severity"] * multiplier
        df = df.sort_values("pain_score", ascending=False)

        st.subheader("Oportunidades detectadas")
        st.dataframe(df[["id", "user_id", "description", "severity", "pain_score", "created_at"]])

        top = df.iloc[0]
        st.markdown("---")
        st.subheader("Idea principal")
        st.write(f"**Descripción:** {top['description']}")
        st.write(f"**Pain score:** {top['pain_score']}")
        st.write(f"**Severity:** {top['severity']}")
