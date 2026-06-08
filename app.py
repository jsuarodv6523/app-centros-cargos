import streamlit as st
import pandas as pd

st.set_page_config(page_title="Analisis Centros", layout="wide")
st.title("Analisis de Centros Educativos")

# Subida de archivos
calplan_file = st.file_uploader("Calplan_Cargos", type="csv")
sipe_file = st.file_uploader("SIPE", type="csv")
enclave_file = st.file_uploader("AulaEnclaves", type="csv")
teoria_file = st.file_uploader("CargosTeoria", type="csv")

if calplan_file and sipe_file and enclave_file and teoria_file:

    # =========================
    # CALPLAN
    # =========================
    df1 = pd.read_csv(calplan_file, sep=None, engine="python", encoding="latin1", on_bad_lines="skip")
    df1.columns = df1.columns.str.strip()

    if len(df1.columns) < 3:
        st.error("Error leyendo Calplan_Cargos")
        st.stop()

    codigo_col = df1.columns[0]
    etapa_col = df1.columns[1]
    nombre_col = df1.columns[2]

    cargos = df1.groupby([codigo_col, etapa_col, nombre_col]).size().reset_index(name="CargosReales")
    cargos.columns = ["Código Centro", "Etapa Centro", "Nombre Centro", "CargosReales"]

    # =========================
    # SIPE
    # =========================
    df2 = pd.read_csv(sipe_file, sep=";", encoding="latin1", on_bad_lines="skip")
    df2.columns = df2.columns.str.strip()

    df2["IdEstudio"] = pd.to_numeric(df2["IdEstudio"], errors="coerce")
    df2["Grupos Actual PRV"] = pd.to_numeric(df2["Grupos Actual PRV"], errors="coerce").fillna(0)

    infantil = df2[df2["IdEstudio"].between(8424, 8429)]
    primaria = df2[df2["IdEstudio"].between(8430, 8435)]

    inf = infantil.groupby(["Código Centro", "Etapa Centro", "Nombre Centro"])["Grupos Actual PRV"].sum().reset_index(name="Infantil")
    pri = primaria.groupby(["Código Centro", "Etapa Centro", "Nombre Centro"])["Grupos Actual PRV"].sum().reset_index(name="Primaria")

    sipe = pd.merge(inf, pri, how="outer",
        on=["Código Centro", "Etapa Centro", "Nombre Centro"]
    ).fillna(0)

    # =========================
    # ENCLAVES
    # =========================
