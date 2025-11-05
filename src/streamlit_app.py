# streamlit_app.py
import streamlit as st
from src.production_pipeline import load_model, predict_from_input

st.title("🩺 Predição de Obesidade")

model = load_model(r"G:\FIAP-Pos-data-analytics\Pos_Data_Analytics_Curso\Challenges_Fases\Challenger_Fase_4\notebook\xgb_model.joblib")

# Coleta de dados básicos do usuário
# gender = st.selectbox("Gênero", ["Male", "Female"])
# age = st.number_input("Idade", 0, 120)
# height = st.number_input("Altura (m)", 0.5, 2.5)
# weight = st.number_input("Peso (kg)", 0.0, 300.0)

# Coleta de dados de hábitos e estilo de vida
family_history = st.selectbox("Histórico familiar de obesidade?", ["yes", "no"])
FAVC = st.selectbox("Consome alimentos de alta calória?", ["yes", "no"])
FCVC = st.number_input("Frequência consumo verduras (1 = raramente | 2 = às vezes | 3 = sempre)", 0, 3)
NCP = st.number_input("Refeições/dia (1 = 1 ref | 2 = 2 refs | 3 = 3 refs | 4 = mais de 3 refs | )", 1, 4)
CAEC = st.selectbox("Lanche entre refeições", ["no", "Sometimes", "Frequently", "Always"])
SMOKE = st.selectbox("Fuma?", ["yes", "no"])
CH2O = st.number_input("Água por dia (1 < 1L/dia | 2 = 1-2L/dia | 3 > 2L/dia )", 1, 3)
SCC = st.selectbox("Controla calorias?", ["yes", "no"])
FAF = st.number_input("Atividade física (0 = não | 1 = ~1-2x/sem | 2 = ~3-4x/sem | 3 = 5x/sem ou mais|)", 0, 4)
TUE = st.number_input("Uso tecnologia (0 = ~0-2h/dia | 1 = ~3-5h/dia | 2 > 5h/dia |)", 0, 2)
CALC = st.selectbox("Consumo de álcool", ["no", "Sometimes", "Frequently", "Always"])
MTRANS = st.selectbox("Meio de transporte", ["Automobile", "Motorbike", "Public_Transportation", "Bike", "Walking"])

# Botao de predição
if st.button("Prever"):
    user_input = {
        # 'Gender': gender,
        # 'Age': age,
        # 'Height': height,
        # 'Weight': weight,
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

    # Agora recebe dict amigável (mensagem + probabilidade %)
    result = predict_from_input(model, user_input)

    st.subheader("Resultado")
    st.write(result["mensagem"])

    # opcional
    if "probabilidade" in result:
        st.metric("Probabilidade estimada", result["probabilidade"])