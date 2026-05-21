# Proyecto Integrador - Analitica de Datos con Streamlit

Aplicacion de analitica con Streamlit para EDA, resultados y consumo de API, usando datasets locales.

## Requisitos
- Python 3.10+ (recomendado)
- Entorno virtual (.venv)

## Instalacion
```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\Activate.ps1
```

Mac/Linux:
```bash
source .venv/bin/activate
```

Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Ejecucion
```bash
streamlit run Inicio.py
```

## Estructura
```text
.
├── Inicio.py
├── pages/
│   ├── 1_Analisis Exploratorio de Datos (EDA).py
│   ├── 2_Resultados (EDA).py
│   ├── 3_Consumo_de_API.py
│   └── graficosDeSuicidios.py
├── co.csv
├── Presuntos_Suicidios._Colombia,_2015_a_2024._Cifras_definitivas_20260319.csv
├── requirements.txt
└── .gitignore
```

## Paginas
- Inicio: portada del proyecto, objetivos y equipo.
- Analisis Exploratorio (EDA): carga CSV, vista previa, tipos, nulos y estadisticas.
- Resultados (EDA): formulario para conclusiones y descarga de reporte en Markdown.
- Consumo de API: consulta MockAPI con filtros y graficos.
- Graficos de Suicidios: graficos y mapa con filtros y coordenadas.

## Notas
- El dataset principal se carga desde el archivo local de suicidios.
- El mapa puede usar co.csv (coordenadas) o un CSV cargado por el usuario.
- El consumo de API usa MockAPI; valida que las entidades existan.
