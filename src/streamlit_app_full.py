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
import io
import os
import re
import base64
from fpdf import FPDF
import matplotlib.pyplot as plt
from datetime import datetime, timezone
#import datetime
from src.production_pipeline import predict_from_input, load_model
from pathlib import Path

# -----------------------------
# CONFIG
# -----------------------------
DB_PATH = "patients.db"
LOGO_PATH = "logo.png"
HOSPITAL_NAME = "Hospital TechSaúde"
PRIMARY_COLOR = "#0A4D68"  # azul hospital
ACCENT_COLOR = "#00A896"   # verde
BG_LIGHT = "#FFFFFF"
BG_DARK = "#0F1722"
TEXT_LIGHT = "#0B1B2B"
TEXT_DARK = "#E6EEF2"

# -----------------------------
# Configurando root do projeto
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # sobe dois níveis até o root do projeto

xgb_model_path = str(BASE_DIR / "notebook" / "xgb_model.joblib")

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
# SALVAR registro
# -----------------------------

# Salvar no SQLite
def save_record(user_type, user_name, inputs, mensagem, probabilidade, path=DB_PATH):
    timestamp_utc = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(path)
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO records 
        (timestamp, user_type, user_name, inputs, mensagem, probabilidade) 
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (timestamp_utc, user_type, user_name, str(inputs), mensagem, probabilidade),
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


def generate_pdf(patient_name, inputs, mensagem, probabilidade):
    pdf = PDFReport()

    # Fonte Unicode
    pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
    pdf.add_font("DejaVu", "B", FONT_PATH, uni=True)
    pdf.set_font("DejaVu", size=12)

    pdf.add_page()

    # Título
    pdf.cell(0, 10, f"Relatório de Avaliação — {patient_name}", ln=True)

    # Data BR
    dt = datetime.now()
    formatted_date = dt.strftime("%d/%m/%Y - %H:%M")

    pdf.ln(4)
    pdf.set_font("DejaVu", size=10)
    pdf.cell(0, 8, f"Data: {formatted_date}", ln=True)

    # BLOCO — DADOS DO PACIENTE
    pdf.ln(6)
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 8, "Dados do paciente:", ln=True)

    pdf.set_font("DejaVu", size=10)
    for k, v in inputs.items():

        field_name = FIELD_MAPPING.get(k, k)

        # Traduz valores categóricos
        if isinstance(v, str) and v in CATEGORY_TRANSLATION:
            display_value = CATEGORY_TRANSLATION[v]
        else:
            display_value = v

        # Se tiver explicação numérica
        if k in EXPLAIN_NUMERIC:
            meaning = EXPLAIN_NUMERIC[k].get(v)
            if meaning:
                display_value = f"{v} — {meaning}"

        pdf.multi_cell(0, 6, f" • {field_name}: {display_value}")

    # BLOCO — RESULTADO
    pdf.ln(4)
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 8, "Resultado da predição:", ln=True)

    pdf.set_font("DejaVu", size=11)
    pdf.multi_cell(0, 6, f"Mensagem: {mensagem}")
    pdf.ln(2)
    pdf.multi_cell(0, 6, f"Probabilidade estimada: {probabilidade:.2f}%")

    return pdf.output(dest="S").encode("latin1", "replace")

# -----------------------------
# RECOMENDACOES NUTRICIONAIS SIMPLES
# -----------------------------
def recommend_nutrition_profile(inputs):
    # heurísticas simples para sugestão
    recs = []
    if inputs.get('FAVC') == 'yes':
        recs.append('Reduzir alimentos de alta caloria; priorizar fontes proteicas magras e fibras.')
    if inputs.get('FCVC', 3) <= 2:
        recs.append('Aumentar consumo de vegetais (>=3 porções/dia).')
    if inputs.get('CH2O', 2) <= 1:
        recs.append('Aumentar ingestão de água para 1-2 L/dia ou mais.')
    if inputs.get('FAF', 0) == 0:
        recs.append('Iniciar programa de atividade física gradual (ex.: 3x/sem 30 min).')
    if inputs.get('SMOKE') == 'yes':
        recs.append('Considerar cessação do tabaco; avaliar suporte médico.')
    if not recs:
        recs.append('Manter hábitos saudáveis; alimentação balanceada e atividade física regular.')
    return recs

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
# PÁGINAS
# -----------------------------

def render_home():
    st.image(create_logo())
    st.title('Bem-vindo ao Sistema de Avaliação Preventiva')
    st.markdown(
        f"""
        **{HOSPITAL_NAME}** — Ferramenta de suporte para triagem e acompanhamento do risco de obesidade.

        Este sistema auxilia médicos e equipes multidisciplinares a identificar pacientes com maior risco
de desenvolver obesidade, sugerindo ações nutricionais e gerando relatórios clínicos.
        """
    )
    st.write('---')
    st.markdown('### Como funciona')
    st.markdown('- Preencha o formulário na aba **Prever**')
    st.markdown('- Receba uma estimativa de risco, recomendações nutricionais e um PDF para impressão')
    st.markdown('- Registre o exame no histórico do paciente (DB local)')


def render_predict(load_model_fn=None, predict_fn=None):
    st.header('Formulário de triagem')
    with st.form('predict_form'):
        
        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input('Nome do paciente')
            family_history = st.selectbox('Histórico familiar de obesidade', ['yes', 'no'])
            FAVC = st.selectbox('Consome alimentos de alta caloria', ['yes', 'no'])
            FCVC = st.number_input('Frequência consumo verduras (1=raramente,3=sempre)', min_value=1, max_value=3, value=3)
            NCP = st.number_input('Refeições por dia (1-4)', min_value=1, max_value=4, value=3)
            CAEC = st.selectbox('Lanche entre refeições', ['no', 'Sometimes', 'Frequently', 'Always'])

        with col2:
            SMOKE = st.selectbox('Fuma?', ['yes', 'no'])
            CH2O = st.number_input('Água por dia (1<1L,2=1-2L,3>2L)', min_value=1, max_value=3, value=2)
            SCC = st.selectbox('Controla calorias?', ['yes', 'no'])
            FAF = st.number_input('Atividade física (0-3)', min_value=0, max_value=3, value=1)
            TUE = st.number_input('Uso tecnologia (0-2)', min_value=0, max_value=2, value=1)

        col3, col4 = st.columns(2)
        with col3:
            CALC = st.selectbox('Consumo de álcool', ['no', 'Sometimes', 'Frequently', 'Always'])
        with col4:
            MTRANS = st.selectbox('Meio de transporte', ['Automobile','Motorbike','Public_Transportation','Bike','Walking'])

        submitted = st.form_submit_button('🔍 Analisar paciente')

    if submitted:
        
        if predict_fn is None:
            st.error("⚠ Nenhuma função de predição fornecida.")
            return
        
        inputs = {
            'Nome': nome,
            'family_history': family_history,
            'FAVC': FAVC,
            'FCVC': FCVC,
            'NCP': NCP,
            'CAEC': CAEC,
            'SMOKE': SMOKE,
            'CH2O': CH2O,
            'SCC': SCC,
            'FAF': FAF,
            'TUE': TUE,
            'CALC': CALC,
            'MTRANS': MTRANS
        }

        result = predict_fn(inputs)

        mensagem = result.get("mensagem", "Sem mensagem")
        prob_raw = result.get("probabilidade")

        if prob_raw is None:
            st.error("Erro: probabilidade não encontrada na resposta.")
            st.write("RESULT DEBUG:", result)
            return

        # ✅ Extrai apenas o número
        match = re.search(r"([\d.,]+)", prob_raw)

        if not match:
            st.error(f"Erro: probabilidade inválida → {prob_raw}")
            st.write("RESULT DEBUG:", result)
            return

        prob = float(match.group(1).replace(",", "."))

        # ✅ Exibe na interface
        st.success(mensagem)
        st.metric("Probabilidade (%)", f"{prob:.2f}%")
        st.pyplot(render_risk_chart(prob))

        st.subheader('Recomendações nutricionais')
        recs = recommend_nutrition_profile(inputs)
        for r in recs:
            st.write('- ' + r)

        # salvar no DB se usuário autenticado (médico) ou se paciente quiser
        user_type = st.session_state.get('user_type', 'anon')
        user_name = st.session_state.get('user_name', 'anon')
        save_record(user_type, user_name, inputs, mensagem, prob)
        st.info('Registro salvo no histórico.')

        # gerar PDF
        pdf_bytes = generate_pdf(nome or 'Paciente', inputs, mensagem, prob)
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="relatorio_{nome or "paciente"}.pdf">⬇️ Baixar relatório em PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

# HISTÓRICO DE AVALIAÇÕES
def render_history():
    st.header('Histórico de avaliações')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, timestamp, user_type, user_name, mensagem, probabilidade FROM records ORDER BY id DESC LIMIT 200')
    rows = c.fetchall()
    conn.close()
    if not rows:
        st.write('Nenhum registro encontrado.')
        return
    import pandas as pd
    df = pd.DataFrame(rows, columns=['id', 'timestamp', 'user_type', 'user_name', 'mensagem', 'probabilidade'])
    st.dataframe(df)

    st.markdown('**Exportar como CSV**')
    csv = df.to_csv(index=False).encode('utf-8')
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="historico.csv">⬇️ Baixar histórico (CSV)</a>'
    st.markdown(href, unsafe_allow_html=True)


def render_about():
    st.header('Sobre')
    st.write(f"Este sistema foi desenvolvido para {HOSPITAL_NAME} como protótipo de suporte à triagem clínica.")
    st.write('Funcionalidades: gráfico de risco, geração de PDF, histórico em sqlite, autenticação simples e recomendações nutricionais básicas.')


def render_settings():
    st.header('Configurações')
    dark = st.checkbox('Tema escuro (dark mode)')
    local_css(dark)
    st.write('Paleta atual:')
    st.color_picker('Cor primária', value=PRIMARY_COLOR)
    st.color_picker('Cor de acento', value=ACCENT_COLOR)

# -----------------------------
# MAIN
# -----------------------------

def main():
    st.set_page_config(
        page_title='Predição de Obesidade - Sistema Clínico',
        page_icon='🩺',
        layout='wide'
    )

    model = load_model(
        xgb_model_path
        #r"G:\FIAP-Pos-data-analytics\Pos_Data_Analytics_Curso\Challenges_Fases\Challenger_Fase_4\notebook\random_forest_final.joblib"
    )

    init_db()
    create_logo()

    # Sidebar
    st.sidebar.title('Navegação')
    auth_widget()
    page = st.sidebar.radio('Ir para', ['Home', 'Prever', 'Histórico', 'Sobre', 'Configurações'])

    if 'theme_dark' not in st.session_state:
        st.session_state['theme_dark'] = False

    # Páginas
    if page == 'Home':
        render_home()

    elif page == 'Prever':
        render_predict(
            load_model_fn=None,
            predict_fn=lambda x: predict_from_input(model, x)
        )

    elif page == 'Histórico':
        render_history()

    elif page == 'Sobre':
        render_about()

    elif page == 'Configurações':
        render_settings()

if __name__ == '__main__':
    main()
