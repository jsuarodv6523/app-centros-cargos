import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Analisis Centros", layout="wide")

st.title("Analisis de Centros Educativos")

# Subida de archivos
calplan_file = st.file_uploader("Calplan_Cargos", type="csv")
sipe_file = st.file_uploader("SIPE", type="csv")
enclave_file = st.file_uploader("AulaEnclaves", type="csv")
teoria_file = st.file_uploader("CargosTeoria", type="csv")

if calplan_file and sipe_file and enclave_file and teoria_file:

    
    df1 = pd.read_csv(
    calplan_file,
    sep="\t",
    encoding="latin1",
    on_bad_lines="skip"
    )
    df1.columns = df1.columns.str.strip()
    
        
    # Normalizar nombres
    df1.columns = df1.columns.str.strip().str.lower()
     
    # Detectar columnas automáticamente
    cargos = df1.groupby([
    "Código Centro",
    "Etapa Centro",
    "Nombre Centro"
    ]).size().reset_index(name="CargosReales")


    
    cargos = df1.groupby([
    codigo_col,
    etapa_col,
    nombre_col
    ]).size().reset_index(name="CargosReales")



    df2 = pd.read_csv(
    sipe_file,
    sep=None,
    engine="python",
    encoding="latin1",
    on_bad_lines="skip"
    )
    df2.columns = df2.columns.str.strip()
    df2["IdEstudio"] = pd.to_numeric(df2["IdEstudio"], errors="coerce")

    df_teoria = pd.read_csv(
    teoria_file,
    sep=None,
    engine="python",
    encoding="latin1",
    on_bad_lines="skip"
    )
    df_teoria.columns = df_teoria.columns.str.strip()
    df_teoria["N grupos Hasta"] = pd.to_numeric(df_teoria["N grupos Hasta"], errors="coerce")
    df_teoria["A. Enclaves"] = pd.to_numeric(df_teoria["A. Enclaves"], errors="coerce")
    df_teoria["N Cargos Teoria"] = pd.to_numeric(df_teoria["N Cargos Teoria"], errors="coerce")

    infantil = df2[df2["IdEstudio"].between(8424, 8429)]
    primaria = df2[df2["IdEstudio"].between(8430, 8435)]

    inf = infantil.groupby([
        "Código Centro",
        "Etapa Centro",
        "Nombre Centro"
    ])["Grupos Actual PRV"].sum().reset_index(name="Infantil")

    pri = primaria.groupby([
        "Código Centro",
        "Etapa Centro",
        "Nombre Centro"
    ])["Grupos Actual PRV"].sum().reset_index(name="Primaria")

    sipe = pd.merge(inf, pri,
        on=["Código Centro", "Etapa Centro", "Nombre Centro"],
        how="outer").fillna(0)

    df3 = pd.read_csv(
    enclave_file,
    sep=None,
    engine="python",
    encoding="latin1",
    on_bad_lines="skip"
    )
    df3.columns = df3.columns.str.strip()
    df3.columns = df3.columns.str.strip()
    df3 = df3.rename(columns={"A.ENCLAVE": "AulasEnclave"})

    df3["Isla"] = df3["Código Centro"].astype(str).str[:2]
    df3["Municipio"] = df3["Código Centro"].astype(str).str[:5]

    final = pd.merge(cargos, sipe,
        on=["Código Centro", "Etapa Centro", "Nombre Centro"],
        how="left").fillna(0)

    final = pd.merge(final, df3,
        on="Código Centro",
        how="left").fillna(0)

    final["TotalGrupos"] = final["Infantil"] + final["Primaria"]

    
def calcular_cargos(row):
    g = row["TotalGrupos"]
    e = row["AulasEnclave"]

    # Filtrar por aulas enclave
    posibles = df_teoria[df_teoria["A. Enclaves"] == e]

    # Buscar filas que cumplen el rango
    for _, r in posibles.iterrows():
        hasta = r["N grupos Hasta"]

        if pd.isna(hasta):
            continue

        if g <= hasta:
            return r["N Cargos Teoria"]

    return None


    final["CargosTeoricos"] = final.apply(calcular_cargos, axis=1)

    final["Diferencia"] = final["CargosReales"] - final["CargosTeoricos"]

    def estado(row):
        if row["Diferencia"] == 0:
            return "OK"
        elif row["Diferencia"] < 0:
            return "FALTAN"
        else:
            return "SOBRAN"

    final["Estado"] = final.apply(estado, axis=1)

    st.write(final)
