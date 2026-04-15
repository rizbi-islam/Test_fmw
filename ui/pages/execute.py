import ui._pathfix  # noqa
import os
import streamlit as st
from ui.state import init_state, get_config


def render():
    init_state()
    config = get_config()

    st.title("▶️ Execute Tests")
    st.caption("Run your test suite and watch live execution logs.")
    st.divider()

    suite_path = config.get("data",{}).get("excel",{}).get(
        "test_suite_path","assets/templates/test_suite.xlsx")
    sheet_name = config.get("data",{}).get("excel",{}).get("suite_sheet","TestSuite")

    st.subheader("Pre-Run Settings")
    c1,c2,c3,c4 = st.columns(4)
    c1.info(f"**Driver**\n\n{config.get('driver',{}).get('default','selenium').upper()}")
    c2.info(f"**Browser**\n\n{config.get('driver',{}).get('browser','chrome').upper()}")
    c3.info(f"**Mode**\n\n{config.get('execution',{}).get('mode','sequential').upper()}")
    c4.info(f"**OTP**\n\n{config.get('otp',{}).get('default','mock').upper()}")
    st.divider()

    st.subheader("Select Tests to Run")
    if not os.path.exists(suite_path):
        st.warning(f"Suite not found: `{suite_path}`"); return

    try:
        from core.test_cases.excel_parser import ExcelParser
        parser = ExcelParser(suite_path, sheet_name=sheet_name)
        suite  = parser.parse()
    except Exception as e:
        st.error(f"Failed to load suite: {e}"); return

    run_mode = st.radio("Run Mode", ["All Enabled Tests","Select Specific Tests"], horizontal=True)
    selected_ids = []
    if run_mode == "Select Specific Tests":
        all_ids = [tc.test_id for tc in suite.test_cases]
        selected_ids = st.multiselect(
            "Choose Test Cases", options=all_ids,
            default=[tc.test_id for tc in suite.test_cases if tc.enabled])

    headless_run = st.checkbox("Run Headless",
                                value=config.get("driver",{}).get("headless",False))
    st.divider()

    if st.button("▶️ Start Execution", use_container_width=True, type="primary",
                  disabled=st.session_state.get("execution_running", False)):

        test_cases = suite.enabled_tests if run_mode == "All Enabled Tests" else \
                     [tc for tc in suite.test_cases if tc.test_id in selected_ids]

        if not test_cases:
            st.warning("No test cases selected."); return

        run_config = {**config}
        run_config.setdefault("driver", {})
        run_config["driver"]["headless"] = headless_run

        log_area    = st.empty()
        status_area = st.empty()
        progress    = st.progress(0)

        st.session_state.execution_running = True
        logs  = []
        total = len(test_cases)

        def add_log(msg):
            logs.append(msg)
            log_area.code("\n".join(logs[-50:]), language="text")

        add_log(f"Starting — {total} test case(s)")
        add_log("=" * 55)

        results = []
        try:
            from core.flow.flow_executor import FlowExecutor
            executor = FlowExecutor(run_config)

            for idx, tc in enumerate(test_cases):
                add_log(f"\n[{idx+1}/{total}] {tc.test_id} — {tc.name}")
                status_area.info(f"Running {tc.test_id} ({idx+1}/{total})...")
                progress.progress(idx / total)
                try:
                    result = executor._run_single(tc)
                    results.append(result)
                    for step in result.step_results:
                        icon = "OK" if step.status == "PASS" else ("SKIP" if step.status == "SKIP" else "FAIL")
                        add_log(f"  [{icon}] Step {step.step_no:02d} [{step.keyword}] {step.message}")
                    add_log(f"  => {tc.test_id}: {'PASSED' if result.status=='PASS' else 'FAILED'} ({result.elapsed_seconds}s)")
                except Exception as e:
                    add_log(f"  => {tc.test_id}: ERROR — {e}")
                progress.progress((idx + 1) / total)
        except Exception as e:
            add_log(f"Execution error: {e}")

        st.session_state.execution_running = False

        from core.flow.flow_executor import SuiteResult
        suite_result = SuiteResult(suite.name)
        suite_result.results = results
        st.session_state.suite_result = suite_result

        add_log("\n" + "=" * 55)
        add_log(f"DONE — Passed: {suite_result.passed} | Failed: {suite_result.failed} | Skipped: {suite_result.skipped}")

        try:
            from core.reports.html_reporter import HtmlReporter
            reporter    = HtmlReporter(run_config.get("reports", {"output_dir":"reports/output"}))
            report_path = reporter.generate(suite_result)
            st.session_state.last_report_path = report_path
            add_log(f"Report saved: {report_path}")
        except Exception as e:
            add_log(f"Report error: {e}")

        if suite_result.failed == 0:
            status_area.success(f"✅ All {suite_result.passed} test(s) PASSED")
        else:
            status_area.error(f"❌ {suite_result.failed} FAILED | ✅ {suite_result.passed} PASSED")
        progress.progress(1.0)
        st.info("Go to 📊 Reports page to view and download the report.")
