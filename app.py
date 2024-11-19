import os
import pandas as pd
import plotly.express as px
import streamlit as st

FULL_PATH = os.path.dirname(os.path.abspath(__file__)) + os.sep + "titles.csv"

# Configuración de la página
st.set_page_config(
    page_title="Tablero de Producciones",
    page_icon=":clapper:",
    layout="wide"
)

# ---- LEER ARCHIVO CSV ----
@st.cache_data
def get_data_from_csv():
    df = pd.read_csv(FULL_PATH) 
    # Aplicar filtros iniciales para filtrar países específicos en 'production_countries'
    df["genres"] = df["genres"].astype(str)
    df_filtered = df[
        df["production_countries"].isin(["['US']", "['GB']", "['FR']", "['CA']", "['ZA']", "['AU']"])
    ]
    # Filtrar 'genre' con longitud entre 3 y 12 caracteres
    df_filtered = df_filtered[
        df_filtered["genres"].apply(lambda x: 3 <= len(x) <= 12)
    ]
    return df_filtered

df = get_data_from_csv()

# ---- BARRA LATERAL ----
st.sidebar.header("Por favor, filtre aquí:")
production_countries = st.sidebar.multiselect(
    "Seleccione los Países de Producción:",
    options=df["production_countries"].unique(),
    default=df["production_countries"].unique(),
)

type_ = st.sidebar.multiselect(
    "Seleccione el Tipo de Producción:",
    options=df["type"].unique(),
    default=df["type"].unique(),
)

genres = st.sidebar.multiselect(
    "Seleccione el Género:",
    options=df["genres"].unique(),
    default=df["genres"].unique(),
)

df_seleccion = df.query(
    "production_countries == @production_countries & type == @type_ & genres == @genres"
)

# ---- PÁGINA PRINCIPAL ----
st.title(":clapper: Tablero de Producciones")
st.markdown("##")

# KPI PRINCIPALES
total_producciones = df_seleccion.shape[0]
puntuacion_media = round(df_seleccion["imdb_score"].mean(), 2)
producciones_por_year = len(df_seleccion["release_year"].unique())

columna_izquierda, columna_media, columna_derecha = st.columns(3)
with columna_izquierda:
    st.subheader("Total de Producciones:")
    st.subheader(f"{total_producciones:,}")
with columna_media:
    st.subheader("Puntuación IMDb Media:")
    st.subheader(f"{puntuacion_media}")
with columna_derecha:
    st.subheader("Años con Producciones:")
    st.subheader(f"{producciones_por_year}")

st.markdown("---")

# PRODUCCIONES POR PUNTUACIÓN IMDb [GRÁFICO DE BARRAS]
producciones_por_puntuacion = (
    df_seleccion.groupby(by=["imdb_score"]).size().reset_index(name="count")
)
fig_puntuacion = px.bar(
    producciones_por_puntuacion,
    x="imdb_score",
    y="count",
    title="<b>Producciones por Puntuación IMDb</b>",
    color_discrete_sequence=["#0083B8"] * len(producciones_por_puntuacion),
    template="plotly_white",
)
fig_puntuacion.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False))
)

# PRODUCCIONES POR AÑO [GRÁFICO DE BARRAS]
producciones_por_año = (
    df_seleccion.groupby(by=["release_year"]).size().reset_index(name="count")
)
fig_año = px.bar(
    producciones_por_año,
    x="release_year",
    y="count",
    title="<b>Producciones por Año</b>",
    color_discrete_sequence=["#0083B8"] * len(producciones_por_año),
    template="plotly_white",
)
fig_año.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

columna_izquierda, columna_derecha = st.columns(2)
columna_izquierda.plotly_chart(fig_puntuacion, use_container_width=True)
columna_derecha.plotly_chart(fig_año, use_container_width=True)

# ---- OCULTAR ESTILO STREAMLIT ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)