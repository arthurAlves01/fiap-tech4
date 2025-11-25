import streamlit as st
import shared.utils as utils

def render_home():
    st.image(utils.create_logo())
    st.title('Bem-vindo ao Sistema de Avaliação Preventiva')
    st.markdown(
        f"""
        **{st.session_state.HOSPITAL_NAME}** — Ferramenta de suporte para triagem e acompanhamento do risco de obesidade.

        Este sistema auxilia médicos e equipes multidisciplinares a identificar pacientes com maior risco
de desenvolver obesidade, sugerindo ações nutricionais e gerando relatórios clínicos.
        """
    )
    st.write('---')
    st.markdown('### Como funciona')
    st.markdown('- Preencha o formulário na aba **Prever**')
    st.markdown('- Receba uma estimativa de risco, recomendações nutricionais e um PDF para impressão')
    st.markdown('- Registre o exame no histórico do paciente (DB local)')

render_home()