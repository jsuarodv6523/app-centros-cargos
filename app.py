import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Analisis Centros", layout="wide")

st.title("Analisis de Centros Educativos")

# Subida de archivos
calplan_file = st.file_uploader("Calplan_Cargos", type="csv")
sipe_file = st.file_uploader("SIPE", type="csv")
enclave_file = st.file_uploader("AulaEnclaves", type="csv")

if calplan_file and sipe_file and enclave_file:

    df1 = pd.read_csv(calplan_file, sep="\t")

    cargos = df1.groupby([
        "Código Centro",
        "Etapa Centro",
        "Nombre Centro"
    ]).size().reset_index(name="CargosReales")

    df2 = pd.read_csv(sipe_file, sep=";")
    df2["IdEstudio"] = pd.to_numeric(df2["IdEstudio"], errors="coerce")

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

    df3 = pd.read_csv(enclave_file, sep="\t")
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

        if e == 0:
            if g <= 5:
                return 1
            elif g <= 8:
                return 2
            elif g <= 17:
                return 3
            else:
                return 4

        if e == 1:
            if g <= 5:
                return 2
            elif g <= 8:
                return 3
            else:
                return 4

        if e == 2:
            if g <= 4:
                return 2
            elif g <= 7:
                return 3
            else:
                return 4

        return 4

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
