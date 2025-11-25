from datetime import datetime, timezone
import sqlite3
import streamlit as st

# -----------------------------
# UTIL: inicializar DB
# -----------------------------


# Criar tabela se não existir no sqlite
def init_db(path=st.session_state.DB_PATH):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_type TEXT,
            user_name TEXT,
            inputs TEXT,
            mensagem TEXT,
            probabilidade REAL
        )
        """
    )
    conn.commit()
    conn.close()

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