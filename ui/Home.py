import os
import streamlit as st

BEAVER_API_HOST = os.environ["BEAVER_API_HOST"]

st.set_page_config(layout="wide", page_icon="🦫", page_title="Beaver")
st.title("Beaver")

st.markdown(
    f"""
    - **API is running at {BEAVER_API_HOST}**
    - [**API documentation**]({BEAVER_API_HOST}/docs)
"""
)
