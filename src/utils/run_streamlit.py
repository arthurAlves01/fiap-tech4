"""Helper de CLI para executar o app Streamlit programaticamente (conveniência para desenvolvimento)."""
import sys
from dotenv import load_dotenv
import streamlit.web.cli as stcli

load_dotenv()

app = "src/app.py"

def run() -> None:
    """Inicia o Streamlit programaticamente (altera `sys.argv`)."""
    sys.argv = ["streamlit", "run", app]
    stcli.main()