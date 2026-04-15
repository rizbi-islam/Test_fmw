import ui._pathfix  # noqa
import os
import datetime
import streamlit as st
from ui.state import init_state, get_config


def render():
    init_state()
    config = get_config()

    st.title("📊 Reports")
    st.caption("Browse and download all generated test reports.")
    st.divider()

    report_dir = config.get("reports",{}).get("output_dir","reports/output")
    os.makedirs(report_dir, exist_ok=True)

    # ── Last Run Summary ──────────────────────────────────────
    suite_result = st.session_state.get("suite_result")
    if suite_result:
        st.subheader("Last Run Summary")
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Total",   suite_result.total)
        m2.metric("Passed",  suite_result.passed)
        m3.metric("Failed",  suite_result.failed)
        m4.metric("Skipped", suite_result.skipped)

        if suite_result.results:
            st.subheader("Test Case Results")
            for result in suite_result.results:
                icon = "✅" if result.status=="PASS" else ("❌" if result.status=="FAIL" else "⚠️")
                with st.expander(
                    f"{icon}  [{result.test_id}]  {result.test_name}  — {result.elapsed_seconds}s",
                    expanded=(result.status == "FAIL"),
                ):
                    c1,c2,c3 = st.columns(3)
                    c1.write(f"**Status:** {result.status}")
                    c2.write(f"**Steps:** {result.total_steps}")
                    c3.write(f"**Duration:** {result.elapsed_seconds}s")
                    if result.step_results:
                        import pandas as pd
                        step_data = []
                        for s in result.step_results:
                            d = s.to_dict() if hasattr(s,"to_dict") else vars(s)
                            step_data.append({
                                "Step":    d.get("step_no",""),
                                "Keyword": d.get("keyword",""),
                                "Status":  d.get("status",""),
                                "Message": d.get("message",""),
                                "ms":      d.get("elapsed_ms",""),
                            })
                        st.dataframe(pd.DataFrame(step_data), use_container_width=True, hide_index=True)
                    if result.error_message:
                        st.error(f"Error: {result.error_message}")
        st.divider()

    # ── Report Files ──────────────────────────────────────────
    st.subheader("Saved Reports")
    report_files = sorted(
        [f for f in os.listdir(report_dir) if f.endswith(".html")], reverse=True)

    if not report_files:
        st.info("No reports yet. Run your test suite to generate reports.")
        return

    st.write(f"Found **{len(report_files)}** report(s) in `{report_dir}`")
    selected = st.selectbox("Select Report", report_files, index=0)

    if selected:
        report_path = os.path.join(report_dir, selected)
        with open(report_path,"r",encoding="utf-8") as f:
            html_content = f.read()

        dl1,dl2 = st.columns(2)
        dl1.download_button(
            label=f"⬇️ Download {selected}",
            data=html_content, file_name=selected,
            mime="text/html", use_container_width=True)

        stat     = os.stat(report_path)
        modified = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        dl2.info(f"**Size:** {stat.st_size//1024} KB\n\n**Modified:** {modified}")

        st.subheader("Preview")
        st.components.v1.html(html_content, height=600, scrolling=True)

    st.divider()
    st.subheader("Manage Reports")
    if st.button("🗑️ Delete All Reports", type="secondary"):
        if st.checkbox("Confirm — delete all reports permanently"):
            for f in report_files:
                try: os.remove(os.path.join(report_dir, f))
                except Exception: pass
            st.success("All reports deleted.")
            st.rerun()
