# streamlit_app.py
import streamlit as st
from src.production_pipeline import load_model, predict_from_input

st.title("🩺 Predição de Obesidade")

model = load_model(r"G:\FIAP-Pos-data-analytics\Pos_Data_Analytics_Curso\Challenges_Fases\Challenger_Fase_4\notebook\xgb_model.joblib")

# Campos do usuário
gender = st.selectbox("Gênero", ["Male", "Female"])
family_history = st.selectbox("Histórico familiar de obesidade?", ["yes", "no"])
FAVC = st.selectbox("Consome alimentos muito calóricos?", ["yes", "no"])
CAEC = st.selectbox("Lanche entre refeições", ["no", "Sometimes", "Frequently", "Always"])
SMOKE = st.selectbox("Fuma?", ["yes", "no"])
SCC = st.selectbox("Controla calorias?", ["yes", "no"])
CALC = st.selectbox("Consumo de álcool", ["no", "Sometimes", "Frequently", "Always"])
MTRANS = st.selectbox("Meio de transporte", ["Automobile", "Motorbike", "Public_Transportation", "Bike", "Walking"])

age = st.number_input("Idade", 0, 110)
height = st.number_input("Altura (m)", 0.5, 2.5)
weight = st.number_input("Peso (kg)", 0.0, 300.0)
FCVC = st.number_input("Frequência consumo verduras (0-3)", 0, 3)
NCP = st.number_input("Refeições/dia", 1, 10)
CH2O = st.number_input("Água por dia", 0.0, 10.0)
FAF = st.number_input("Atividade física (0-4)", 0, 4)
TUE = st.number_input("Uso tecnologia (0-2)", 0, 2)

if st.button("Prever"):
    user_input = {
        'Gender': gender,
        'Age': age,
        'Height': height,
        'Weight': weight,
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