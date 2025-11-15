import streamlit as st
from src.production_pipeline import load_model, predict_from_input
from PIL import Image
from pathlib import Path

# Configurando root do projeto
BASE_DIR = Path(__file__).resolve().parent.parent  # sobe dois níveis até o root do projeto

xgb_model_path = BASE_DIR / "notebook" / "xgb_model.joblib"


# ================================
# 📌 CONFIGURAÇÕES DE PÁGINA
# ================================
st.set_page_config(
    page_title="Predição de Obesidade",
    page_icon="🩺",
    layout="centered",
)

# ================================
# 📌 HEADER DA APLICAÇÃO
# ================================

# Imagem (adicione sua imagem local)
try:
    banner = Image.open("hospital_image.jpg")
    st.image(banner, use_column_width=True)
except:
    st.write("")  # Caso não tenha imagem

st.markdown(
    """
    <h1 style='text-align: center; color:#0A4D68;'>
        🩺 Avaliação de Risco de Obesidade
    </h1>
    <p style='text-align: center; font-size:18px; color:#333;'>
        Sistema de predição de risco baseado em hábitos, estilo de vida e fatores familiares.
        <br>
        Desenvolvido para auxiliar profissionais da saúde na análise preventiva.
    </p>
    """,
    unsafe_allow_html=True,
)

# ================================
# 📌 Carregar modelo
# ================================
model = load_model(
    xgb_model_path
)

st.write("---")

st.markdown(
    """
    <h3 style='color:#0A4D68;'>
        📋 Preencha os dados do paciente
    </h3>
    """,
    unsafe_allow_html=True
)

# ================================
# 📌 FORMULÁRIO
# ================================
with st.form("form_predict"):
    
    col1, col2 = st.columns(2)

    with col1:
        family_history = st.selectbox("Histórico familiar de obesidade", ["yes", "no"])
        FAVC = st.selectbox("Consome alimentos de alta caloria", ["yes", "no"])
        FCVC = st.number_input(
            "Frequência de consumo de verduras (1 a 3)",
            min_value=1, max_value=3, step=1
        )
        NCP = st.number_input(
            "Refeições por dia (1 a 4)",
            min_value=1, max_value=4, step=1
        )
        CAEC = st.selectbox("Lanches entre refeições", ["no", "Sometimes", "Frequently", "Always"])

    with col2:
        SMOKE = st.selectbox("Fuma?", ["yes", "no"])
        CH2O = st.number_input("Hidratação diária (1 a 3)", min_value=1, max_value=3)
        SCC = st.selectbox("Controla calorias?", ["yes", "no"])
        FAF = st.number_input("Atividade física semanal (0 a 3)", min_value=0, max_value=3)
        TUE = st.number_input("Uso de tecnologia (0 a 2)", min_value=0, max_value=2)

    CALC = st.selectbox("Consumo de álcool", ["no", "Sometimes", "Frequently", "Always"])
    MTRANS = st.selectbox("Meio de transporte principal", 
                          ["Automobile", "Motorbike", "Public_Transportation", "Bike", "Walking"])

    submitted = st.form_submit_button("🔍 Analisar")

# ================================
# 📌 PREDIÇÃO
# ================================
if submitted:
    user_input = {
        "family_history": family_history,
        "FAVC": FAVC,
        "FCVC": FCVC,
        "NCP": NCP,
        "CAEC": CAEC,
        "SMOKE": SMOKE,
        "CH2O": CH2O,
        "SCC": SCC,
        "FAF": FAF,
        "TUE": TUE,
        "CALC": CALC,
        "MTRANS": MTRANS
    }

    result = predict_from_input(model, user_input)

    risk_msg = result.get("mensagem", "")
    prob = result.get("probabilidade", None)

    st.write("---")
    st.markdown(
        """
        <h3 style='color:#0A4D68;'>📊 Resultado da Análise</h3>
        """,
        unsafe_allow_html=True
    )

    st.success(risk_msg)

    if prob:
        st.metric("Probabilidade Estimada de Obesidade", f"{prob}")

    st.info(
        """
        ✅ *Atenção:*  
        Este resultado é uma estimativa baseada nos dados preenchidos.  
        Ele deve ser analisado em conjunto com avaliação clínica profissional.
        """
    )

    st.write("---")

    st.markdown(
        """
        <p style='font-size:16px; color:#333'>
        Este sistema foi desenvolvido para apoiar médicos e equipes hospitalares no monitoramento da saúde e 
        tomada de decisão preventiva, direcionando pacientes para acompanhamento nutricional, psicológico 
        e atividades físicas, quando necessário.
        </p>
        """,
        unsafe_allow_html=True
    )

# ================================
# ✅ FOOTER
# ================================
st.write("---")
st.markdown(
    """
    <center>
    <p style="color:gray;">
    © 2025 — Sistema de Avaliação Preventiva de Obesidade<br>
    Desenvolvido com foco em saúde, tecnologia e inovação.
    </p>
    </center>
    """,
    unsafe_allow_html=True
)
