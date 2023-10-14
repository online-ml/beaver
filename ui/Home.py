import os
import urllib.parse
import beaver_sdk
import streamlit as st


BEAVER_HOST = os.environ["BEAVER_HOST"]
BEAVER_SDK = beaver_sdk.Instance(urllib.parse.urljoin(BEAVER_HOST, ":8000"))

if __name__ == "__main__":
    st.set_page_config(layout="wide", page_icon="🦫", page_title="Beaver")
    st.title("Beaver")

    st.markdown(
        f"""
        - API {urllib.parse.urljoin(BEAVER_HOST, ':8000/api')}
        - API documentation {urllib.parse.urljoin(BEAVER_HOST, ':8000/api/docs')}
        - rq dashboard {urllib.parse.urljoin(BEAVER_HOST, ':9181')}
    """
    )
