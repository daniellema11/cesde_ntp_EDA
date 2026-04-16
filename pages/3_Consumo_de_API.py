import streamlit as st
import pandas as pd
import requests

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

# --- Información Técnica ---
st.info(f"""
**Detalles de la API (MockAPI):**
- **Base URL:** `{MOCK_API_BASE_URL}`
- **Entidades:** `/horarioAdmin` y `/horarioProfesor`
- **Horario Admin:** Información de horarios con sedes CESDE, aulas y profesores.
- **Horario Profesor:** Información de horarios con institutos y estado activo/inactivo.
""")

