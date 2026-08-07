import os
import time

import pandas as pd
import requests
import streamlit as st

API_URL_DEFAULT = os.getenv("API_URL", "http://127.0.0.1:8000")
FRICTIONLOG_API_KEY = os.getenv("FRICTIONLOG_API_KEY")

st.set_page_config(page_title="FrictionLog - Hub de Innovación", layout="wide")
st.title("FrictionLog")
st.write("Registra fricciones del día a día y deja que la IA proponga soluciones.")

api_base = st.sidebar.text_input("API Base URL", API_URL_DEFAULT)
api_key = st.sidebar.text_input(
    "API Key (opcional)", value=FRICTIONLOG_API_KEY or "", type="password"
)
st.sidebar.markdown("---")


def _headers():
    h = {}
    if api_key:
        h["Authorization"] = f"Bearer {api_key}"
    return h


@st.cache_data(ttl=30)
def fetch_fricciones(api_url):
    try:
        r = requests.get(f"{api_url}/fricciones", headers=_headers())
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def register_friction(api_url, description, severity):
    try:
        r = requests.post(
            f"{api_url}/registrar-friccion",
            json={"description": description, "severity": severity},
            headers=_headers(),
        )
        if r.status_code == 200:
            return True, r.json()
        return False, r.text
    except Exception as e:
        return False, str(e)


def delete_friction(api_url, friction_id):
    try:
        r = requests.delete(f"{api_url}/fricciones/{friction_id}", headers=_headers())
        if r.status_code == 200:
            return True, "Ok"
        return False, r.text
    except Exception as e:
        return False, str(e)


col1, col2 = st.sidebar.columns([3, 1])
col2.button("Refrescar", on_click=lambda: st.cache_data.clear())

data = fetch_fricciones(api_base)
if isinstance(data, dict) and data.get("error"):
    st.error(f"Error de conexión con la API: {data.get('error')}")
else:
    df = pd.DataFrame(data)

    st.sidebar.subheader("Nueva Fricción")
    with st.sidebar.form("new_friction_form"):
        new_desc = st.text_area("¿Qué te causó fricción hoy?")
        new_severity = st.slider("Severidad", 1, 5, 3)
        submitted = st.form_submit_button("Registrar")

        if submitted:
            if len(new_desc) < 10:
                st.error("La descripción debe tener al menos 10 caracteres.")
            else:
                ok, res = register_friction(api_base, new_desc, new_severity)
                if ok:
                    st.success("¡Fricción registrada!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Error: {res}")

    if df.empty:
        st.info("No hay fricciones. ¡Captura la primera en la barra lateral!")
    else:
        st.subheader("Oportunidades de Innovación")

        df["severity"] = df["severity"].fillna(1).astype(int)
        df = df.sort_values("severity", ascending=False)

        for _, row in df.iterrows():
            tp = str(row.get("tipo_problema", ""))
            is_analyzed = (
                row.get("tipo_problema") is not None and tp not in ("N/A", "") and "Error" not in tp
            )

            label = f"#{row['id']} | Sev: {row['severity']} | {str(row['description'])[:50]}..."
            if is_analyzed:
                label += f" ✅ {row['tipo_problema']}"

            with st.expander(label):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"**Problema:** {row['description']}")
                    if is_analyzed:
                        st.markdown("---")
                        st.markdown("### Propuesta de la IA")
                        st.write(f"**Producto:** {row.get('tipo_problema')}")
                        st.write(f"**Categoría:** {row.get('categoria')}")
                        st.write(f"**Impacto:** {row.get('impacto')}")
                        st.success(f"**MVP Features:** {row.get('idea_solucion')}")

                with c2:
                    if not is_analyzed and st.button(
                        "Guardar Análisis",
                        key=f"ai_{row['id']}",
                        help="Analizar y guardar en DB",
                    ):
                        with st.spinner("Generando arquitectura..."):
                            try:
                                resp = requests.post(
                                    f"{api_base}/fricciones/{row['id']}/analizar",
                                    headers=_headers(),
                                )
                                if resp.status_code == 200:
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    det = resp.json().get("detail", "desconocido")
                                    st.error(f"Error en análisis: {det}")
                            except Exception as e:
                                st.error(f"Error: {e}")

                    if st.button("Analizar con IA", key=f"live_{row['id']}", type="primary"):
                        with st.spinner("Consultando a la IA..."):
                            try:
                                res_ia = requests.post(
                                    f"{api_base}/analizar-con-ia",
                                    json={"description": row["description"]},
                                    headers=_headers(),
                                )

                                if res_ia.status_code == 200:
                                    data_ia = res_ia.json().get("analisis", {})
                                    st.success("¡Completado!")
                                    st.info(f"Categoría: {data_ia.get('categoria', 'N/A')}")
                                    impact = str(data_ia.get("impacto", "N/A")).upper()
                                    st.warning(f"Impacto: {impact}")
                                    st.error(f"Causa: {data_ia.get('tipo_problema', 'N/A')}")
                                    st.success(f"Idea: {data_ia.get('idea_solucion', 'N/A')}")
                                else:
                                    detalles = res_ia.json().get("detail", "Error desconocido")
                                    st.error(f"Fallo del modelo: {detalles}")
                            except Exception as e:
                                st.error(f"Error de red: {e}")

                    if st.button("Borrar", key=f"del_{row['id']}"):
                        ok, res = delete_friction(api_base, row["id"])
                        if ok:
                            st.success("Fricción borrada")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"Error al borrar: {res}")

