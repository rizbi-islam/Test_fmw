import ui._pathfix  # noqa — path fix must be first
import os
import streamlit as st
from ui.state import init_state, get_config


def render():
    init_state()
    config = get_config()

    st.title("🧪 KWAF Dashboard")
    st.caption("Keyword-driven Web Automation Framework")
    st.divider()

    suite_path = config.get("data", {}).get("excel", {}).get(
        "test_suite_path", "assets/templates/test_suite.xlsx"
    )

    total_tests   = 0
    enabled_tests = 0
    reports       = []

    if os.path.exists(suite_path):
        try:
            from core.test_cases.excel_parser import ExcelParser
            parser = ExcelParser(
                suite_path,
                sheet_name=config.get("data", {}).get("excel", {}).get("suite_sheet", "TestSuite")
            )
            suite         = parser.parse()
            total_tests   = suite.total
            enabled_tests = suite.enabled_count
        except Exception:
            pass

    report_dir = config.get("reports", {}).get("output_dir", "reports/output")
    if os.path.exists(report_dir):
        reports = sorted(
            [f for f in os.listdir(report_dir) if f.endswith(".html")],
            reverse=True
        )

    # ── Metric Cards ──────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Tests",   total_tests)
    c2.metric("Enabled Tests", enabled_tests)
    c3.metric("Disabled",      total_tests - enabled_tests)
    c4.metric("Reports",       len(reports))
    st.divider()

    # ── Framework Status ──────────────────────────────────────
    st.subheader("Framework Status")
    checks = {
        "Test Suite (Excel)":    os.path.exists(suite_path),
        "Config File":           os.path.exists("config/config.yaml"),
        "Screenshots Directory": os.path.exists("assets/screenshots"),
        "Reports Directory":     os.path.exists(report_dir),
        "OTP Layer":             os.path.exists("core/otp/otp_factory.py"),
        "CAPTCHA Layer":         os.path.exists("core/captcha/captcha_factory.py"),
    }
    col1, col2 = st.columns(2)
    for i, (name, ok) in enumerate(checks.items()):
        col = col1 if i % 2 == 0 else col2
        col.write(f"{'✅' if ok else '❌'}  {name}")
    st.divider()

    # ── Active Config Summary ─────────────────────────────────
    st.subheader("Active Configuration")
    ca, cb, cc = st.columns(3)
    ca.info(
        f"**Driver:** {config.get('driver',{}).get('default','selenium').upper()}\n\n"
        f"**Browser:** {config.get('driver',{}).get('browser','chrome').upper()}\n\n"
        f"**Headless:** {config.get('driver',{}).get('headless', False)}"
    )
    cb.info(
        f"**Data:** {config.get('data',{}).get('default_provider','excel').upper()}\n\n"
        f"**OTP:** {config.get('otp',{}).get('default','mock').upper()}\n\n"
        f"**CAPTCHA:** {config.get('captcha',{}).get('default','bypass').upper()}"
    )
    cc.info(
        f"**Execution:** {config.get('execution',{}).get('mode','sequential').upper()}\n\n"
        f"**Retry:** {config.get('execution',{}).get('retry_on_failure',1)}x\n\n"
        f"**Env:** {config.get('environment',{}).get('name','local').upper()}"
    )
    st.divider()

    # ── Quick Actions ─────────────────────────────────────────
    st.subheader("Quick Actions")
    qa1, qa2, qa3 = st.columns(3)
    if qa1.button("🔍 Inspect a Site",  use_container_width=True):
        st.session_state.page = "🔍  Site Inspector"
        st.rerun()
    if qa2.button("▶️ Run Tests Now",    use_container_width=True):
        st.session_state.page = "▶️  Execute Tests"
        st.rerun()
    if qa3.button("📊 View Last Report", use_container_width=True):
        st.session_state.page = "📊  Reports"
        st.rerun()

    # ── Last Report Download ──────────────────────────────────
    if reports:
        st.divider()
        last = reports[0]
        st.success(f"Last report: `{last}`")
        with open(os.path.join(report_dir, last), "r", encoding="utf-8") as f:
            html_content = f.read()
        st.download_button(
            label="⬇️ Download Last Report",
            data=html_content,
            file_name=last,
            mime="text/html",
            use_container_width=True,
        )
