import streamlit as st
import sqlite3
import base64

def render_history():
    st.header('Histórico de avaliações')
    conn = sqlite3.connect(st.session_state.DB_PATH)
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

render_history()