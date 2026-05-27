import streamlit as st
from dotenv import load_dotenv

load_dotenv()

import os
from workflow import run_workflow
from dashboard import render_dashboard


st.set_page_config(page_title="Contract Review Test Results", layout="wide")

st.markdown("""
<style>
    .header{
        background-color: #2C3E50;
        color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        text-align: center; 
    }
</style>
<div class="header">
    <h1>Contract Review Test Results</h1>
</div>
""", unsafe_allow_html=True)

openai_api_key = os.getenv("OPENAI_API_KEY")    

if not openai_api_key:
    st.error("OpenAI API key not found. Please set the 'OPENAI_API_KEY' enviornment variable.")
    st.stop()

if "results" not in st.session_state:
    st.session_state["results"] = None

assistant_key = st.text_input(
    "Assistant key",
    placeholder="Enter assistant name"
)

if st.button("Run evaluation"):
    with st.spinner("Running GPT evaluation..."):
        st.session_state["results"] = run_workflow(assistant_key=assistant_key)

if st.session_state["results"] is not None:
    render_dashboard(st.session_state["results"])
else:
    st.info("Enter an assistant key, then click Run evaluation.")

