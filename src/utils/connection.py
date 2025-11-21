from datetime import datetime, timezone
import sqlite3
import streamlit as st

def save_record(user_type, user_name, inputs, mensagem, probabilidade, path=st.session_state.DB_PATH):
    timestamp_utc = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(path)
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO records 
        (timestamp, user_type, user_name, inputs, mensagem, probabilidade) 
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (timestamp_utc, user_type, user_name, str(inputs), mensagem, probabilidade),
    )

    conn.commit()
    conn.close()