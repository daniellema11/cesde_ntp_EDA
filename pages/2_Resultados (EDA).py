import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Plantilla de Resultados - Proyecto Analítica",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Plantilla de Entrega: Resultados del EDA")
st.markdown("""
### Instrucciones
Utiliza esta página para documentar tus hallazgos. Completa cada sección basándote en lo que descubriste en la pestaña de **Análisis Exploratorio**.
Al finalizar, puedes previsualizar tu reporte consolidado.
""")

st.divider()

# --- Formulario de Resultados ---
with st.container():
    st.header("🔍 1. Identificación y Contexto")
    contexto = st.text_area(
        "¿De qué se trata el dataset? (Deducción del origen, tema y propósito)",
        placeholder="Nuestra dataset se trata de los suicidios en colombia entre los años 2015-2025, el proposito es permitir el analisis de  este suceso, identificando patrones como el sexo, dia, la ciudad, manera de suicidio  y motivo del suceso, etc.",
        height=150
    )

    st.header("❗ 2. Calidad de los Datos")
    calidad = st.text_area(
        "¿Qué encontraste sobre los datos faltantes y la limpieza?",
        placeholder="Los datos tienen un gran integridad, ya que cumple con todos los campos, por ello no debemos hacer limpieza.",
        height=150
    )

    st.header("📈 3. Hallazgos Estadísticos Key")
    estadisticas = st.text_area(
        "Interpretación de los números y categorías principales (Medias, modas, etc.)",
        placeholder="A partir del análisis del dataset, se identifican varios patrones relevantes. En cuanto a la edad, el grupo con mayor número de casos corresponde a personas entre 20 y 24 años, el genero mayoritario es masculino (hombres), la mayoria no termino la educacion primaria, el mes con mas sucesos es AGOSTO y el dia es el DOMINGO, el municipio mas impactado es bogota y segundo medellin, y el mecanismo causal general es (generadores de asfixia), el motivo del suceso es de conflictos con la pareja, entre otras cosas ",
        height=150
    )

    st.header("💡 4. Conclusión Final")
    conclusion = st.text_area(
        "¿Cuál es el mensaje principal que nos dan estos datos?",
        placeholder="En conclusion, el dataset permite evidenciar que el suicidio es un fenómeno que presenta patrones claros según variables como la edad, el sexo y el motivo del suceso. Los datos muestran que no se distribuye de manera uniforme, sino que afecta más a ciertos grupos poblacionales. Esto resalta la importancia de analizar este tipo de información para apoyar la toma de decisiones y el diseño de estrategias de prevención más enfocadas.",
        height=100
    )

st.divider()

# --- Generación de Reporte ---
if st.button("🚀 Generar Previsualización del Reporte"):
    if contexto and calidad and estadisticas and conclusion:
        st.success("✅ Reporte Generado Exitosamente")
        
        reporte_md = f"""
        # Reporte de Análisis Exploratorio de Datos
        
        ## 1. Identificación y Contexto
        {contexto}
        
        ## 2. Calidad de los Datos
        {calidad}
        
        ## 3. Hallazgos Estadísticos Clave
        {estadisticas}
        
        ## 4. Conclusión Final
        {conclusion}
        
        ---
        *Generado por el módulo de Reportes - Proyecto Integrador*
        """
        
        st.markdown(reporte_md)
        st.download_button(
            label="📥 Descargar Reporte (.md)",
            data=reporte_md,
            file_name="reporte_eda_estudiante.md",
            mime="text/markdown"
        )
    else:
        st.warning("⚠️ Por favor, completa todas las secciones antes de generar el reporte.")

# --- Barra Lateral ---
st.sidebar.info("Esta es tu hoja de trabajo. Asegúrate de analizar bien los datos antes de escribir tus conclusiones.")
st.sidebar.markdown("---")
st.sidebar.write("© 2026 - Plantilla de Resultados")
