import ui._pathfix  # noqa — must be first
import sys
import os
import streamlit as st
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config() -> dict:
    path = os.path.join(ROOT, "config", "config.yaml")
    if os.path.exists(path):
        with open(path) as f:
            return yaml.safe_load(f) or {}
    return {}


def save_config(config: dict) -> None:
    path = os.path.join(ROOT, "config", "config.yaml")
    with open(path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def get_config() -> dict:
    if "kwaf_config" not in st.session_state:
        st.session_state.kwaf_config = load_config()
    return st.session_state.kwaf_config


def init_state() -> None:
    defaults = {
        "kwaf_config":       load_config(),
        "suite_result":      None,
        "last_report_path":  None,
        "run_log":           [],
        "inspected_fields":  [],
        "test_cases":        [],
        "execution_running": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
