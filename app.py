import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Análisis Centros", layout="wide")

st.title("📊 Análisis de Cargos en Centros Educativos")

# =========================
# SUBIDA DE ARCHIVOS
# =========================
col1, col2 = st.columns(2)

with col1:
    calplan_file = st.file_uploader("1️⃣ Calplan_Cargos", type="csv")
    sipe_file = st.file_uploader("2️⃣ SIPE", type="csv")

with col2:
    enclave_file = st.file_uploader("3️⃣ AulaEnclaves", type="csv")
    teoria_file = st.file_uploader("4️⃣ CargosTeoria", type="csv")

if calplan_file and sipe_file and enclave_file:

    # ---- CALPLAN ----
    df1 = pd.read_csv(calplan_file, sep="\t")

    cargos = (
        df1.groupby(["Código Centro", "Etapa Centro", "Nombre Centro"])
        .size()
        .reset_index(name="CargosReales")
    )

    # ---- SIPE ----
    df2 = pd.read_csv(sipe_file, sep=";")
    df2["IdEstudio"] = pd.to_numeric(df2["IdEstudio"], errors="coerce")

    infantil = df2[df2["IdEstudio"].between(8424, 8429)]
    primaria = df2[df2["IdEstudio"].between(8430, 8435)]

    inf = infantil.groupby(
        ["Código Centro", "Etapa Centro", "Nombre Centro"]
    )["Grupos Actual PRV"].sum().reset_index(name="Infantil")

    pri = primaria.groupby(
        ["Código Centro", "Etapa Centro", "Nombre Centro"]
    )["Grupos Actual PRV"].sum().reset_index(name="Primaria")

    sipe = pd.merge(inf, pri,
        on=["Código Centro", "Etapa Centro", "Nombre Centro"],
        how="outer"
    ).fillna(0)

    # ---- ENCLAVES ----
    df3 = pd.read_csv(enclave_file, sep="\t")
    df3 = df3.rename(columns={"A.ENCLAVE": "AulasEnclave"})

    # Isla y municipio
    df3["Isla"] = df3["Código Centro"].astype(str).str[:2]
    df3["Municipio"] = df3["Código Centro"].astype(str).str[:5]

    # ---- UNIÓN ----
    final = pd.merge(cargos, sipe,
        on=["Código Centro", "Etapa Centro", "Nombre Centro"],
        how="left"
    ).fillna(0)

    final = pd.merge(final, df3,
        on="Código Centro",
        how="left"
    ).fillna(0)

    # ---- TOTAL GRUPOS ----
    final["TotalGrupos"] = final["Infantil"] + final["Primaria"]

    # ---- CARGOS TEÓRICOS ----
    def calcular_cargos(row):
        g = row["TotalGrupos"]
        e = row["AulasEnclave"]

        if e == 0:
            if g <= 5: return 1
            elif g <= 8: return 2
            elif g <= 17: return 3
            else: return 4

        if e == 1:
            if g <= 5: return 2
            elif g <= 8: return 3
            else: return 4

        if e == 2:
            if g <= 4: return 2
            elif g <= 7: return 3
            else: return 4

        return 4

    final["CargosTeoricos"] = final.apply(calcular_cargos, axis=1)

    # ---- DIFERENCIA ----
    final["Diferencia"] = final["CargosReales"] - final["CargosTeoricos"]

    # ---- SEMÁFORO ----
    def estado(row):
        if row["Diferencia"] == 0:
            return "🟢 OK"
        elif row["Diferencia"] < 0:
            return "🔴 FALTAN"
        else:
            return "🟡 SOBRAN"

    final["Estado"] = final.apply(estado, axis=1)

    # =========================
    # FILTROS
    # =========================
    st.sidebar.header("🔎 Filtros")

    isla_sel = st.sidebar.multiselect(
        "Isla",
        sorted(final["Isla"].unique())
    )

    municipio_sel = st.sidebar.multiselect(
        "Municipio",
        sorted(final["Municipio"].unique())
    )

    estado_sel = st.sidebar.multiselect(
        "Estado",
        ["🟢 OK", "🟡 SOBRAN", "🔴 FALTAN"]
    )

    df_filtrado = final.copy()

    if isla_sel:
        df_filtrado = df_filtrado[df_filtrado["Isla"].isin(isla_sel)]

    if municipio_sel:
        df_filtrado = df_filtrado[df_filtrado["Municipio"].isin(municipio_sel)]

    if estado_sel:
        df_filtrado = df_filtrado[df_filtrado["Estado"].isin(estado_sel)]

    # =========================
    # MÉTRICAS
    # =========================
    col1, col2, col3 = st.columns(3)

    col1.metric("Centros", len(df_filtrado))
    col2.metric("FALTAN", (df_filtrado["Estado"] == "🔴 FALTAN").sum())
    col3.metric("SOBRAN", (df_filtrado["Estado"] == "🟡 SOBRAN").sum())

    # =========================
    # TABLA CON COLORES
    # =========================
    st.subheader("📋 Resultado")

    def color_estado(val):
        if "OK" in val:
            return "background-color: #c6f6c6"
        elif "FALTAN" in val:
            return "background-color: #f8c6c6"
        else:
            return "background-color: #fff3b0"

    styled = df_filtrado.style.applymap(color_estado, subset=["Estado"])

    st.dataframe(styled, use_container_width=True)

    # =========================
    # TABLA DE PROBLEMAS
    # =========================
    st.subheader("🚨 Centros con incidencias")

    problemas = df_filtrado[df_filtrado["Estado"] != "🟢 OK"]
    st.dataframe(problemas)

    # =========================
    # DESCARGA EXCEL
    # =========================
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_filtrado.to_excel(writer, sheet_name='General', index=False)
        problemas.to_excel(writer, sheet_name='Incidencias', index=False)

    st.download_button(
        label="📥 Descargar Excel",
        data=buffer.getvalue(),
        file_name="analisis_centros.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
``
