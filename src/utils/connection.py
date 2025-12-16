from datetime import datetime, timezone
import sqlite3
import streamlit as st
import os


def init_db(db_path: str) -> None:
    """Initialize the database and create the records table if it doesn't exist."""
    try:
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                user_type TEXT,
                user_name TEXT,
                inputs TEXT,
                mensagem TEXT,
                probabilidade REAL
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        st.warning(f"Erro ao inicializar DB: {e}")


def save_record(user_type, user_name, inputs, mensagem, probabilidade, path=None):
    # Inicializar caminho padrão do banco se não fornecido
    if path is None:
        path = st.session_state.get("DB_PATH", "records.db")
    
    timestamp_utc = datetime.now(timezone.utc).isoformat()

    try:
        # Ensure table exists before inserting
        init_db(path)
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
    except Exception as e:
        # Se não conseguir salvar, apenas registra no log
        st.warning(f"Aviso: Não foi possível salvar registro no banco: {e}")