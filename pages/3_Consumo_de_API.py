import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Sistema de Horarios CESDE - MockAPI", layout="wide")

st.title("📅 Sistema de Gestión de Horarios Académicos")
st.markdown("""
### Objetivo
En esta sección, consumiremos **dos entidades** personalizadas creadas en **MockAPI** que simulan datos del sistema de horarios académicos.
- **Horarios Administrativos:** Horarios gestionados por la administración con información de sedes y aulas.
- **Horarios de Profesores:** Horarios asignados a profesores con información de institutos.
""")

# --- Configuración de la API (MockAPI) ---
MOCK_API_ID = "69d7ac5b9c5ebb0918c8298c" 
MOCK_API_BASE_URL = f"https://{MOCK_API_ID}.mockapi.io"

# --- Botón para Limpiar Caché ---
if st.button("🔄 Refrescar Datos (Limpiar Caché)"):
    st.cache_data.clear()
    st.rerun()

# --- Función para obtener datos de MockAPI ---
@st.cache_data
def get_mockapi_data(entity):
    paths_to_try = [f"{MOCK_API_BASE_URL}/{entity}", f"{MOCK_API_BASE_URL}/api/v1/{entity}"]
    
    last_error = ""
    for url in paths_to_try:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return pd.DataFrame(data)
                else:
                    return pd.DataFrame([data])
            else:
                last_error = f"Status {response.status_code} en {url}"
        except Exception as e:
            last_error = f"Error: {e} en {url}"
            
    st.error(f"No se pudo conectar con '{entity}'. Último intento: {last_error}")
    return pd.DataFrame()

# --- Carga de Datos ---
with st.spinner("Conectando con MockAPI..."):
    df_horarioAdmin = get_mockapi_data("horarioAdmin")
    df_horarioProfesor = get_mockapi_data("horarioProfesor")

# --- Sección 1: Horarios Administrativos (Entidad 1) ---
st.header("🏫 Horarios Administrativos - CESDE")
st.markdown("Consulta y filtra los horarios gestionados por la administración con información de sedes y aulas.")

if not df_horarioAdmin.empty:
    # Filtros para Horarios Administrativos
    col_a_1, col_a_2, col_a_3 = st.columns(3)
    
    with col_a_1:
        materias_admin = ["Todas"] + sorted(df_horarioAdmin['materia'].unique().tolist()) if 'materia' in df_horarioAdmin.columns else ["Todas"]
        sel_materia_admin = st.selectbox("Filtrar por Materia:", materias_admin, key="sel_materia_admin")
    
    with col_a_2:
        sedes_admin = ["Todas"] + sorted(df_horarioAdmin['sede'].unique().tolist()) if 'sede' in df_horarioAdmin.columns else ["Todas"]
        sel_sede_admin = st.selectbox("Filtrar por Sede:", sedes_admin, key="sel_sede_admin")
    
    with col_a_3:
        dias_admin = ["Todos"] + sorted(df_horarioAdmin['recurrenciaDiaAdmin'].unique().tolist()) if 'recurrenciaDiaAdmin' in df_horarioAdmin.columns else ["Todos"]
        sel_dia_admin = st.selectbox("Filtrar por Día:", dias_admin, key="sel_dia_admin")

    # Filtro adicional por profesor
    col_a_4, col_a_5 = st.columns(2)
    with col_a_4:
        profesores_admin = ["Todos"] + sorted(df_horarioAdmin['nombreProfesor'].unique().tolist()) if 'nombreProfesor' in df_horarioAdmin.columns else ["Todos"]
        sel_profesor_admin = st.selectbox("Filtrar por Profesor:", profesores_admin, key="sel_profesor_admin")
    
    with col_a_5:
        search_id_admin = st.text_input("Buscar por Identificación:", "", key="search_id_admin")

    # Aplicación de filtros
    f_horarioAdmin = df_horarioAdmin.copy()
    if sel_materia_admin != "Todas":
        f_horarioAdmin = f_horarioAdmin[f_horarioAdmin['materia'] == sel_materia_admin]
    if sel_sede_admin != "Todas":
        f_horarioAdmin = f_horarioAdmin[f_horarioAdmin['sede'] == sel_sede_admin]
    if sel_dia_admin != "Todos":
        f_horarioAdmin = f_horarioAdmin[f_horarioAdmin['recurrenciaDiaAdmin'] == sel_dia_admin]
    if sel_profesor_admin != "Todos":
        f_horarioAdmin = f_horarioAdmin[f_horarioAdmin['nombreProfesor'] == sel_profesor_admin]
    if search_id_admin:
        f_horarioAdmin = f_horarioAdmin[f_horarioAdmin['identificacionPersona'].astype(str).str.contains(search_id_admin, case=False)]

    # Métricas de Horarios Administrativos
    ma1, ma2, ma3, ma4 = st.columns(4)
    with ma1:
        st.metric("📋 Total Horarios", len(f_horarioAdmin))
    with ma2:
        profesores_unicos = f_horarioAdmin['nombreProfesor'].nunique() if 'nombreProfesor' in f_horarioAdmin.columns else 0
        st.metric("👨‍🏫 Profesores Únicos", profesores_unicos)
    with ma3:
        materias_unicas = f_horarioAdmin['materia'].nunique() if 'materia' in f_horarioAdmin.columns else 0
        st.metric("📚 Materias Únicas", materias_unicas)
    with ma4:
        sedes_unicas = f_horarioAdmin['sede'].nunique() if 'sede' in f_horarioAdmin.columns else 0
        st.metric("🏢 Sedes", sedes_unicas)

    st.dataframe(f_horarioAdmin, use_container_width=True)
    
    # Gráficos para Horarios Admin
    with st.expander("📊 Ver Estadísticas de Horarios Administrativos"):
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            if 'sede' in f_horarioAdmin.columns:
                st.subheader("Horarios por Sede")
                sede_counts = f_horarioAdmin['sede'].value_counts()
                st.bar_chart(sede_counts)
        with col_chart2:
            if 'recurrenciaDiaAdmin' in f_horarioAdmin.columns:
                st.subheader("Horarios por Día")
                dia_counts = f_horarioAdmin['recurrenciaDiaAdmin'].value_counts()
                st.bar_chart(dia_counts)
        
        # Gráfica de líneas: Tendencia de cantidad por día
        if 'recurrenciaDiaAdmin' in f_horarioAdmin.columns:
            st.subheader("Tendencia de Horarios por Día")
            dia_counts_line = f_horarioAdmin['recurrenciaDiaAdmin'].value_counts().reset_index()
            dia_counts_line.columns = ['Día', 'Cantidad']
            st.line_chart(dia_counts_line, x='Día', y='Cantidad')
else:
    st.info("💡 Esperando datos de 'horarioAdmin'... Verifica que la entidad exista en MockAPI.")

st.divider()

# --- Sección 2: Horarios de Profesores (Entidad 2) ---
st.header("👨‍🏫 Horarios de Profesores")
st.markdown("Consulta y filtra los horarios asignados a profesores con información de institutos.")

if not df_horarioProfesor.empty:
    # Filtros para Horarios de Profesores
    col_p_1, col_p_2, col_p_3 = st.columns(3)
    
    with col_p_1:
        materias_prof = ["Todas"] + sorted(df_horarioProfesor['materiaProfesor'].unique().tolist()) if 'materiaProfesor' in df_horarioProfesor.columns else ["Todas"]
        sel_materia_prof = st.selectbox("Filtrar por Materia:", materias_prof, key="sel_materia_prof")
    
    with col_p_2:
        institutos = ["Todos"] + sorted(df_horarioProfesor['instituto'].unique().tolist()) if 'instituto' in df_horarioProfesor.columns else ["Todos"]
        sel_instituto = st.selectbox("Filtrar por Instituto:", institutos, key="sel_instituto")
    
    with col_p_3:
        dias_prof = ["Todos"] + sorted(df_horarioProfesor['recurrenciaDiaProfes'].unique().tolist()) if 'recurrenciaDiaProfes' in df_horarioProfesor.columns else ["Todos"]
        sel_dia_prof = st.selectbox("Filtrar por Día:", dias_prof, key="sel_dia_prof")

    # Filtro adicional por estado activo
    col_p_4, col_p_5 = st.columns(2)
    with col_p_4:
        estados = ["Todos", "Activos", "Inactivos"]
        sel_estado = st.selectbox("Filtrar por Estado:", estados, key="sel_estado")
    
    with col_p_5:
        search_id_prof = st.text_input("Buscar por Identificación:", "", key="search_id_prof")

    # Aplicación de filtros
    f_horarioProfesor = df_horarioProfesor.copy()
    if sel_materia_prof != "Todas":
        f_horarioProfesor = f_horarioProfesor[f_horarioProfesor['materiaProfesor'] == sel_materia_prof]
    if sel_instituto != "Todos":
        f_horarioProfesor = f_horarioProfesor[f_horarioProfesor['instituto'] == sel_instituto]
    if sel_dia_prof != "Todos":
        f_horarioProfesor = f_horarioProfesor[f_horarioProfesor['recurrenciaDiaProfes'] == sel_dia_prof]
    if sel_estado == "Activos" and 'activo' in f_horarioProfesor.columns:
        f_horarioProfesor = f_horarioProfesor[f_horarioProfesor['activo'] == True]
    elif sel_estado == "Inactivos" and 'activo' in f_horarioProfesor.columns:
        f_horarioProfesor = f_horarioProfesor[f_horarioProfesor['activo'] == False]
    if search_id_prof:
        f_horarioProfesor = f_horarioProfesor[f_horarioProfesor['identificacionPersona'].astype(str).str.contains(search_id_prof, case=False)]

    # Métricas de Horarios de Profesores
    mp1, mp2, mp3, mp4 = st.columns(4)
    with mp1:
        st.metric("📋 Total Horarios", len(f_horarioProfesor))
    with mp2:
        materias_prof_unicas = f_horarioProfesor['materiaProfesor'].nunique() if 'materiaProfesor' in f_horarioProfesor.columns else 0
        st.metric("📚 Materias Únicas", materias_prof_unicas)
    with mp3:
        institutos_unicos = f_horarioProfesor['instituto'].nunique() if 'instituto' in f_horarioProfesor.columns else 0
        st.metric("🏛️ Institutos", institutos_unicos)
    with mp4:
        if 'activo' in f_horarioProfesor.columns:
            activos = f_horarioProfesor['activo'].sum()
            st.metric("✅ Horarios Activos", activos)
        else:
            st.metric("✅ Horarios Activos", "N/A")

    st.dataframe(f_horarioProfesor, use_container_width=True)
    
    # Gráficos para Horarios Profesor
    with st.expander("📊 Ver Estadísticas de Horarios de Profesores"):
        col_chart3, col_chart4 = st.columns(2)
        with col_chart3:
            if 'instituto' in f_horarioProfesor.columns:
                st.subheader("Horarios por Instituto")
                instituto_counts = f_horarioProfesor['instituto'].value_counts()
                st.bar_chart(instituto_counts)
        with col_chart4:
            if 'recurrenciaDiaProfes' in f_horarioProfesor.columns:
                st.subheader("Horarios por Día")
                dia_prof_counts = f_horarioProfesor['recurrenciaDiaProfes'].value_counts()
                st.bar_chart(dia_prof_counts)
        
        # Gráfica de líneas: Tendencia de cantidad por día
        if 'recurrenciaDiaProfes' in f_horarioProfesor.columns:
            st.subheader("Tendencia de Horarios por Día")
            dia_prof_counts_line = f_horarioProfesor['recurrenciaDiaProfes'].value_counts().reset_index()
            dia_prof_counts_line.columns = ['Día', 'Cantidad']
            st.line_chart(dia_prof_counts_line, x='Día', y='Cantidad')
        
        # Gráfico de estado activo/inactivo
        if 'activo' in df_horarioProfesor.columns:
            st.subheader("Estado de Horarios")
            estado_counts = df_horarioProfesor['activo'].value_counts()
            estado_labels = estado_counts.rename(index={True: 'Activos', False: 'Inactivos'})
            st.bar_chart(estado_labels)
else:
    st.info("💡 Esperando datos de 'horarioProfesor'... Verifica que la entidad exista en MockAPI.")

st.divider()

# --- Sección 3: Comparativa de Datos ---
st.header("📈 Comparativa General")

if not df_horarioAdmin.empty and not df_horarioProfesor.empty:
    col_comp1, col_comp2 = st.columns(2)
    
    with col_comp1:
        st.subheader("Resumen Horarios Admin")
        st.write(f"- **Total de registros:** {len(df_horarioAdmin)}")
        if 'nombreProfesor' in df_horarioAdmin.columns:
            st.write(f"- **Profesores únicos:** {df_horarioAdmin['nombreProfesor'].nunique()}")
        if 'sede' in df_horarioAdmin.columns:
            st.write(f"- **Sedes CESDE:** {df_horarioAdmin['sede'].nunique()}")
        if 'materia' in df_horarioAdmin.columns:
            st.write(f"- **Materias disponibles:** {df_horarioAdmin['materia'].nunique()}")
    
    with col_comp2:
        st.subheader("Resumen Horarios Profesor")
        st.write(f"- **Total de registros:** {len(df_horarioProfesor)}")
        if 'instituto' in df_horarioProfesor.columns:
            st.write(f"- **Institutos:** {df_horarioProfesor['instituto'].nunique()}")
        if 'materiaProfesor' in df_horarioProfesor.columns:
            st.write(f"- **Materias disponibles:** {df_horarioProfesor['materiaProfesor'].nunique()}")
        if 'activo' in df_horarioProfesor.columns:
            activos_total = df_horarioProfesor['activo'].sum()
            inactivos_total = len(df_horarioProfesor) - activos_total
            st.write(f"- **Activos:** {activos_total} | **Inactivos:** {inactivos_total}")
else:
    st.info("Se necesitan datos de ambas entidades para mostrar la comparativa.")

st.divider()

# --- Sección 4: Graficos interactivos ---
st.header("📊 Graficos interactivos")
st.markdown("Filtros solo para los graficos (independientes de las tablas).")

data_options = ["Horarios Administrativos", "Horarios de Profesores"]
data_choice = st.selectbox("Fuente de datos", data_options, key="chart_data_source")

df_chart_base = df_horarioAdmin if data_choice == "Horarios Administrativos" else df_horarioProfesor

if df_chart_base.empty:
    st.info("No hay datos disponibles para graficar.")
else:
    chart_columns = list(df_chart_base.columns)
    default_chart_col = chart_columns[0]

    chart_col = st.selectbox(
        "Columna para grafico de barras",
        options=chart_columns,
        index=chart_columns.index(default_chart_col),
        key="chart_col",
    )

    filter_columns = ["(Sin filtro)"] + chart_columns
    filter_col_1 = st.selectbox(
        "Filtro 1 - Columna",
        options=filter_columns,
        index=0,
        key="chart_filter_col_1",
    )

    filter_values_1 = []
    if filter_col_1 != "(Sin filtro)":
        values_1 = sorted(df_chart_base[filter_col_1].dropna().astype(str).unique().tolist())
        filter_values_1 = st.multiselect(
            "Filtro 1 - Valores",
            options=values_1,
            key="chart_filter_values_1",
        )

    filter_col_2 = st.selectbox(
        "Filtro 2 - Columna",
        options=filter_columns,
        index=0,
        key="chart_filter_col_2",
    )

    filter_values_2 = []
    if filter_col_2 != "(Sin filtro)":
        values_2 = sorted(df_chart_base[filter_col_2].dropna().astype(str).unique().tolist())
        filter_values_2 = st.multiselect(
            "Filtro 2 - Valores",
            options=values_2,
            key="chart_filter_values_2",
        )

    df_chart = df_chart_base.copy()
    if filter_col_1 != "(Sin filtro)" and filter_values_1:
        df_chart = df_chart[df_chart[filter_col_1].astype(str).isin(filter_values_1)]
    if filter_col_2 != "(Sin filtro)" and filter_values_2:
        df_chart = df_chart[df_chart[filter_col_2].astype(str).isin(filter_values_2)]

    series = (
        df_chart[chart_col]
        .fillna("Sin dato")
        .astype(str)
        .str.strip()
        .replace("", "Sin dato")
    )

    counts = series.value_counts()
    chart_data = counts.reset_index()
    chart_data.columns = [chart_col, "Cantidad"]

    st.subheader("Grafico de barras")
    st.bar_chart(chart_data, x=chart_col, y="Cantidad")

    if not df_chart.empty:
        st.subheader("Gráfico de líneas")
        line_data = chart_data.copy()
        st.line_chart(line_data, x=chart_col, y="Cantidad")

        st.subheader("Gráfico tipo Dona")
        legend_labels = [
            f"{label} ({count})"
            for label, count in zip(chart_data[chart_col], chart_data["Cantidad"])
        ]
        fig = go.Figure(data=[go.Pie(
            labels=legend_labels,
            values=chart_data["Cantidad"],
            hole=0.3,
            hovertemplate="<b>%{label}</b><br>Cantidad: %{value}<extra></extra>"
        )])
        fig.update_layout(
            title="Distribución de datos",
            height=500,
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos para el gráfico de líneas con los filtros actuales.")

# --- Información Técnica ---
st.info(f"""
**Detalles de la API (MockAPI):**
- **Base URL:** `{MOCK_API_BASE_URL}`
- **Entidades:** `/horarioAdmin` y `/horarioProfesor`
- **Horario Admin:** Información de horarios con sedes CESDE, aulas y profesores.
- **Horario Profesor:** Información de horarios con institutos y estado activo/inactivo.
""")