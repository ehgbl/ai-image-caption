import os, sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st
from streamlit_option_menu import option_menu


from src.app import run_upload_page  

st.set_page_config(page_title="Image Caption", page_icon="📸", layout="wide")

with st.sidebar:
    choice = option_menu(
        "📸 Alt-Text Express",
        ["Home", "Upload", "Settings"],
        icons=["house", "cloud-upload", "gear"],
        default_index=1,
    )

if choice == "Home":
    st.title("Welcome to Alt-Text Express!")
    st.markdown("Fast, Accessible Photo Descriptions")
    st.write("Use the sidebar to navigate.")
elif choice == "Upload":
    run_upload_page()   
else:
    st.title("Settings")
    st.write("Re-enter API key, choose defaults, etc.")
