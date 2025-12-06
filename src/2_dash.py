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

# Dicionário de renomeação para português
column_name = {
    'Gender': 'sexo',
    'Age': 'idade',
    'Height': 'altura',
    'Weight': 'peso',
    'family_history': 'hist_familiar_obes',
    'FAVC': 'cons_altas_cal_freq',
    'FCVC': 'cons_verduras',
    'NCP': 'refeicoes_principais_dia',
    'CAEC': 'lancha_entre_ref',
    'SMOKE': 'fuma',
    'CH2O': 'agua_dia',
    'SCC': 'controle_calorias',
    'FAF': 'ativ_fisica',
    'TUE': 'uso_tecnologia',
    'CALC': 'cons_alcool',
    'MTRANS': 'transporte',
    'Obesity': 'nivel_obesidade'
}

df = df.rename(columns=column_name).copy()

# Mapeamento dos valores para português
value_mapping = {
    'sexo': {'Male': 'Masculino', 'Female': 'Feminino'},
    'hist_familiar_obes': {'yes': 'Sim', 'no': 'Não'},
    'cons_altas_cal_freq': {'yes': 'Sim', 'no': 'Não'},
    'cons_verduras': {'yes': 'Sim', 'no': 'Não'},
    'lancha_entre_ref': {'frequently': 'Frequentemente', 'sometimes': 'Às vezes', 'always': 'Sempre', 'no': 'Nunca'},
    'fuma': {'yes': 'Sim', 'no': 'Não'},
    'controle_calorias': {'yes': 'Sim', 'no': 'Não'},
    'cons_alcool': {'never': 'Nunca', 'always': 'Sempre', 'frequently': 'Frequentemente', 'sometimes': 'Às vezes'},
    'transporte': {
        'Public_Transportation': 'Transporte Público',
        'Automobile': 'Automóvel',
        'Bike': 'Bicicleta',
        'Walking': 'A pé'
    },
    'nivel_obesidade': {
        'Insufficient_Weight': 'Peso Insuficiente',
        'Normal_Weight': 'Peso Normal',
        'Overweight_Level_I': 'Sobrepeso Nível I',
        'Overweight_Level_II': 'Sobrepeso Nível II',
        'Obesity_Type_I': 'Obesidade Tipo I',
        'Obesity_Type_II': 'Obesidade Tipo II',
        'Obesity_Type_III': 'Obesidade Tipo III'
    }
}

# Aplicar mapeamento
for coluna, mapa in value_mapping.items():
    if coluna in df.columns:
        df[coluna] = df[coluna].replace(mapa)

df = df.rename_axis('ds').sort_index()

# Filtro por gênero
sexo_list = df["sexo"].unique()
sexo_filter = st.sidebar.multiselect("👥 Gênero", sexo_list, default=sexo_list)

# Faixa de idade
min_idade = int(df["idade"].min())
max_idade = int(df["idade"].max())
idade_filter = st.sidebar.slider("📅 Faixa de Idade", min_idade, max_idade, (min_idade, max_idade))

# Nível de Obesidade
if "nivel_obesidade" in df.columns:
    obesidade_list = df["nivel_obesidade"].unique()
    obesidade_filter = st.sidebar.multiselect("⚖️ Nível de Obesidade", obesidade_list, default=obesidade_list)
else:
    obesidade_filter = None

# Histórico familiar
if "hist_familiar_obes" in df.columns:
    familia_list = df["hist_familiar_obes"].unique()
    familia_filter = st.sidebar.multiselect("👨‍👩‍👧 Histórico Familiar", familia_list, default=familia_list)
else:
    familia_filter = None

# Transporte
if "transporte" in df.columns:
    transporte_list = df["transporte"].unique()
    transporte_filter = st.sidebar.multiselect("🚗 Transporte", transporte_list, default=transporte_list)
else:
    transporte_filter = None

# Tabagismo
if "fuma" in df.columns:
    fuma_list = df["fuma"].unique()
    fuma_filter = st.sidebar.multiselect("🚭 Fuma?", fuma_list, default=fuma_list)
else:
    fuma_filter = None

# Snacks entre refeições
if "lancha_entre_ref" in df.columns:
    lancha_list = df["lancha_entre_ref"].unique()
    lancha_filter = st.sidebar.multiselect("🍿 Snacks entre refeições", lancha_list, default=lancha_list)
else:
    lancha_filter = None

# Controle de Calorias
if "controle_calorias" in df.columns:
    controle_list = df["controle_calorias"].unique()
    controle_filter = st.sidebar.multiselect("📊 Controle de Calorias", controle_list, default=controle_list)
else:
    controle_filter = None

# ============================================================
# APLICAÇÃO DOS FILTROS
# ============================================================
df_filtrado = df.copy()

df_filtrado = df_filtrado[
    (df_filtrado["sexo"].isin(sexo_filter)) &
    (df_filtrado["idade"].between(idade_filter[0], idade_filter[1]))
]

if obesidade_filter is not None:
    df_filtrado = df_filtrado[df_filtrado["nivel_obesidade"].isin(obesidade_filter)]

if familia_filter is not None:
    df_filtrado = df_filtrado[df_filtrado["hist_familiar_obes"].isin(familia_filter)]

if transporte_filter is not None:
    df_filtrado = df_filtrado[df_filtrado["transporte"].isin(transporte_filter)]

if fuma_filter is not None:
    df_filtrado = df_filtrado[df_filtrado["fuma"].isin(fuma_filter)]

if lancha_filter is not None:
    df_filtrado = df_filtrado[df_filtrado["lancha_entre_ref"].isin(lancha_filter)]

if controle_filter is not None:
    df_filtrado = df_filtrado[df_filtrado["controle_calorias"].isin(controle_filter)]

# ============================================================
# BIG NUMBERS (KPIs)
# ============================================================
st.markdown("---")
st.header("📊 Indicadores Principais (KPIs)")

col1, col2, col3, col4, col5 = st.columns(5)

# Total de registros
total_registros = len(df_filtrado)
col1.metric("👥 Total de Pessoas", f"{total_registros:,}")

# Idade média
idade_media = df_filtrado["idade"].mean()
col2.metric("📅 Idade Média", f"{idade_media:.1f} anos")

# Peso médio
peso_medio = df_filtrado["peso"].mean()
col3.metric("⚖️ Peso Médio", f"{peso_medio:.1f} kg")

# Altura média
altura_media = df_filtrado["altura"].mean()
col4.metric("📏 Altura Média", f"{altura_media:.2f} m")

# Taxa de obesidade
# Cálculo: Conta registros com "Obesidade" (Tipo I, II, III) e divide pelo total
# Fórmula: (Quantidade de pessoas com Obesidade / Total de pessoas) * 100
if "nivel_obesidade" in df_filtrado.columns:
    casos_obesidade = len(df_filtrado[df_filtrado["nivel_obesidade"].str.contains("Obesidade", case=False, na=False)])
    taxa_obesidade = (casos_obesidade / total_registros * 100) if total_registros > 0 else 0
    col5.metric("⚠️ Taxa de Obesidade", f"{taxa_obesidade:.1f}%", 
                help="Percentual de pessoas com Obesidade Tipo I, II ou III em relação ao total")

# ============================================================
# STORYTELLING: DISTRIBUIÇÃO DE OBESIDADE
# ============================================================
st.markdown("---")
st.header("1️⃣ Como está a Distribuição de Níveis de Obesidade?")
st.markdown("Entenda a proporção de pessoas em cada categoria de peso.")

# Gráfico horizontal com contagem e porcentagem
if "nivel_obesidade" in df_filtrado.columns:
    contagem_obesidade = df_filtrado["nivel_obesidade"].value_counts().sort_values(ascending=True)
    df_obesidade = contagem_obesidade.reset_index()
    df_obesidade.columns = ['nivel_obesidade', 'contagem']
    df_obesidade['percentual'] = 100 * df_obesidade['contagem'] / df_obesidade['contagem'].sum()
    df_obesidade['rótulo'] = df_obesidade['contagem'].astype(int).astype(str) + ' (' + df_obesidade['percentual'].round(1).astype(str) + '%)'
    
    fig_obesidade = px.bar(
        df_obesidade,
        x='contagem',
        y='nivel_obesidade',
        text='rótulo',
        color='contagem',
        color_continuous_scale='Reds',
        orientation='h'
    )
    fig_obesidade.update_traces(textposition='outside')
    fig_obesidade.update_layout(
        title='Distribuição de Níveis de Obesidade',
        xaxis_title='Quantidade',
        yaxis_title='Nível de Obesidade',
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_obesidade, use_container_width=True)

# ============================================================
# STORYTELLING: GÊNERO
# ============================================================
st.markdown("---")
st.header("2️⃣ Qual a Relação entre Gênero e Obesidade?")
st.markdown("Comparação dos níveis de obesidade entre homens e mulheres.")

col1, col2 = st.columns(2)

with col1:
    fig_sexo = px.histogram(
        df_filtrado,
        x='sexo',
        text_auto=True,
        title='Distribuição por Gênero',
        color='sexo',
        color_discrete_sequence=['#FF6B9D', '#4A90E2']
    )
    fig_sexo.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_sexo, use_container_width=True)

with col2:
    if "nivel_obesidade" in df_filtrado.columns:
        fig_sexo_obesidade = px.histogram(
            df_filtrado,
            x='sexo',
            color='nivel_obesidade',
            text_auto=True,
            barmode='group',
            title='Gênero x Nível de Obesidade'
        )
        fig_sexo_obesidade.update_layout(height=400)
        st.plotly_chart(fig_sexo_obesidade, use_container_width=True)

# ============================================================
# STORYTELLING: IDADE
# ============================================================
st.markdown("---")
st.header("3️⃣ Como a Idade Influencia os Níveis de Obesidade?")
st.markdown("Visualizar a distribuição etária e sua correlação com o peso.")

fig_idade = px.histogram(
    df_filtrado,
    x="idade",
    color="nivel_obesidade",
    text_auto=True,
    barmode='group',
    title='Distribuição de Idade por Nível de Obesidade',
    nbins=15
)
fig_idade.update_layout(height=400)
st.plotly_chart(fig_idade, use_container_width=True)

# ============================================================
# STORYTELLING: HISTÓRICO FAMILIAR
# ============================================================
st.markdown("---")
st.header("4️⃣ O Histórico Familiar Impacta a Obesidade?")
st.markdown("Analisar se antecedentes familiares correlacionam com níveis de obesidade.")

if "hist_familiar_obes" in df_filtrado.columns:
    fig_familia = px.histogram(
        df_filtrado,
        x='hist_familiar_obes',
        color='nivel_obesidade',
        text_auto=True,
        barmode='group',
        title='Histórico Familiar x Nível de Obesidade',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_familia.update_layout(height=400)
    st.plotly_chart(fig_familia, use_container_width=True)

# ============================================================
# STORYTELLING: HÁBITOS E COMPORTAMENTOS
# ============================================================
st.markdown("---")
st.header("5️⃣ Qual o Impacto dos Hábitos no Nível de Obesidade?")
st.markdown("Explorar fatores de estilo de vida e suas correlações.")

col1, col2 = st.columns(2)

with col1:
    if "transporte" in df_filtrado.columns:
        fig_transporte = px.histogram(
            df_filtrado,
            x="nivel_obesidade",
            color="transporte",
            text_auto=True,
            barmode="group",
            title='Tipo de Transporte x Obesidade'
        )
        fig_transporte.update_layout(height=400)
        st.plotly_chart(fig_transporte, use_container_width=True)

with col2:
    if "fuma" in df_filtrado.columns:
        fig_fuma = px.histogram(
            df_filtrado,
            x="nivel_obesidade",
            color="fuma",
            text_auto=True,
            barmode="group",
            title='Tabagismo x Obesidade'
        )
        fig_fuma.update_layout(height=400)
        st.plotly_chart(fig_fuma, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    if "lancha_entre_ref" in df_filtrado.columns:
        fig_lancha = px.histogram(
            df_filtrado,
            x="nivel_obesidade",
            color="lancha_entre_ref",
            text_auto=True,
            barmode="group",
            title='Consumo de Snacks x Obesidade'
        )
        fig_lancha.update_layout(height=400)
        st.plotly_chart(fig_lancha, use_container_width=True)

with col2:
    if "controle_calorias" in df_filtrado.columns:
        fig_controle = px.histogram(
            df_filtrado,
            x="nivel_obesidade",
            color="controle_calorias",
            text_auto=True,
            barmode="group",
            title='Controle de Calorias x Obesidade'
        )
        fig_controle.update_layout(height=400)
        st.plotly_chart(fig_controle, use_container_width=True)

# ============================================================
# CORRELAÇÃO ENTRE VARIÁVEIS NUMÉRICAS
# ============================================================
st.markdown("---")
st.header("6️⃣ Correlação Entre Variáveis Numéricas")
st.markdown("Identificar relações entre medidas físicas e comportamentais.")

colunas_remover = ['cons_altas_cal_freq', 'hist_familiar_obes', 'lancha_entre_ref', 'fuma', 'controle_calorias', 'transporte',
             'sexo', 'cons_alcool', 'nivel_obesidade']

df_correl = df_filtrado.drop(columns=[c for c in colunas_remover if c in df_filtrado.columns], errors='ignore')
df_correl = df_correl.dropna()

if len(df_correl.columns) > 1:
    matriz_correlacao = df_correl.corr().round(2)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(matriz_correlacao, annot=True, cmap="coolwarm", linewidths=0.7, ax=ax, fmt='.2f')
    st.pyplot(fig)
else:
    st.info("Poucas variáveis numéricas disponíveis após aplicar os filtros.")

# ============================================================
# DADOS COMPLETOS
# ============================================================
st.markdown("---")
st.header("📋 Dados Completos Filtrados")

with st.expander("Clique para expandir e visualizar a tabela completa"):
    st.dataframe(df_filtrado, use_container_width=True)

st.markdown("---")
st.markdown("*Dashboard interativo criado com Streamlit e Plotly*")
