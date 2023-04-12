import streamlit as st

st.title("Infrastructure")

tabs = st.tabs(["Message buses", "Stream processors", "Job runner"])

with tabs[0]:
    st.text("hey")
