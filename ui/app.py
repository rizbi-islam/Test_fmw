"""
KWAF — Streamlit UI Dashboard
Entry point: streamlit run ui/app.py
"""
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.getcwd() != ROOT:
    os.chdir(ROOT)

import streamlit as st

st.set_page_config(
    page_title="KWAF — Automation Framework",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("🧪 KWAF")
st.sidebar.caption("Keyword-driven Web Automation Framework")
st.sidebar.divider()

PAGES = [
    "🏠  Dashboard",
    "🔍  Site Inspector",
    "📋  Test Suite Manager",
    "⚙️  Run Configuration",
    "▶️  Execute Tests",
    "📊  Reports",
]

if "page" not in st.session_state:
    st.session_state.page = PAGES[0]

for label in PAGES:
    is_active = st.session_state.page == label
    if st.sidebar.button(
        label,
        use_container_width=True,
        type="primary" if is_active else "secondary",
        key=f"nav_{label}",
    ):
        st.session_state.page = label
        st.rerun()

st.sidebar.divider()
st.sidebar.caption("Phase 3 — UI Layer")

page = st.session_state.page

if page == PAGES[0]:
    from ui.pages import dashboard as pg
elif page == PAGES[1]:
    from ui.pages import site_inspector as pg
elif page == PAGES[2]:
    from ui.pages import test_suite_manager as pg
elif page == PAGES[3]:
    from ui.pages import run_config as pg
elif page == PAGES[4]:
    from ui.pages import execute as pg
elif page == PAGES[5]:
    from ui.pages import reports as pg
else:
    from ui.pages import dashboard as pg

pg.render()
