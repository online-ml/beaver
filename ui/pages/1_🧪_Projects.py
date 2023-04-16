import streamlit as st


project = st.sidebar.radio("Project", ["Phishing", "Taxis"])

st.title(project)

tabs = st.tabs(["Overview", "Experiments"])

with tabs[0]:
    st.text("hey")
