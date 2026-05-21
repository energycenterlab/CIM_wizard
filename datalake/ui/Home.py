"""CIM Datalake — entry point.  Run with:  streamlit run Home.py"""
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="CIM Datalake", layout="centered")

st.title("CIM Datalake")
st.caption("Shared spatial dataset repository for the development team.")

st.divider()

st.page_link("pages/Explore_page.py", label="Explore datasets")
st.page_link("pages/Upload_page.py",  label="Upload a dataset")
