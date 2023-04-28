import os
import streamlit as st
import beaver_sdk

BEAVER_API_HOST = os.environ["BEAVER_API_HOST"]
BEAVER_SDK = beaver_sdk.Instance(BEAVER_API_HOST)

if __name__ == "__main__":

    st.set_page_config(layout="wide", page_icon="🦫", page_title="Beaver")
    st.title("Beaver")

    st.markdown(
        f"""
        - **API is running at {BEAVER_API_HOST}**
        - [**API documentation**]({BEAVER_API_HOST}/docs)
    """
    )
