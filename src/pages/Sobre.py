import streamlit as st

st.header('Sobre')
st.write(f"Este sistema foi desenvolvido para {st.session_state.nome_hospital} como protótipo de suporte à triagem clínica.")
st.write('Funcionalidades: gráfico de risco, geração de PDF, histórico em sqlite, autenticação simples e recomendações nutricionais básicas.')