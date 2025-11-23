"""
Streamlit app: Predição de Obesidade — versão completa
Recursos inclusos:
- Multi-page (Home, Prever, Histórico, Sobre, Configurações)
- Autenticação simples (médico / paciente)
- Gráfico de risco (matplotlib)
- Perfil nutricional sugerido (baseado em respostas)
- Geração de PDF de relatório (FPDF)
- Banco de dados SQLite para registro histórico
- Criação automática de logo simples (PIL)
- Paleta de cores e tema dark/light (CSS)

Observações:
- Ajuste os caminhos e instale dependências: streamlit, pillow, fpdf, matplotlib
- Para rodar: `streamlit run streamlit_app_full.py`

"""
import os, sys
sys.path.append(os.path.abspath("."))

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import sqlite3
import os
from fpdf import FPDF
import matplotlib.pyplot as plt
from src.models.production_pipeline import load_model
from pathlib import Path

# -----------------------------
# Configurando root do projeto
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # sobe dois níveis até o root do projeto

xgb_model_path = str(BASE_DIR / "src" / "models" / "xgb_model.joblib")

# -----------------------------
# CONFIG
# -----------------------------
DB_PATH = "patients.db"
st.session_state.DB_PATH = "patients.db"
st.session_state.LOGO_PATH = "logo.png"
st.session_state.FONT_PATH = "src/fonts/DejaVuSans.ttf"
LOGO_PATH = "logo.png"
HOSPITAL_NAME = "Hospital TechSaúde"
st.session_state.nome_hospital = "Hospital TechSaúde"
st.session_state.HOSPITAL_NAME = "Hospital TechSaúde"
st.session_state.PRIMARY_COLOR = "#0A4D68"
st.session_state.ACCENT_COLOR = "#00A896"
PRIMARY_COLOR = "#0A4D68"  # azul hospital
ACCENT_COLOR = "#00A896"   # verde
BG_LIGHT = "#FFFFFF"
BG_DARK = "#0F1722"
TEXT_LIGHT = "#0B1B2B"
TEXT_DARK = "#E6EEF2"
st.session_state.model = load_model(
    xgb_model_path
)

st.session_state.FIELD_MAPPING = {
    "family_history": "Histórico familiar de obesidade",
    "FAVC": "Consumo de alimentos muito calóricos",
    "FCVC": "Consumo de vegetais",
    "NCP": "Nº de refeições diárias",
    "CAEC": "Lanches entre refeições",
    "SMOKE": "Fuma",
    "CH2O": "Consumo de água",
    "SCC": "Controla calorias",
    "FAF": "Atividade física semanal",
    "TUE": "Uso de tecnologia",
    "CALC": "Consumo de álcool",
    "MTRANS": "Meio de transporte"
}

st.session_state.EXPLAIN_NUMERIC = {
    "FCVC": {
        1: "Raramente",
        2: "Às vezes",
        3: "Sempre"
    },
    "NCP": {
        1: "1 refeição",
        2: "2 refeições",
        3: "3 refeições",
        4: "Mais de 3 refeições"
    },
    "CH2O": {
        1: "< 1L/dia",
        2: "1–2L/dia",
        3: "> 2L/dia"
    },
    "FAF": {
        0: "Nenhuma",
        1: "1–2x/sem",
        2: "3–4x/sem",
        3: "5x/sem ou mais"
    },
    "TUE": {
        0: "0–2h/dia",
        1: "3–5h/dia",
        2: "> 5h/dia"
    }
}

st.session_state.CATEGORY_TRANSLATION = {
    "yes": "Sim",
    "no": "Não",
    "Sometimes": "Às vezes",
    "Frequently": "Frequentemente",
    "Always": "Sempre",
    "Automobile": "Automóvel",
    "Motorbike": "Moto",
    "Public_Transportation": "Transporte público",
    "Bike": "Bicicleta",
    "Walking": "A pé",
}

# -----------------------------
# Conexão com Postgres
# -----------------------------


# -----------------------------
# UTIL: criar logo simples
# -----------------------------
def create_logo(path=LOGO_PATH, hospital=HOSPITAL_NAME):
    if os.path.exists(path):
        return path
    img = Image.new("RGBA", (400, 100), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    # Desenho simples: cruz + texto
    # cross
    draw.rectangle((20, 20, 70, 80), fill=PRIMARY_COLOR)
    draw.rectangle((40, 0, 50, 100), fill=ACCENT_COLOR)
    # texto
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    draw.text((90, 30), hospital, fill=PRIMARY_COLOR, font=font)
    img.save(path)
    return path

# -----------------------------
# UTIL: inicializar DB
# -----------------------------


# Criar tabela se não existir no sqlite
def init_db(path=DB_PATH):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_type TEXT,
            user_name TEXT,
            inputs TEXT,
            mensagem TEXT,
            probabilidade REAL
        )
        """
    )
    conn.commit()
    conn.close()

# -----------------------------
# GERAR PDF (FPDF) - COM UTF-8
# -----------------------------

FONT_PATH = "src/fonts/DejaVuSans.ttf"   # ajuste se necessário

# Tradução / descrição dos campos
FIELD_MAPPING = {
    "family_history": "Histórico familiar de obesidade",
    "FAVC": "Consumo de alimentos muito calóricos",
    "FCVC": "Consumo de vegetais",
    "NCP": "Nº de refeições diárias",
    "CAEC": "Lanches entre refeições",
    "SMOKE": "Fuma",
    "CH2O": "Consumo de água",
    "SCC": "Controla calorias",
    "FAF": "Atividade física semanal",
    "TUE": "Uso de tecnologia",
    "CALC": "Consumo de álcool",
    "MTRANS": "Meio de transporte"
}

# Tradução de categorias
CATEGORY_TRANSLATION = {
    "yes": "Sim",
    "no": "Não",
    "Sometimes": "Às vezes",
    "Frequently": "Frequentemente",
    "Always": "Sempre",
    "Automobile": "Automóvel",
    "Motorbike": "Moto",
    "Public_Transportation": "Transporte público",
    "Bike": "Bicicleta",
    "Walking": "A pé",
}

# Interpretação de valores numéricos
EXPLAIN_NUMERIC = {
    "FCVC": {
        1: "Raramente",
        2: "Às vezes",
        3: "Sempre"
    },
    "NCP": {
        1: "1 refeição",
        2: "2 refeições",
        3: "3 refeições",
        4: "Mais de 3 refeições"
    },
    "CH2O": {
        1: "< 1L/dia",
        2: "1–2L/dia",
        3: "> 2L/dia"
    },
    "FAF": {
        0: "Nenhuma",
        1: "1–2x/sem",
        2: "3–4x/sem",
        3: "5x/sem ou mais"
    },
    "TUE": {
        0: "0–2h/dia",
        1: "3–5h/dia",
        2: "> 5h/dia"
    }
}


class PDFReport(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, 10, 8, 33)

        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, HOSPITAL_NAME, ln=True, align="R")
        self.ln(5)

    def footer(self):
        self.set_y(-35)
        self.set_font("DejaVu", size=9)
        self.multi_cell(0, 6, "Profissional responsável: __________________________")
        self.ln(2)
        self.multi_cell(0, 6, "Assinatura: ________________________________________")
        self.ln(5)
        self.cell(0, 10, "Documento gerado automaticamente pelo sistema clínico", align="C")

# -----------------------------
# EXEMPLO DE FUNCAO DE PREDICAO (placeholder)
# -----------------------------
# A função real deve vir do seu pipeline: predict_from_input(model, user_input)
# Aqui criamos uma simulação para o app funcionar caso o usuário não carregue o modelo.

def dummy_predict(user_input):
    # rules-based simple risk score
    score = 0
    mapping = {
        'yes': 2,
        'no': 0,
        'Sometimes': 1,
        'Frequently': 2,
        'Always': 3,
        'Automobile': 2,
        'Motorbike': 1,
        'Public_Transportation': 1,
        'Bike': 0,
        'Walking': 0
    }
    for k, v in user_input.items():
        if isinstance(v, str):
            score += mapping.get(v, 0)
        elif isinstance(v, (int, float)):
            score += v
    prob = min(100, int(score * 6))
    if prob < 30:
        msg = 'Baixo risco estimado de obesidade.'
    elif prob < 60:
        msg = 'Risco moderado — recomenda-se acompanhamento.'
    else:
        msg = 'Alto risco — avaliar intervenções imediatas.'
    return {"mensagem": msg, "probabilidade": prob}

# -----------------------------
# RENDER: gráfico de risco
# -----------------------------
def render_risk_chart(prob):
    fig, ax = plt.subplots(figsize=(6, 2))
    ax.barh([0], [prob], height=0.6)
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xlabel('Probabilidade (%)')
    ax.set_title('Probabilidade Estimada de Obesidade')
    # cor por faixa
    if prob < 30:
        color = '#2ECC71'
    elif prob < 60:
        color = '#F1C40F'
    else:
        color = '#E74C3C'
    ax.patches[0].set_color(color)
    for spine in ax.spines.values():
        spine.set_visible(False)
    return fig

# -----------------------------
# CSS: tema e paleta
# -----------------------------
def local_css(dark=False):
    bg = BG_DARK if dark else BG_LIGHT
    text = TEXT_DARK if dark else TEXT_LIGHT
    css = f"""
    <style>
    .reportview-container {{background: {bg};}}
    .sidebar .sidebar-content {{background: {PRIMARY_COLOR};}}
    h1, h2, h3, p, label {{color: {text};}}
    .stButton>button {{ background-color: {ACCENT_COLOR}; color: white; }}
    .stMetric>div>div>div:nth-child(1) {{ color: {PRIMARY_COLOR}; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -----------------------------
# AUTENTICAÇÃO SIMPLES
# -----------------------------
# Para demo: credenciais em memória. Em produção, usar sistema seguro.
CREDENTIALS = {
    'medico': {'user': 'medico', 'pass': 'med123'},
    'paciente': {'user': 'paciente', 'pass': 'pac123'}
}

def auth_widget():
    if 'auth' not in st.session_state:
        st.session_state['auth'] = False
        st.session_state['user_type'] = None
        st.session_state['user_name'] = None
    with st.sidebar.expander('🔒 Login'):
        if not st.session_state['auth']:
            user = st.text_input('Usuário')
            pwd = st.text_input('Senha', type='password')
            tipo = st.selectbox('Tipo', ['medico', 'paciente'])
            if st.button('Entrar'):
                cred = CREDENTIALS.get(tipo)
                if cred and user == cred['user'] and pwd == cred['pass']:
                    st.session_state['auth'] = True
                    st.session_state['user_type'] = tipo
                    st.session_state['user_name'] = user
                    st.success('Login efetuado')
                else:
                    st.error('Credenciais inválidas')
        else:
            st.write(f"Logado como: **{st.session_state['user_name']}** ({st.session_state['user_type']})")
            if st.button('Sair'):
                st.session_state['auth'] = False
                st.session_state['user_type'] = None
                st.session_state['user_name'] = None
                st.experimental_rerun()

# -----------------------------
# MAIN
# -----------------------------

def main():
    st.set_page_config(
        page_title='Predição de Obesidade - Sistema Clínico',
        page_icon='🩺',
        layout='wide'
    )

    create_logo()

    if 'theme_dark' not in st.session_state:
        st.session_state['theme_dark'] = False

    pages = [
        st.Page("pages/Home.py", title="Home", icon=":material/home:"),
        st.Page("pages/Dashboard.py", title="EDA", icon=":material/analytics:"),
        st.Page("pages/Historico.py", title="Histórico", icon=":material/history:"),
        st.Page("pages/Prever.py", title="Prever", icon=":material/search:"),
        st.Page("pages/Sobre.py", title="Sobre", icon=":material/info:")
    ]

    pg = st.navigation(pages)
    pg.run()

    init_db()

if __name__ == '__main__':
    main()