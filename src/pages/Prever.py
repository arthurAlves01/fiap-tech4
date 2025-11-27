import streamlit as st
from src.models.production_pipeline import predict_from_input, load_model
import shared.utils as utils
import shared.plots as plots
import shared.connection as connection
import base64
import re

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

        col1, col2 = st.columns(2)
        with col1:
            st.pyplot(plots.render_risk_chart(prob))

        st.subheader('Recomendações nutricionais')
        recs = utils.recommend_nutrition_profile(inputs)
        for r in recs:
            st.write('- ' + r)

        # salvar no DB se usuário autenticado (médico) ou se paciente quiser
        user_type = st.session_state.get('user_type', 'anon')
        user_name = st.session_state.get('user_name', 'anon')
        connection.save_record(user_type, user_name, inputs, mensagem, prob, st.session_state.DB_PATH)
        st.info('Registro salvo no histórico.')

        # gerar PDF
        pdf_bytes = utils.generate_pdf(nome or 'Paciente', inputs, mensagem, prob)
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="relatorio_{nome or "paciente"}.pdf">⬇️ Baixar relatório em PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

render_predict(
    load_model_fn=None,
    predict_fn=lambda x: predict_from_input(st.session_state.model, x)
)