import streamlit.web.cli as stcli
import sys
from dotenv import load_dotenv
import os

load_dotenv()

app = "src/app.py"

def run():
    sys.argv = ["streamlit", "run", app]
    stcli.main()