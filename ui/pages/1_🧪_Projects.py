import streamlit as st
from Home import BEAVER_SDK


projects = BEAVER_SDK.project.list()
project_name = st.sidebar.radio("Project", [p["name"] for p in projects])
project = next(p for p in projects if p["name"] == project_name)

st.title(project_name)

tabs = st.tabs(["Overview", "Experiments"])

with tabs[0]:
    st.json(project)

with tabs[1]:
    project_state = BEAVER_SDK.project(project_name).state()
    st.json(project_state["experiments"])
