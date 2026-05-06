"""
CIM Datalake — Home / landing page.
Run with:  streamlit run Home.py
"""
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="CIM Datalake",
    page_icon="🗄️",
    layout="wide",
)

st.title("🗄️ CIM Datalake")
st.subheader("Shared Spatial Dataset Repository")

st.markdown(
    "A lightweight datalake for sharing and discovering geospatial datasets across the team. "
    "Use the **sidebar** to navigate between the Upload and Explore pages."
)

col_upload, col_explore = st.columns(2, gap="large")

with col_upload:
    st.markdown(
        """
        <div style="border:1px solid #ddd;border-radius:8px;padding:20px;height:160px;">
        <h4>📤 Upload</h4>
        Upload any JSON / GeoJSON dataset along with its metadata:<br>
        &nbsp;• Name, description, tags<br>
        &nbsp;• Spatial footprint (drawn on map, EPSG:4326)<br>
        &nbsp;• Temporal coverage (start → end date)
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_explore:
    st.markdown(
        """
        <div style="border:1px solid #ddd;border-radius:8px;padding:20px;height:160px;">
        <h4>📥 Explore & Download</h4>
        Discover datasets interactively:<br>
        &nbsp;• Filter by tags and temporal range<br>
        &nbsp;• Draw a study-area polygon on the map<br>
        &nbsp;• See intersecting dataset footprints<br>
        &nbsp;• Download matching datasets as JSON
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()
st.markdown("### Database Connection")

from db import init_db  # noqa: E402

try:
    init_db()
    st.success("✅ Connected to PostGIS — schema is ready.")
except ValueError as exc:
    st.warning(f"⚠️ {exc}")
    st.markdown("**Set the connection string in `.streamlit/secrets.toml`:**")
    st.code(
        '[secrets]\nDATABASE_URL = "postgresql://user:password@host:5432/dbname"',
        language="toml",
    )
except Exception as exc:
    st.error(f"❌ Database error: {exc}")
