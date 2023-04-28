import streamlit as st
from Home import BEAVER_SDK

st.title("Infrastructure")

tabs = st.tabs(["Message buses", "Stream processors", "Job runner"])

with tabs[0]:
    st.json(BEAVER_SDK.message_bus.list())

with tabs[1]:
    st.json(BEAVER_SDK.stream_processor.list())

with tabs[2]:
    st.json(BEAVER_SDK.job_runner.list())
