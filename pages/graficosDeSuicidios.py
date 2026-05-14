import os
import re

import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt


st.set_page_config(page_title="Graficos de Suicidios", layout="wide")

st.title("📊 Graficos de Suicidios")
st.markdown("Visualizaciones enfocadas en variables clave del dataset de suicidios.")


@st.cache_data
def load_data(file_path):
	if file_path is None:
		return None

	if not os.path.exists(file_path):
		return None

	file_path_lower = file_path.lower()
	if file_path_lower.endswith(".xlsx") or file_path_lower.endswith(".xls"):
		return pd.read_excel(file_path)

	return pd.read_csv(file_path)


def sort_age_group_labels(labels):
	def sort_key(label):
		match = re.search(r"\d+", label)
		if match:
			return (0, int(match.group(0)), label.lower())
		return (1, label.lower())

	return sorted(labels, key=sort_key)


def normalize_text(value):
	if value is None:
		return ""
	text = str(value).strip().lower()
	text = re.sub(r"\s+", " ", text)
	text = re.sub(r"[^a-z0-9\s]", "", text)
	return text


base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
default_file = os.path.join(
	base_dir,
	"Presuntos_Suicidios._Colombia,_2015_a_2024._Cifras_definitivas_20260319.csv",
)
coords_default_file = os.path.join(base_dir, "co.csv")

with st.sidebar:
	st.header("⚙️ Configuracion")
	st.caption("Fuente fija: archivo del proyecto")

	df = load_data(file_path=default_file)
	if df is None:
		st.warning("No se pudo cargar el archivo. Verifica la ruta del proyecto.")
		st.stop()

	column_options = list(df.columns)
	default_chart_col = "Grupo de Edad judicial"
	if default_chart_col not in column_options:
		default_chart_col = column_options[0]

	def reset_filters():
		st.session_state["filter_col_1"] = "(Sin filtro)"
		st.session_state["filter_values_1"] = []
		st.session_state["filter_col_2"] = "(Sin filtro)"
		st.session_state["filter_values_2"] = []

	column_name = st.selectbox(
		"Columna para grafico de barras",
		options=column_options,
		index=column_options.index(default_chart_col),
		key="chart_col",
		on_change=reset_filters,
	)

	filter_columns = ["(Sin filtro)"] + column_options
	filter_col_1 = st.selectbox(
		"Filtro 1 - Columna",
		options=filter_columns,
		index=0,
		key="filter_col_1",
	)

	filter_values_1 = []
	if filter_col_1 != "(Sin filtro)":
		values_1 = sorted(df[filter_col_1].dropna().astype(str).unique().tolist())
		filter_values_1 = st.multiselect(
			"Filtro 1 - Valores",
			options=values_1,
			key="filter_values_1",
		)

	filter_col_2 = st.selectbox(
		"Filtro 2 - Columna",
		options=filter_columns,
		index=0,
		key="filter_col_2",
	)

	filter_values_2 = []
	if filter_col_2 != "(Sin filtro)":
		values_2 = sorted(df[filter_col_2].dropna().astype(str).unique().tolist())
		filter_values_2 = st.multiselect(
			"Filtro 2 - Valores",
			options=values_2,
			key="filter_values_2",
		)

	coords_file = st.file_uploader(
		"CSV de coordenadas (municipio/departamento)",
		type=["csv"],
	)


df_filtered = df.copy()
if filter_col_1 != "(Sin filtro)" and filter_values_1:
	df_filtered = df_filtered[
		df_filtered[filter_col_1].astype(str).isin(filter_values_1)
	]

if filter_col_2 != "(Sin filtro)" and filter_values_2:
	df_filtered = df_filtered[
		df_filtered[filter_col_2].astype(str).isin(filter_values_2)
	]

col_series = (
	df_filtered[column_name]
	.fillna("Sin dato")
	.astype(str)
	.str.strip()
	.replace("", "Sin dato")
)

counts = col_series.value_counts()
ordered_labels = sort_age_group_labels(counts.index.tolist())
counts = counts.reindex(ordered_labels)

st.subheader("1. Grafico de barras:")
st.markdown(f"Cantidad de registros por {column_name}.")

chart_data = counts.reset_index()
chart_data.columns = [column_name, "Cantidad"]

st.bar_chart(
	chart_data,
	x=column_name,
	y="Cantidad",
	horizontal=False,
)

st.subheader("2. Mapa interactivo")
st.markdown("Distribucion geografica usando las mismas condiciones de filtro.")

dept_col = "Departamento del hecho DANE"
muni_col = "Municipio del hecho DANE"

if dept_col not in df_filtered.columns or muni_col not in df_filtered.columns:
	st.warning("No se encontraron las columnas de municipio/departamento en el dataset.")
	st.stop()

dept_counts = (
	df_filtered[dept_col]
	.fillna("Sin dato")
	.astype(str)
	.str.strip()
)

muni_series = df_filtered[[dept_col, muni_col]].copy()
muni_series[dept_col] = muni_series[dept_col].fillna("Sin dato").astype(str).str.strip()
muni_series[muni_col] = muni_series[muni_col].fillna("Sin dato").astype(str).str.strip()

muni_counts = muni_series.groupby([dept_col, muni_col]).size().reset_index(name="count")

map_rows = []

coords_source = coords_file if coords_file is not None else coords_default_file

if coords_source is not None:
	coords_df = pd.read_csv(coords_source, sep=";", decimal=",", encoding="latin-1")
	coords_columns = list(coords_df.columns)

	default_muni_col = "ciudad"
	default_dept_col = "departamento"
	default_lat_col = "latitud"
	default_lon_col = "longitud"

	muni_coord_col = st.selectbox(
		"Columna de municipio (coordenadas)",
		options=coords_columns,
		index=coords_columns.index(default_muni_col)
		if default_muni_col in coords_columns
		else 0,
	)
	dept_coord_col = st.selectbox(
		"Columna de departamento (coordenadas)",
		options=coords_columns,
		index=coords_columns.index(default_dept_col)
		if default_dept_col in coords_columns
		else 0,
	)
	lat_coord_col = st.selectbox(
		"Columna de latitud (coordenadas)",
		options=coords_columns,
		index=coords_columns.index(default_lat_col)
		if default_lat_col in coords_columns
		else 0,
	)
	lon_coord_col = st.selectbox(
		"Columna de longitud (coordenadas)",
		options=coords_columns,
		index=coords_columns.index(default_lon_col)
		if default_lon_col in coords_columns
		else 0,
	)

	coords_df = coords_df.copy()
	coords_df["_muni_key"] = coords_df[muni_coord_col].apply(normalize_text)
	coords_df["_dept_key"] = coords_df[dept_coord_col].apply(normalize_text)

	muni_counts["_muni_key"] = muni_counts[muni_col].apply(normalize_text)
	muni_counts["_dept_key"] = muni_counts[dept_col].apply(normalize_text)

	merged = muni_counts.merge(
		coords_df,
		on=["_muni_key", "_dept_key"],
		how="left",
	)

	merged[lat_coord_col] = pd.to_numeric(merged[lat_coord_col], errors="coerce")
	merged[lon_coord_col] = pd.to_numeric(merged[lon_coord_col], errors="coerce")
	merged = merged.dropna(subset=[lat_coord_col, lon_coord_col])

	for _, row in merged.iterrows():
		map_rows.append({
			"lat": row[lat_coord_col],
			"lon": row[lon_coord_col],
			"count": int(row["count"]),
			"label": f"{row[muni_col]} ({row[dept_col]})",
		})
else:
	lat_candidates = [col for col in column_options if "lat" in col.lower()]
	lon_candidates = [col for col in column_options if "lon" in col.lower()]
	if lat_candidates and lon_candidates:
		lat_col = st.selectbox(
			"Columna de latitud",
			options=lat_candidates,
			index=0,
		)
		lon_col = st.selectbox(
			"Columna de longitud",
			options=lon_candidates,
			index=0,
		)
		points_df = df_filtered[[lat_col, lon_col]].copy()
		points_df[lat_col] = pd.to_numeric(points_df[lat_col], errors="coerce")
		points_df[lon_col] = pd.to_numeric(points_df[lon_col], errors="coerce")
		points_df = points_df.dropna(subset=[lat_col, lon_col])
		for _, row in points_df.iterrows():
			map_rows.append({
				"lat": row[lat_col],
				"lon": row[lon_col],
				"count": 1,
				"label": "",
			})
	else:
		st.info(
			"Para el mapa necesitas coordenadas. "
			"Sube un CSV con municipio/departamento y latitud/longitud."
		)
		st.stop()

if not map_rows:
	st.warning("No hay datos geograficos para mostrar en el mapa.")
	st.stop()

map_df = pd.DataFrame(map_rows)
st.map(map_df, latitude="lat", longitude="lon", size="count")


st.subheader("3. Grafico de dona:")
st.markdown(f"Proporcion de registros por {column_name}.")

top_n = 10
counts_for_pie = counts.copy()
if len(counts_for_pie) > top_n:
	top = counts_for_pie.iloc[:top_n]
	others = counts_for_pie.iloc[top_n:].sum()
	counts_for_pie = pd.concat([top, pd.Series({"Otros": others})])

def autopct_fmt(pct):
	return f"{pct:.1f}%" if pct >= 2 else ""

fig, ax = plt.subplots(figsize=(7, 7))
wedges, _, _ = ax.pie(
	counts_for_pie,
	labels=None,
	autopct=autopct_fmt,
	startangle=90,
	pctdistance=0.78,
	wedgeprops=dict(width=0.35),
	textprops={"fontsize": 9},
)
ax.axis("equal")
legend_labels = [
	f"{label} ({int(value)})"
	for label, value in counts_for_pie.items()
]
ax.legend(
	wedges,
	legend_labels,
	title=column_name,
	loc="center left",
	bbox_to_anchor=(1.02, 0.5),
	fontsize=9,
	title_fontsize=9,
)
st.pyplot(fig, use_container_width=True)
