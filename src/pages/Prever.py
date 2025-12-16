import os
import sys
import streamlit as st
import base64
import re
import glob

# Inicializa variáveis de configuração se não existirem
if "DB_PATH" not in st.session_state:
    st.session_state["DB_PATH"] = "records.db"
if "HOSPITAL_NAME" not in st.session_state:
    st.session_state["HOSPITAL_NAME"] = "Hospital Padrão"
if "LOGO_PATH" not in st.session_state:
    st.session_state["LOGO_PATH"] = "logo.png"
if "FONT_PATH" not in st.session_state:
    st.session_state["FONT_PATH"] = "DejaVuSans.ttf"
if "PRIMARY_COLOR" not in st.session_state:
    st.session_state["PRIMARY_COLOR"] = (25, 118, 210)
if "ACCENT_COLOR" not in st.session_state:
    st.session_state["ACCENT_COLOR"] = (255, 152, 0)
if "FIELD_MAPPING" not in st.session_state:
    st.session_state["FIELD_MAPPING"] = {}
if "CATEGORY_TRANSLATION" not in st.session_state:
    st.session_state["CATEGORY_TRANSLATION"] = {}
if "EXPLAIN_NUMERIC" not in st.session_state:
    st.session_state["EXPLAIN_NUMERIC"] = {}

# Traduções para exibição no formulário e para o PDF
if "CATEGORY_TRANSLATION" not in st.session_state:
    st.session_state["CATEGORY_TRANSLATION"] = {
        'yes': 'Sim',
        'no': 'Não',
        'Sometimes': 'Às vezes',
        'sometimes': 'Às vezes',
        'Frequently': 'Frequentemente',
        'frequently': 'Frequentemente',
        'Always': 'Sempre',
        'always': 'Sempre',
        'never': 'Nunca',
        'Never': 'Nunca',
        'Automobile': 'Automóvel',
        'Motorbike': 'Moto',
        'Public_Transportation': 'Transporte Público',
        'Bike': 'Bicicleta',
        'Walking': 'A pé'
    }

if "FIELD_NAME_MAP" not in st.session_state:
    st.session_state["FIELD_NAME_MAP"] = {
        'family_history': 'Histórico familiar de obesidade',
        'FAVC': 'Consome alimentos de alta caloria',
        'FCVC': 'Consumo de verduras',
        'NCP': 'Refeições por dia',
        'CAEC': 'Lanches entre refeições',
        'SMOKE': 'Fuma',
        'CH2O': 'Ingestão de água',
        'SCC': 'Controla calorias',
        'FAF': 'Atividade física',
        'TUE': 'Uso de tecnologia',
        'CALC': 'Consumo de álcool',
        'MTRANS': 'Meio de transporte'
    }

if "EXPLAIN_NUMERIC" not in st.session_state or not st.session_state["EXPLAIN_NUMERIC"]:
    st.session_state["EXPLAIN_NUMERIC"] = {
        'FCVC': {1: 'Raramente', 2: 'Ocasionalmente', 3: 'Frequentemente'},
        'CH2O': {1: '<1L/dia', 2: '1-2L/dia', 3: '>2L/dia'},
        'NCP': {1: '1 refeição', 2: '2 refeições', 3: '3 refeições', 4: '4 refeições'},
        'FAF': {0: 'Inativo', 1: 'Baixa atividade', 2: 'Atividade moderada', 3: 'Atividade intensa'},
        'TUE': {0: 'Pouco uso', 1: 'Moderado', 2: 'Alto uso'}
    }

# Tenta importar o pacote `src`; se falhar, adiciona o root do repo ao `sys.path` e tenta novamente.
try:
    from src.models.production_pipeline import predict_from_input, load_model
except ModuleNotFoundError:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.models.production_pipeline import predict_from_input, load_model

import utils.utils as utils
import utils.plots as plots
import utils.connection as connection

# Função para carregar modelo com cache
@st.cache_resource
def load_ml_model():
    """Carrega o modelo XGBoost ou Random Forest disponível em src/models/"""
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    model_files = sorted(glob.glob(os.path.join(models_dir, "*.joblib")))
    
    if not model_files:
        st.error("❌ Nenhum modelo encontrado em `src/models/`. Por favor, treine e salve um modelo.")
        return None
    
    # Preferir XGBoost se disponível, senão usar Random Forest
    xgb_files = [f for f in model_files if 'xgb' in f.lower()]
    model_path = xgb_files[0] if xgb_files else model_files[0]
    
    try:
        model = load_model(model_path)
        return model
    except Exception as e:
        st.error(f"❌ Erro ao carregar modelo: {e}")
        return None

def render_predict(load_model_fn=None, predict_fn=None):
    st.header('Formulário de triagem')
    # If no predictor function provided, load the model from default location
    if predict_fn is None:
        try:
            model = load_ml_model()
            if model is not None:
                predict_fn = lambda x: predict_from_input(model, x)
        except Exception:
            predict_fn = None
    with st.form('predict_form'):
        
        col1, col2 = st.columns(2)
    
        with col1:
            nome = st.text_input('Nome do paciente', value="")
            # Mostrar opções em português, converter para valores esperados pelo modelo
            family_history_display = st.radio('Histórico familiar de obesidade', ['Sim', 'Não'])
            family_history = 'yes' if family_history_display == 'Sim' else 'no'
            FAVC_display = st.radio('Consome alimentos de alta caloria', ['Sim', 'Não'])
            FAVC = 'yes' if FAVC_display == 'Sim' else 'no'
            FCVC = st.number_input('Frequência consumo verduras (1=raramente,3=sempre)', min_value=1, max_value=3, value=3)
            NCP = st.number_input('Refeições por dia (1-4)', min_value=1, max_value=4, value=3)
            CAEC_display = st.selectbox('Lanche entre refeições', ['Nunca', 'Às vezes', 'Frequentemente', 'Sempre'])
            CAEC_MAP = { 'Nunca': 'no', 'Às vezes': 'Sometimes', 'Frequentemente': 'Frequently', 'Sempre': 'Always'}
            CAEC = CAEC_MAP.get(CAEC_display, 'no')

        with col2:
            SMOKE_display = st.radio('Fuma?', ['Sim', 'Não'])
            SMOKE = 'yes' if SMOKE_display == 'Sim' else 'no'
            CH2O = st.number_input('Água por dia (1<1L,2=1-2L,3>2L)', min_value=1, max_value=3, value=2)
            SCC_display = st.radio('Controla calorias?', ['Sim', 'Não'])
            SCC = 'yes' if SCC_display == 'Sim' else 'no'
            FAF = st.number_input('Atividade física (0-3)', min_value=0, max_value=3, value=1)
            TUE = st.number_input('Uso tecnologia (0-2)', min_value=0, max_value=2, value=1)

        col3, col4 = st.columns(2)
        with col3:
            CALC_display = st.selectbox('Consumo de álcool', ['Nunca', 'Às vezes', 'Frequentemente', 'Sempre'])
            CALC_MAP = {'Nunca':'never', 'Às vezes':'sometimes', 'Frequentemente':'frequently', 'Sempre':'always', 'no':'never'}
            CALC = CALC_MAP.get(CALC_display, 'never')
        with col4:
            MTRANS_display = st.selectbox('Meio de transporte', ['Automóvel','Moto','Transporte Público','Bicicleta','A pé'])
            MTRANS_MAP = {
                'Automóvel': 'Automobile',
                'Moto': 'Motorbike',
                'Transporte Público': 'Public_Transportation',
                'Bicicleta': 'Bike',
                'A pé': 'Walking'
            }
            MTRANS = MTRANS_MAP.get(MTRANS_display, 'Automobile')

        submitted = st.form_submit_button('🔍 Analisar paciente')

    if submitted:
        
        if predict_fn is None:
            st.error("⚠ Nenhuma função de predição fornecida.")
            return
    
        if not nome.strip():
            st.error("O campo Nome é obrigatório.")
        else:
            st.success(f"Nome recebido: {nome}")

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

        # ✅ Exibe na interface com rótulos mais claros
        # Interpretação binária (Sim/Não) e classificação de risco por faixas
        previsao_binaria = "Sim" if prob >= 50 else "Não"
        if prob >= 60:
            risco = "Alto"
            st.error(f"🔴 Resultado: {previsao_binaria} — Risco {risco} de obesidade ({prob:.2f}%)")
        elif prob >= 30:
            risco = "Moderado"
            st.warning(f"🟠 Resultado: {previsao_binaria} — Risco {risco} de obesidade ({prob:.2f}%)")
        else:
            risco = "Baixo"
            st.success(f"🟢 Resultado: {previsao_binaria} — Risco {risco} de obesidade ({prob:.2f}%)")

        st.metric("Probabilidade (%)", f"{prob:.2f}%")
        st.pyplot(plots.render_risk_chart(prob))

        st.subheader('Recomendações nutricionais')
        recs = utils.recommend_nutrition_profile(inputs)
        for r in recs:
            st.write('- ' + r)

        # salvar no DB se usuário autenticado (médico) ou se paciente quiser
        user_type = st.session_state.get('user_type', 'anon')
        user_name = st.session_state.get('user_name', 'anon')
        connection.save_record(user_type, user_name, inputs, mensagem, prob)
        st.info('Registro salvo no histórico.')

        # gerar PDF
        pdf_bytes = utils.generate_pdf(nome or 'Paciente', inputs, mensagem, prob)
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="relatorio_{nome or "paciente"}.pdf">⬇️ Baixar relatório em PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

# Carregar modelo e chamar render_predict
if __name__ == '__main__':
    model = load_ml_model()
    if model is not None:
        render_predict(
            load_model_fn=load_ml_model,
            predict_fn=lambda x: predict_from_input(model, x)
        )
    else:
        st.error("❌ Não é possível fazer predições sem um modelo carregado.")