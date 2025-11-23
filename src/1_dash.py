import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Dashboard de Obesidade", layout="wide")

# ============================================================
# TÍTULO
# ============================================================
st.title("📊 Análise Exploratória dos Dados de Obesidade")
st.write("Dashboard interativo com filtros para análise personalizada.")

st.sidebar.title("⚙️ Filtros")


# ============================================================
# INPUT DO DATASET
# ============================================================
uploaded = st.sidebar.file_uploader("Envie o arquivo CSV", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
else:
    st.sidebar.info("Usando dataset padrão embutido no script.")
    df = pd.read_csv("Obesity.csv")  # Ajuste se necessário

df = df.rename_axis('ds').sort_index()


# ============================================================
# SIDEBAR — FILTROS DINÂMICOS
# ============================================================

st.sidebar.subheader("Filtros do Dashboard")

# Filtro por gênero
gender_list = df["Gender"].unique()
gender_filter = st.sidebar.multiselect("Gênero", gender_list, default=gender_list)

# Faixa de idade
min_age = int(df["Age"].min())
max_age = int(df["Age"].max())
age_filter = st.sidebar.slider("Faixa de Idade", min_age, max_age, (min_age, max_age))

# Obesidade
if "Obesity" in df.columns:
    obesity_list = df["Obesity"].unique()
    obesity_filter = st.sidebar.multiselect("Nível de Obesidade", obesity_list, default=obesity_list)
else:
    obesity_filter = None

# Histórico familiar
if "family_history" in df.columns:
    family_list = df["family_history"].unique()
    family_filter = st.sidebar.multiselect("Histórico Familiar", family_list, default=family_list)
else:
    family_filter = None

# MTRANS
if "MTRANS" in df.columns:
    mtrans_list = df["MTRANS"].unique()
    mtrans_filter = st.sidebar.multiselect("Transporte", mtrans_list, default=mtrans_list)
else:
    mtrans_filter = None

# Tabagismo
if "SMOKE" in df.columns:
    smoke_list = df["SMOKE"].unique()
    smoke_filter = st.sidebar.multiselect("Fuma?", smoke_list, default=smoke_list)
else:
    smoke_filter = None

# CAEC
if "CAEC" in df.columns:
    caec_list = df["CAEC"].unique()
    caec_filter = st.sidebar.multiselect("Consumo de Snacks (CAEC)", caec_list, default=caec_list)
else:
    caec_filter = None

# SCC
if "SCC" in df.columns:
    scc_list = df["SCC"].unique()
    scc_filter = st.sidebar.multiselect("Nível de Estresse Alimentar (SCC)", scc_list, default=scc_list)
else:
    scc_filter = None


# ============================================================
# APLICAÇÃO DOS FILTROS
# ============================================================
df_filtered = df.copy()

df_filtered = df_filtered[
    (df_filtered["Gender"].isin(gender_filter)) &
    (df_filtered["Age"].between(age_filter[0], age_filter[1]))
]

if obesity_filter is not None:
    df_filtered = df_filtered[df_filtered["Obesity"].isin(obesity_filter)]

if family_filter is not None:
    df_filtered = df_filtered[df_filtered["family_history"].isin(family_filter)]

if mtrans_filter is not None:
    df_filtered = df_filtered[df_filtered["MTRANS"].isin(mtrans_filter)]

if smoke_filter is not None:
    df_filtered = df_filtered[df_filtered["SMOKE"].isin(smoke_filter)]

if caec_filter is not None:
    df_filtered = df_filtered[df_filtered["CAEC"].isin(caec_filter)]

if scc_filter is not None:
    df_filtered = df_filtered[df_filtered["SCC"].isin(scc_filter)]


# ============================================================
# MOSTRA DATAFRAME FILTRADO
# ============================================================
st.subheader("📁 Dataset Filtrado")
st.dataframe(df_filtered.head())


# ============================================================
# VISUALIZAÇÕES
# ============================================================

st.write("---")
st.header("📌 Distribuições Categóricas")

# GENDER
st.subheader("Distribuição por Gênero")
fig = px.histogram(df_filtered, x='Gender')
st.plotly_chart(fig, use_container_width=True)

# GENDER + OBESITY
st.subheader("Gênero x Obesidade")
if "Obesity" in df_filtered.columns:
    fig = px.histogram(
        df_filtered,
        x='Gender',
        color='Obesity',
        text_auto=True,
        barmode='group'
    )
    st.plotly_chart(fig, use_container_width=True)

# family_history + Obesity
st.subheader("Histórico Familiar x Obesidade")
if "family_history" in df_filtered.columns:
    fig = px.histogram(
        df_filtered,
        x='family_history',
        color='Obesity',
        text_auto=True,
        barmode='group'
    )
    st.plotly_chart(fig, use_container_width=True)

# AGE
st.subheader("Distribuição por Idade x Obesidade")
fig = px.histogram(
    df_filtered,
    x="Age",
    color="Obesity",
    text_auto=True,
    barmode='group'
)
st.plotly_chart(fig, use_container_width=True)


# ============================================================
# HÁBITOS
# ============================================================
st.write("---")
st.header("🚶‍♂️ Hábitos e Comportamentos")

for col in ["MTRANS", "CAEC", "SMOKE", "SCC"]:
    if col in df_filtered.columns:
        st.subheader(f"{col} x Obesidade")
        fig = px.histogram(
            df_filtered,
            x="Obesity",
            color=col,
            text_auto=True,
            barmode="group"
        )
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# CORRELAÇÃO
# ============================================================
st.write("---")
st.header("🔢 Matriz de Correlação (Somente Variáveis Numéricas)")

cols_drop = ['FAVC', 'family_history', 'CAEC', 'SMOKE', 'SCC', 'MTRANS',
             'Gender', 'CALC', 'Obesity']

df_correl = df_filtered.drop(columns=[c for c in cols_drop if c in df_filtered.columns], errors='ignore')

df_correl = df_correl.dropna()

if len(df_correl.columns) > 1:
    correlation_matrix = df_correl.corr().round(2)
    fig, ax = plt.subplots(figsize=(8, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", linewidths=.7, ax=ax)
    st.pyplot(fig)
else:
    st.info("Poucas variáveis numéricas disponíveis após aplicar os filtros.")


# Layout do Dash
app.layout = html.Div(
    style={'backgroundColor': 'white', 'minHeight': '100vh', 'padding': '20px'},
    children=[
        html.H1("Meu Dashboard", style={'color': '#111'}),
        dcc.Graph(id='fig1', figure=fig)  # seu objeto fig
    ]
)

st.write("---")
st.subheader("Dataset Completo Filtrado")
st.dataframe(df_filtered)
