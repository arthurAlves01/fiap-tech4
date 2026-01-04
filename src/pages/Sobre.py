"""Página 'Sobre' com informações do projeto."""
import streamlit as st

# Inicializa variáveis de configuração se não existirem
if "HOSPITAL_NAME" not in st.session_state:
    st.session_state["HOSPITAL_NAME"] = "Hospital Padrão"


def render_sobre() -> None:
    st.header('Sobre')
    st.write(f"Este sistema foi desenvolvido para {st.session_state.get('HOSPITAL_NAME', 'Hospital Padrão')} como protótipo de suporte à triagem clínica.")
    st.write('Funcionalidades: gráfico de risco, geração de PDF, histórico em sqlite, autenticação simples e recomendações nutricionais básicas.')

if __name__ == '__main__':
    render_sobre()