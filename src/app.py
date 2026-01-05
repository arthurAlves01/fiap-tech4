import os, sys
import streamlit as st
<<<<<<< HEAD
=======
from PIL import Image, ImageDraw, ImageFont
import sqlite3
import os
from fpdf import FPDF
import matplotlib.pyplot as plt
from src.models.production_pipeline import load_model
from pathlib import Path
from src.shared.connection import init_db
>>>>>>> 6ef5725b88c105026ec44da32fd9ede12c957cac

# Ensure repository root is on sys.path for local imports
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
src_dir = os.path.abspath(os.path.dirname(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Minimal app loader to expose only the required pages in the navigation
from src.pages.Home import render_home
from src.pages.Prever import render_predict
from src.pages.Historico import render_historico
from src.pages.Sobre import render_sobre
from src.pages.Dashboard import render_dashboard

<<<<<<< HEAD
st.set_page_config(page_title="App Principal - Obesidade", page_icon="🏥", layout="wide")
=======
# -----------------------------
# CONFIG
# -----------------------------
st.session_state.DB_PATH = BASE_DIR / "data" / "patients.db"
st.session_state.LOGO_PATH = "assets/images/logo.png"
st.session_state.FONT_PATH = "assets/fonts/DejaVuSans.ttf"
st.session_state.nome_hospital = "Hospital TechSaúde"
st.session_state.HOSPITAL_NAME = "Hospital TechSaúde"
st.session_state.PRIMARY_COLOR = "#0A4D68"
st.session_state.ACCENT_COLOR = "#00A896"
st.session_state.BG_LIGHT = "#FFFFFF"
st.session_state.BG_DARK = "#0F1722"
st.session_state.TEXT_LIGHT = "#0B1B2B"
st.session_state.TEXT_DARK = "#E6EEF2"
st.session_state.model = load_model(
    xgb_model_path
)
>>>>>>> 6ef5725b88c105026ec44da32fd9ede12c957cac

menu = ["Home", "Prever", "Historico", "Sobre"]
choice = st.sidebar.selectbox("Navegação", menu, index=0)

<<<<<<< HEAD
if choice == "Home":
    render_home()
elif choice == "Prever":
    render_predict()
elif choice == "Historico":
    render_historico()
elif choice == "Sobre":
    render_sobre()
=======
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
    bg = st.session_state.BG_DARK if dark else st.session_state.BG_LIGHT
    text = st.session_state.TEXT_DARK if dark else st.session_state.TEXT_LIGHT
    css = f"""
    <style>
    .reportview-container {{background: {bg};}}
    .sidebar .sidebar-content {{background: {st.session_state.PRIMARY_COLOR};}}
    h1, h2, h3, p, label {{color: {text};}}
    .stButton>button {{ background-color: {st.session_state.ACCENT_COLOR}; color: white; }}
    .stMetric>div>div>div:nth-child(1) {{ color: {st.session_state.PRIMARY_COLOR}; }}
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

    auth_widget()

    if 'theme_dark' not in st.session_state:
        st.session_state['theme_dark'] = False

    pages = [
        st.Page("pages/Home.py", title="Home", icon=":material/home:"),
        st.Page("pages/Prever.py", title="Prever", icon=":material/search:"),
        st.Page("pages/Historico.py", title="Histórico", icon=":material/history:"),
        st.Page("pages/Dashboard.py", title="EDA", icon=":material/analytics:"),
        st.Page("pages/Sobre.py", title="Sobre", icon=":material/info:")        
    ]

    pg = st.navigation(pages)
    pg.run()

    init_db(st.session_state.DB_PATH)

if __name__ == '__main__':
    main()
>>>>>>> 6ef5725b88c105026ec44da32fd9ede12c957cac
