"""Página Home do app: apresentação e instruções rápidas."""
import streamlit as st
import shared.utils as utils

# Inicializa variáveis de configuração se não existirem
if "HOSPITAL_NAME" not in st.session_state:
    st.session_state["HOSPITAL_NAME"] = "Hospital Padrão"


def render_home() -> None:
    """Renderiza a página inicial do app (logo, título e instruções)."""
    st.image(utils.create_logo())
    st.title('Bem-vindo ao Sistema de Avaliação Preventiva')
    st.markdown(
        f"""
        **{st.session_state.get('HOSPITAL_NAME', 'Hospital Padrão')}** — Ferramenta de suporte para triagem e acompanhamento do risco de obesidade.

        Este sistema auxilia médicos e equipes multidisciplinares a identificar pacientes com maior risco
        de desenvolver obesidade, sugerindo ações nutricionais e gerando relatórios clínicos.
        """
    )
    st.write('---')
    st.markdown('### Como funciona')
    st.markdown('- Preencha o formulário na aba **Prever**')
    st.markdown('- Receba uma estimativa de risco, recomendações nutricionais e um PDF para impressão')
    st.markdown('- Registre o exame no histórico do paciente (DB local)')

if __name__ == '__main__':
    render_home()