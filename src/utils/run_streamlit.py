import streamlit.web.cli as stcli
import sys
from dotenv import load_dotenv
import os

load_dotenv()

app = os.getenv("APP_PATH")

def run():
    sys.argv = ["streamlit", "run", app]
    stcli.main()