import os, sys
import streamlit as st

# Ensure repository root is on sys.path for local imports
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
src_dir = os.path.abspath(os.path.dirname(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Minimal app loader to expose only the required pages in the navigation
from src.pages.Home import render_home
from src.pages.Prever import render_predict
from src.pages.Historico import render_historico
from src.pages.Sobre import render_sobre

st.set_page_config(page_title="App Principal - Obesidade", page_icon="🏥", layout="wide")

menu = ["Home", "Prever", "Historico", "Sobre"]
choice = st.sidebar.selectbox("Navegação", menu, index=0)

if choice == "Home":
    render_home()
elif choice == "Prever":
    render_predict()
elif choice == "Historico":
    render_historico()
elif choice == "Sobre":
    render_sobre()
