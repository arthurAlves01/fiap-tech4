import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Dashboard de Saúde - Análise de Obesidade",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS PERSONALIZADO PARA MELHOR APRESENTAÇÃO
# ============================================================
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .insight-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-top: 1rem;
        margin-bottom: 1rem;
        color: #262730 !important;
        font-size: 1rem;
        line-height: 1.6;
    }
    .insight-box strong {
        color: #1f77b4;
    }
    .metric-container {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# CABEÇALHO PRINCIPAL
# ============================================================
st.markdown('<h1 class="main-header">🏥 Dashboard de Análise de Saúde</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Análise exploratória de dados de obesidade com insights baseados em evidências científicas</p>', unsafe_allow_html=True)

# ============================================================
# SIDEBAR — FILTROS DINÂMICOS
# ============================================================
st.sidebar.title("⚙️ Painel de Controle")
st.sidebar.markdown("---")

# Carregamento e preparação dos dados
@st.cache_data
def load_and_prepare_data():
    """Carrega e prepara os dados com cache para melhor performance"""
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
    return df

df = load_and_prepare_data()

# Filtros na sidebar
st.sidebar.subheader("📊 Filtros de Dados")

# Filtro por gênero
sexo_list = sorted(df["sexo"].unique())
sexo_filter = st.sidebar.multiselect("👥 Gênero", sexo_list, default=sexo_list)

# Faixa de idade
min_idade = int(df["idade"].min())
max_idade = int(df["idade"].max())
idade_filter = st.sidebar.slider("📅 Faixa de Idade", min_idade, max_idade, (min_idade, max_idade))

# Nível de Obesidade
if "nivel_obesidade" in df.columns:
    obesidade_list = sorted(df["nivel_obesidade"].unique())
    obesidade_filter = st.sidebar.multiselect("⚖️ Nível de Obesidade", obesidade_list, default=obesidade_list)
else:
    obesidade_filter = None

# Histórico familiar
if "hist_familiar_obes" in df.columns:
    familia_list = sorted(df["hist_familiar_obes"].unique())
    familia_filter = st.sidebar.multiselect("👨‍👩‍👧 Histórico Familiar", familia_list, default=familia_list)
else:
    familia_filter = None

# Transporte
if "transporte" in df.columns:
    transporte_list = sorted(df["transporte"].unique())
    transporte_filter = st.sidebar.multiselect("🚗 Transporte", transporte_list, default=transporte_list)
else:
    transporte_filter = None

# Tabagismo
if "fuma" in df.columns:
    fuma_list = sorted(df["fuma"].unique())
    fuma_filter = st.sidebar.multiselect("🚭 Tabagismo", fuma_list, default=fuma_list)
else:
    fuma_filter = None

# Snacks entre refeições
if "lancha_entre_ref" in df.columns:
    lancha_list = sorted(df["lancha_entre_ref"].unique())
    lancha_filter = st.sidebar.multiselect("🍿 Snacks entre Refeições", lancha_list, default=lancha_list)
else:
    lancha_filter = None

# Controle de Calorias
if "controle_calorias" in df.columns:
    controle_list = sorted(df["controle_calorias"].unique())
    controle_filter = st.sidebar.multiselect("📊 Controle de Calorias", controle_list, default=controle_list)
else:
    controle_filter = None

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ============================================================
# APLICAÇÃO DOS FILTROS
# ============================================================
def apply_filters(df, sexo_filter, idade_filter, obesidade_filter, familia_filter, 
                  transporte_filter, fuma_filter, lancha_filter, controle_filter):
    """Aplica todos os filtros selecionados"""
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
    
    return df_filtrado

df_filtrado = apply_filters(df, sexo_filter, idade_filter, obesidade_filter, familia_filter,
                           transporte_filter, fuma_filter, lancha_filter, controle_filter)

# ============================================================
# INDICADORES PRINCIPAIS (KPIs)
# ============================================================
st.markdown("---")
st.header("📊 Indicadores Principais (KPIs)")

col1, col2, col3, col4, col5 = st.columns(5)

# Total de registros
total_registros = len(df_filtrado)
col1.metric("👥 Total de Pessoas", f"{total_registros:,}", 
            help="Número total de registros após aplicação dos filtros")

# Idade média
idade_media = df_filtrado["idade"].mean()
idade_std = df_filtrado["idade"].std()
col2.metric("📅 Idade Média", f"{idade_media:.1f} anos", 
            delta=f"±{idade_std:.1f}",
            help="Idade média da população analisada com desvio padrão")

# Peso médio
peso_medio = df_filtrado["peso"].mean()
col3.metric("⚖️ Peso Médio", f"{peso_medio:.1f} kg",
            help="Peso médio em quilogramas")

# Altura média
altura_media = df_filtrado["altura"].mean()
col4.metric("📏 Altura Média", f"{altura_media:.2f} m",
            help="Altura média em metros")

# Taxa de obesidade
if "nivel_obesidade" in df_filtrado.columns:
    casos_obesidade = len(df_filtrado[df_filtrado["nivel_obesidade"].str.contains("Obesidade", case=False, na=False)])
    taxa_obesidade = (casos_obesidade / total_registros * 100) if total_registros > 0 else 0
    casos_total = len(df[df["nivel_obesidade"].str.contains("Obesidade", case=False, na=False)])
    taxa_total = (casos_total / len(df) * 100) if len(df) > 0 else 0
    delta_obesidade = f"{taxa_obesidade - taxa_total:.1f}%"
    col5.metric("⚠️ Taxa de Obesidade", f"{taxa_obesidade:.1f}%", 
                delta=delta_obesidade if taxa_obesidade != taxa_total else None,
                help="Percentual de pessoas com Obesidade Tipo I, II ou III")

# ============================================================
# ANÁLISE 1: DISTRIBUIÇÃO DE NÍVEIS DE OBESIDADE
# ============================================================
st.markdown("---")
st.header("1️⃣ Distribuição de Níveis de Obesidade")
st.markdown("**Objetivo:** Compreender a proporção populacional em cada categoria de peso segundo classificação IMC.")

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
        orientation='h',
        labels={'contagem': 'Quantidade de Pessoas', 'nivel_obesidade': 'Nível de Obesidade'}
    )
    fig_obesidade.update_traces(textposition='outside', textfont_size=11)
    fig_obesidade.update_layout(
        title='Distribuição de Níveis de Obesidade na População',
        xaxis_title='Quantidade de Pessoas',
        yaxis_title='',
        showlegend=False,
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_obesidade, use_container_width=True)
    
    # Insight
    categoria_maior = df_obesidade.loc[df_obesidade['contagem'].idxmax(), 'nivel_obesidade']
    percentual_maior = df_obesidade.loc[df_obesidade['contagem'].idxmax(), 'percentual']
    st.markdown(f"""
    <div class="insight-box">
        <strong>💡 Insight:</strong> A categoria <strong>{categoria_maior}</strong> representa {percentual_maior:.1f}% da população analisada. 
        Esta distribuição permite identificar grupos de risco prioritários para intervenções de saúde pública. 
        Categorias com maior prevalência indicam necessidade de programas preventivos direcionados.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# ANÁLISE 2: GÊNERO E OBESIDADE
# ============================================================
st.markdown("---")
st.header("2️⃣ Análise de Gênero e Obesidade")
st.markdown("**Objetivo:** Identificar diferenças na distribuição de obesidade entre gêneros para orientar estratégias de prevenção específicas.")

col1, col2 = st.columns(2)

with col1:
    fig_sexo = px.histogram(
        df_filtrado,
        x='sexo',
        text_auto=True,
        title='Distribuição Amostral por Gênero',
        color='sexo',
        color_discrete_sequence=['#FF6B9D', '#4A90E2'],
        labels={'sexo': 'Gênero', 'count': 'Quantidade'}
    )
    fig_sexo.update_layout(
        showlegend=False, 
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_sexo, use_container_width=True)

with col2:
    if "nivel_obesidade" in df_filtrado.columns:
        fig_sexo_obesidade = px.histogram(
            df_filtrado,
            x='sexo',
            color='nivel_obesidade',
            text_auto=True,
            barmode='group',
            title='Distribuição de Obesidade por Gênero',
            labels={'sexo': 'Gênero', 'count': 'Quantidade'}
        )
        fig_sexo_obesidade.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_sexo_obesidade, use_container_width=True)

# Insight
if "nivel_obesidade" in df_filtrado.columns:
    obesidade_por_sexo = df_filtrado.groupby('sexo')['nivel_obesidade'].apply(
        lambda x: (x.str.contains('Obesidade', case=False, na=False).sum() / len(x) * 100)
    ).round(1)
    
    if len(obesidade_por_sexo) > 0:
        sexo_maior_risco = obesidade_por_sexo.idxmax()
        taxa_sexo = obesidade_por_sexo.max()
        st.markdown(f"""
        <div class="insight-box">
            <strong>💡 Insight:</strong> A taxa de obesidade no gênero <strong>{sexo_maior_risco}</strong> é de {taxa_sexo}%, 
            evidenciando diferenças significativas entre gêneros. Esta disparidade sugere a necessidade de abordagens 
            diferenciadas em campanhas de saúde, considerando fatores hormonais, metabólicos e comportamentais específicos de cada gênero.
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# ANÁLISE 3: IDADE E OBESIDADE
# ============================================================
st.markdown("---")
st.header("3️⃣ Impacto da Idade nos Níveis de Obesidade")
st.markdown("**Objetivo:** Analisar a correlação entre faixas etárias e prevalência de obesidade para identificar períodos críticos de intervenção.")

fig_idade = px.histogram(
    df_filtrado,
    x="idade",
    color="nivel_obesidade",
    text_auto=True,
    barmode='group',
    title='Distribuição de Idade por Nível de Obesidade',
    nbins=15,
    labels={'idade': 'Idade (anos)', 'count': 'Quantidade'}
)
fig_idade.update_layout(
    height=450,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_idade, use_container_width=True)

# Insight
if "nivel_obesidade" in df_filtrado.columns:
    idade_obesidade = df_filtrado[df_filtrado["nivel_obesidade"].str.contains("Obesidade", case=False, na=False)]["idade"]
    idade_normal = df_filtrado[~df_filtrado["nivel_obesidade"].str.contains("Obesidade", case=False, na=False)]["idade"]
    
    if len(idade_obesidade) > 0 and len(idade_normal) > 0:
        idade_media_obesidade = idade_obesidade.mean()
        idade_media_normal = idade_normal.mean()
        diferenca = abs(idade_media_obesidade - idade_media_normal)
        
        st.markdown(f"""
        <div class="insight-box">
            <strong>💡 Insight:</strong> A idade média de pessoas com obesidade é {idade_media_obesidade:.1f} anos, 
            enquanto pessoas com peso normal têm média de {idade_media_normal:.1f} anos (diferença de {diferenca:.1f} anos). 
            Esta correlação indica que a idade é um fator de risco importante, possivelmente relacionado a mudanças metabólicas, 
            redução de atividade física e alterações hormonais ao longo da vida.
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# ANÁLISE 4: HISTÓRICO FAMILIAR
# ============================================================
st.markdown("---")
st.header("4️⃣ Influência do Histórico Familiar na Obesidade")
st.markdown("**Objetivo:** Avaliar o impacto de antecedentes familiares como fator preditivo de risco para desenvolvimento de obesidade.")

if "hist_familiar_obes" in df_filtrado.columns:
    fig_familia = px.histogram(
        df_filtrado,
        x='hist_familiar_obes',
        color='nivel_obesidade',
        text_auto=True,
        barmode='group',
        title='Histórico Familiar x Nível de Obesidade',
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={'hist_familiar_obes': 'Histórico Familiar', 'count': 'Quantidade'}
    )
    fig_familia.update_layout(
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_familia, use_container_width=True)
    
    # Insight
    familia_obesidade = df_filtrado[df_filtrado['hist_familiar_obes'] == 'Sim']
    familia_sem = df_filtrado[df_filtrado['hist_familiar_obes'] == 'Não']
    
    if len(familia_obesidade) > 0 and len(familia_sem) > 0:
        taxa_com_familia = (familia_obesidade['nivel_obesidade'].str.contains('Obesidade', case=False, na=False).sum() / len(familia_obesidade) * 100)
        taxa_sem_familia = (familia_sem['nivel_obesidade'].str.contains('Obesidade', case=False, na=False).sum() / len(familia_sem) * 100)
        
        st.markdown(f"""
        <div class="insight-box">
            <strong>💡 Insight:</strong> Pessoas com histórico familiar de obesidade apresentam taxa de {taxa_com_familia:.1f}%, 
            enquanto aquelas sem histórico têm {taxa_sem_familia:.1f}% (diferença de {abs(taxa_com_familia - taxa_sem_familia):.1f} pontos percentuais). 
            Este resultado reforça a importância de fatores genéticos e ambientais compartilhados, indicando que indivíduos com histórico familiar 
            devem ser priorizados em programas de prevenção precoce e monitoramento contínuo.
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# ANÁLISE 5: HÁBITOS E COMPORTAMENTOS
# ============================================================
st.markdown("---")
st.header("5️⃣ Impacto dos Hábitos de Vida na Obesidade")
st.markdown("**Objetivo:** Identificar correlações entre comportamentos de estilo de vida e níveis de obesidade para orientar intervenções comportamentais.")

col1, col2 = st.columns(2)

with col1:
    if "transporte" in df_filtrado.columns:
        fig_transporte = px.histogram(
            df_filtrado,
            x="nivel_obesidade",
            color="transporte",
            text_auto=True,
            barmode="group",
            title='Tipo de Transporte x Nível de Obesidade',
            labels={'nivel_obesidade': 'Nível de Obesidade', 'count': 'Quantidade'}
        )
        fig_transporte.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_transporte, use_container_width=True)

with col2:
    if "fuma" in df_filtrado.columns:
        fig_fuma = px.histogram(
            df_filtrado,
            x="nivel_obesidade",
            color="fuma",
            text_auto=True,
            barmode="group",
            title='Tabagismo x Nível de Obesidade',
            labels={'nivel_obesidade': 'Nível de Obesidade', 'count': 'Quantidade'}
        )
        fig_fuma.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
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
            title='Consumo de Snacks x Nível de Obesidade',
            labels={'nivel_obesidade': 'Nível de Obesidade', 'count': 'Quantidade'}
        )
        fig_lancha.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_lancha, use_container_width=True)

with col2:
    if "controle_calorias" in df_filtrado.columns:
        fig_controle = px.histogram(
            df_filtrado,
            x="nivel_obesidade",
            color="controle_calorias",
            text_auto=True,
            barmode="group",
            title='Controle de Calorias x Nível de Obesidade',
            labels={'nivel_obesidade': 'Nível de Obesidade', 'count': 'Quantidade'}
        )
        fig_controle.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_controle, use_container_width=True)

# Insights combinados
insights_habitos = []
if "transporte" in df_filtrado.columns:
    transporte_obesidade = df_filtrado[df_filtrado["nivel_obesidade"].str.contains("Obesidade", case=False, na=False)]
    if len(transporte_obesidade) > 0:
        transporte_mais_comum = transporte_obesidade["transporte"].mode()[0] if len(transporte_obesidade["transporte"].mode()) > 0 else "N/A"
        insights_habitos.append(f"Transporte mais associado à obesidade: <strong>{transporte_mais_comum}</strong>")

if "controle_calorias" in df_filtrado.columns:
    controle_obesidade = df_filtrado[df_filtrado["nivel_obesidade"].str.contains("Obesidade", case=False, na=False)]
    if len(controle_obesidade) > 0:
        taxa_sem_controle = (controle_obesidade["controle_calorias"] == "Não").sum() / len(controle_obesidade) * 100
        insights_habitos.append(f"{taxa_sem_controle:.1f}% das pessoas com obesidade não controlam calorias")

if insights_habitos:
    st.markdown(f"""
    <div class="insight-box">
        <strong>💡 Insight:</strong> {' | '.join(insights_habitos)}. 
        Estes padrões comportamentais indicam que intervenções focadas em educação nutricional, atividade física 
        e mudança de hábitos podem ser altamente efetivas na prevenção e tratamento da obesidade.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# ANÁLISE 6: MATRIZ DE CORRELAÇÃO
# ============================================================
st.markdown("---")
st.header("6️⃣ Análise de Correlação entre Variáveis Numéricas")
st.markdown("**Objetivo:** Identificar relações estatísticas entre variáveis contínuas para compreender fatores interdependentes.")

colunas_remover = ['cons_altas_cal_freq', 'hist_familiar_obes', 'lancha_entre_ref', 'fuma', 'controle_calorias', 'transporte',
             'sexo', 'cons_alcool', 'nivel_obesidade']

df_correl = df_filtrado.drop(columns=[c for c in colunas_remover if c in df_filtrado.columns], errors='ignore')
df_correl = df_correl.select_dtypes(include=[np.number]).dropna()

if len(df_correl.columns) > 1:
    matriz_correlacao = df_correl.corr().round(2)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(
        matriz_correlacao, 
        annot=True, 
        cmap="coolwarm", 
        center=0,
        linewidths=0.7, 
        ax=ax, 
        fmt='.2f',
        square=True,
        cbar_kws={"shrink": 0.8}
    )
    ax.set_title('Matriz de Correlação entre Variáveis Numéricas', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    st.pyplot(fig)
    
    # Insight
    if len(matriz_correlacao) > 0:
        # Encontrar maior correlação (excluindo diagonal)
        mask = np.triu(np.ones_like(matriz_correlacao, dtype=bool), k=1)
        correlacoes = matriz_correlacao.where(mask).stack()
        if len(correlacoes) > 0:
            max_corr = correlacoes.abs().idxmax()
            valor_corr = correlacoes.loc[max_corr]
            
            st.markdown(f"""
            <div class="insight-box">
                <strong>💡 Insight:</strong> A maior correlação observada é entre <strong>{max_corr[0]}</strong> e <strong>{max_corr[1]}</strong> 
                (r = {valor_corr:.2f}). {'Correlação forte' if abs(valor_corr) > 0.7 else 'Correlação moderada' if abs(valor_corr) > 0.4 else 'Correlação fraca'}, 
                indicando que estas variáveis estão {'fortemente' if abs(valor_corr) > 0.7 else 'moderadamente' if abs(valor_corr) > 0.4 else 'fracamente'} relacionadas. 
                Esta relação pode sugerir causalidade ou fatores comuns subjacentes que devem ser considerados em modelos preditivos e intervenções clínicas.
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("⚠️ Poucas variáveis numéricas disponíveis após aplicar os filtros para análise de correlação.")

# ============================================================
# DADOS COMPLETOS
# ============================================================
st.markdown("---")
st.header("📋 Base de Dados Completa")

with st.expander("🔍 Visualizar Tabela Completa de Dados Filtrados", expanded=False):
    st.dataframe(
        df_filtrado,
        use_container_width=True,
        height=400
    )
    st.caption(f"Total de registros: {len(df_filtrado):,} | Total de colunas: {len(df_filtrado.columns)}")

# ============================================================
# RODAPÉ teste
# ============================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>Dashboard de Análise de Saúde - Obesidade</strong></p>
    <p>Desenvolvido com Streamlit, Plotly e Pandas | Análise baseada em dados científicos</p>
    <p style='font-size: 0.9rem;'>© 2024 | Todos os dados são para fins de análise e pesquisa</p>
</div>
""", unsafe_allow_html=True)
