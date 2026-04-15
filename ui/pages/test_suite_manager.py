import ui._pathfix  # noqa
import os
import streamlit as st
import pandas as pd
from ui.state import init_state, get_config


def render():
    init_state()
    config = get_config()
    st.title("📋 Test Suite Manager")
    st.caption("View and manage all test cases. Enable or disable tests before running.")
    st.divider()

    suite_path = config.get("data",{}).get("excel",{}).get(
        "test_suite_path","assets/templates/test_suite.xlsx")
    sheet_name = config.get("data",{}).get("excel",{}).get("suite_sheet","TestSuite")

    col1, col2 = st.columns([5,1])
    suite_path_input = col1.text_input("Excel Test Suite Path", value=suite_path)
    col2.write(""); col2.write("")
    load_btn = col2.button("Load", use_container_width=True)

    if load_btn or "loaded_suite" not in st.session_state:
        if os.path.exists(suite_path_input):
            try:
                from core.test_cases.excel_parser import ExcelParser
                parser = ExcelParser(suite_path_input, sheet_name=sheet_name)
                st.session_state.loaded_suite = parser.parse()
            except Exception as e:
                st.error(f"Failed to load suite: {e}"); return
        else:
            st.warning(f"File not found: `{suite_path_input}`")
            st.info("Run: python assets/templates/create_template.py")
            return

    suite = st.session_state.get("loaded_suite")
    if not suite: return

    m1, m2, m3 = st.columns(3)
    m1.metric("Total",    suite.total)
    m2.metric("Enabled",  suite.enabled_count)
    m3.metric("Disabled", suite.total - suite.enabled_count)
    st.divider()

    bc1, bc2, bc3 = st.columns(3)
    if bc1.button("✅ Enable All",       use_container_width=True):
        for tc in suite.test_cases: tc.enabled = True
        st.rerun()
    if bc2.button("⏸️ Disable All",      use_container_width=True):
        for tc in suite.test_cases: tc.enabled = False
        st.rerun()
    if bc3.button("🔄 Reload from File", use_container_width=True):
        del st.session_state["loaded_suite"]; st.rerun()

    st.divider()
    st.subheader("Test Cases")

    for tc in suite.test_cases:
        with st.expander(
            f"{'✅' if tc.enabled else '⏸️'}  [{tc.test_id}]  {tc.name}  — {tc.step_count} steps",
            expanded=False,
        ):
            ca, cb, cc = st.columns([2,2,1])
            ca.write(f"**ID:** `{tc.test_id}`")
            ca.write(f"**Data Source:** `{tc.data_source}`")
            cb.write(f"**Description:** {tc.description or '—'}")
            new_enabled = cc.toggle("Enabled", value=tc.enabled, key=f"tog_{tc.test_id}")
            if new_enabled != tc.enabled:
                tc.enabled = new_enabled

            if tc.steps:
                steps_df = pd.DataFrame(tc.steps)
                cols = [c for c in ["step_no","keyword","locator","strategy","value","timeout"]
                        if c in steps_df.columns]
                st.dataframe(steps_df[cols], use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Export")
    e1, e2 = st.columns(2)
    enabled_ids = [tc.test_id for tc in suite.test_cases if tc.enabled]
    e1.download_button("⬇️ Export Enabled IDs (txt)",
                        data="\n".join(enabled_ids),
                        file_name="enabled_tests.txt", mime="text/plain",
                        use_container_width=True)
    summary = pd.DataFrame([{
        "TestCaseID": tc.test_id, "TestName": tc.name,
        "Enabled": "YES" if tc.enabled else "NO",
        "Steps": tc.step_count,
    } for tc in suite.test_cases])
    e2.download_button("⬇️ Export Summary (CSV)",
                        data=summary.to_csv(index=False),
                        file_name="suite_summary.csv", mime="text/csv",
                        use_container_width=True)
