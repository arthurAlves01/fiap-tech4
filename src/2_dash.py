import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Dashboard de Saúde - Obesidade", layout="wide")

# ============================================================
# TÍTULO E SUBTÍTULO
# ============================================================
st.title("🏥 Dashboard de Análise de Saúde")
st.markdown("Análise exploratória dos dados de obesidade com insights baseados em dados reais.")

# ============================================================
# SIDEBAR — FILTROS DINÂMICOS
# ============================================================
st.sidebar.title("⚙️ Filtros")

# INPUT DO DATASET
df = pd.read_csv("Obesity.csv")

df = df.rename_axis('ds').sort_index()

# Filtro por gênero
gender_list = df["Gender"].unique()
gender_filter = st.sidebar.multiselect("👥 Gênero", gender_list, default=gender_list)

# Faixa de idade
min_age = int(df["Age"].min())
max_age = int(df["Age"].max())
age_filter = st.sidebar.slider("📅 Faixa de Idade", min_age, max_age, (min_age, max_age))

# Obesidade
if "Obesity" in df.columns:
    obesity_list = df["Obesity"].unique()
    obesity_filter = st.sidebar.multiselect("⚖️ Nível de Obesidade", obesity_list, default=obesity_list)
else:
    obesity_filter = None

# Histórico familiar
if "family_history" in df.columns:
    family_list = df["family_history"].unique()
    family_filter = st.sidebar.multiselect("👨‍👩‍👧 Histórico Familiar", family_list, default=family_list)
else:
    family_filter = None

# MTRANS
if "MTRANS" in df.columns:
    mtrans_list = df["MTRANS"].unique()
    mtrans_filter = st.sidebar.multiselect("🚗 Transporte", mtrans_list, default=mtrans_list)
else:
    mtrans_filter = None

# Tabagismo
if "SMOKE" in df.columns:
    smoke_list = df["SMOKE"].unique()
    smoke_filter = st.sidebar.multiselect("🚭 Fuma?", smoke_list, default=smoke_list)
else:
    smoke_filter = None

# CAEC
if "CAEC" in df.columns:
    caec_list = df["CAEC"].unique()
    caec_filter = st.sidebar.multiselect("🍿 Snacks entre refeições", caec_list, default=caec_list)
else:
    caec_filter = None

# SCC
if "SCC" in df.columns:
    scc_list = df["SCC"].unique()
    scc_filter = st.sidebar.multiselect("📊 Controle de Calorias", scc_list, default=scc_list)
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
# BIG NUMBERS (KPIs)
# ============================================================
st.markdown("---")
st.header("📊 Indicadores Principais (KPIs)")

col1, col2, col3, col4, col5 = st.columns(5)

# Total de registros
total_records = len(df_filtered)
col1.metric("👥 Total de Pessoas", f"{total_records:}")

# Idade média
avg_age = df_filtered["Age"].mean()
col2.metric("📅 Idade Média", f"{avg_age:.1f} anos")

# Peso médio
avg_weight = df_filtered["Weight"].mean()
col3.metric("⚖️ Peso Médio", f"{avg_weight:.1f} kg")

# Altura média
avg_height = df_filtered["Height"].mean()
col4.metric("📏 Altura Média", f"{avg_height:.2f} m")

# Taxa de obesidade
if "Obesity" in df_filtered.columns:
    obesity_cases = len(df_filtered[df_filtered["Obesity"].str.contains("Obesity", case=False, na=False)])
    obesity_rate = (obesity_cases / total_records * 100) if total_records > 0 else 0
    col5.metric("⚠️ Taxa de Obesidade", f"{obesity_rate:.1f}%")

# ============================================================
# STORYTELLING: DISTRIBUIÇÃO DE OBESIDADE
# ============================================================
st.markdown("---")
st.header("1️⃣ Como está a Distribuição de Níveis de Obesidade?")
st.markdown("Entenda a proporção de pessoas em cada categoria de peso.")

# Gráfico horizontal com contagem e porcentagem
if "Obesity" in df_filtered.columns:
    obesity_counts = df_filtered["Obesity"].value_counts().sort_values(ascending=True)
    obesity_counts_df = obesity_counts.reset_index()
    obesity_counts_df.columns = ['Obesity', 'contagem']
    obesity_counts_df['percent'] = 100 * obesity_counts_df['contagem'] / obesity_counts_df['contagem'].sum()
    obesity_counts_df['label'] = obesity_counts_df['contagem'].astype(int).astype(str) + ' (' + obesity_counts_df['percent'].round(1).astype(str) + '%)'
    
    fig_obesity = px.bar(
        obesity_counts_df,
        x='contagem',
        y='Obesity',
        text='label',
        color='contagem',
        color_continuous_scale='Reds',
        orientation='h'
    )
    fig_obesity.update_traces(textposition='outside')
    fig_obesity.update_layout(
        title='Distribuição de Níveis de Obesidade',
        xaxis_title='Quantidade',
        yaxis_title='Nível de Obesidade',
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_obesity, use_container_width=True)

# ============================================================
# STORYTELLING: GÊNERO
# ============================================================
st.markdown("---")
st.header("2️⃣ Qual a Relação entre Gênero e Obesidade?")
st.markdown("Comparação dos níveis de obesidade entre homens e mulheres.")

col1, col2 = st.columns(2)

with col1:
    fig_gender = px.histogram(
        df_filtered,
        x='Gender',
        text_auto=True,
        title='Distribuição por Gênero',
        color='Gender',
        color_discrete_sequence=['#FF6B9D', '#4A90E2']
    )
    fig_gender.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_gender, use_container_width=True)

with col2:
    if "Obesity" in df_filtered.columns:
        fig_gender_obesity = px.histogram(
            df_filtered,
            x='Gender',
            color='Obesity',
            text_auto=True,
            barmode='group',
            title='Gênero x Nível de Obesidade'
        )
        fig_gender_obesity.update_layout(height=400)
        st.plotly_chart(fig_gender_obesity, use_container_width=True)

# ============================================================
# STORYTELLING: IDADE
# ============================================================
st.markdown("---")
st.header("3️⃣ Como a Idade Influencia os Níveis de Obesidade?")
st.markdown("Visualizar a distribuição etária e sua correlação com o peso.")

fig_age = px.histogram(
    df_filtered,
    x="Age",
    color="Obesity",
    text_auto=True,
    barmode='group',
    title='Distribuição de Idade por Nível de Obesidade',
    nbins=15
)
fig_age.update_layout(height=400)
st.plotly_chart(fig_age, use_container_width=True)

# ============================================================
# STORYTELLING: HISTÓRICO FAMILIAR
# ============================================================
st.markdown("---")
st.header("4️⃣ O Histórico Familiar Impacta a Obesidade?")
st.markdown("Analisar se antecedentes familiares correlacionam com níveis de obesidade.")

if "family_history" in df_filtered.columns:
    fig_family = px.histogram(
        df_filtered,
        x='family_history',
        color='Obesity',
        text_auto=True,
        barmode='group',
        title='Histórico Familiar x Nível de Obesidade',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_family.update_layout(height=400)
    st.plotly_chart(fig_family, use_container_width=True)

# ============================================================
# STORYTELLING: HÁBITOS E COMPORTAMENTOS
# ============================================================
st.markdown("---")
st.header("5️⃣ Qual o Impacto dos Hábitos no Nível de Obesidade?")
st.markdown("Explorar fatores de estilo de vida e suas correlações.")

col1, col2 = st.columns(2)

with col1:
    if "MTRANS" in df_filtered.columns:
        fig_mtrans = px.histogram(
            df_filtered,
            x="Obesity",
            color="MTRANS",
            text_auto=True,
            barmode="group",
            title='Tipo de Transporte x Obesidade'
        )
        fig_mtrans.update_layout(height=400)
        st.plotly_chart(fig_mtrans, use_container_width=True)

with col2:
    if "SMOKE" in df_filtered.columns:
        fig_smoke = px.histogram(
            df_filtered,
            x="Obesity",
            color="SMOKE",
            text_auto=True,
            barmode="group",
            title='Tabagismo x Obesidade'
        )
        fig_smoke.update_layout(height=400)
        st.plotly_chart(fig_smoke, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    if "CAEC" in df_filtered.columns:
        fig_caec = px.histogram(
            df_filtered,
            x="Obesity",
            color="CAEC",
            text_auto=True,
            barmode="group",
            title='Consumo de Snacks x Obesidade'
        )
        fig_caec.update_layout(height=400)
        st.plotly_chart(fig_caec, use_container_width=True)

with col2:
    if "SCC" in df_filtered.columns:
        fig_scc = px.histogram(
            df_filtered,
            x="Obesity",
            color="SCC",
            text_auto=True,
            barmode="group",
            title='Controle de Calorias x Obesidade'
        )
        fig_scc.update_layout(height=400)
        st.plotly_chart(fig_scc, use_container_width=True)

# ============================================================
# CORRELAÇÃO ENTRE VARIÁVEIS NUMÉRICAS
# ============================================================
st.markdown("---")
st.header("6️⃣ Correlação Entre Variáveis Numéricas")
st.markdown("Identificar relações entre medidas físicas e comportamentais.")

cols_drop = ['FAVC', 'family_history', 'CAEC', 'SMOKE', 'SCC', 'MTRANS',
             'Gender', 'CALC', 'Obesity']

df_correl = df_filtered.drop(columns=[c for c in cols_drop if c in df_filtered.columns], errors='ignore')
df_correl = df_correl.dropna()

if len(df_correl.columns) > 1:
    correlation_matrix = df_correl.corr().round(2)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", linewidths=0.7, ax=ax, fmt='.2f')
    st.pyplot(fig)
else:
    st.info("Poucas variáveis numéricas disponíveis após aplicar os filtros.")

# ============================================================
# DADOS COMPLETOS
# ============================================================
st.markdown("---")
st.header("📋 Dados Completos Filtrados")

with st.expander("Clique para expandir e visualizar a tabela completa"):
    st.dataframe(df_filtered, use_container_width=True)

st.markdown("---")
st.markdown("*Dashboard interativo criado com Streamlit e Plotly*")
