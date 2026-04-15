"""
Keyword Builder Component.
Visual form-based test case builder — no Excel needed.
Users pick keywords from dropdowns and build test cases step by step.
"""
import streamlit as st


KEYWORD_HELP = {
    "NAVIGATE":       "Go to a URL",
    "CLICK":          "Click an element",
    "TYPE":           "Type text into a field",
    "CLEAR":          "Clear a field",
    "SELECT":         "Choose a dropdown option",
    "WAIT_FOR":       "Wait until element is visible",
    "ASSERT_TEXT":    "Assert element text equals value",
    "ASSERT_VISIBLE": "Assert element is on the page",
    "ASSERT_URL":     "Assert URL contains text",
    "VERIFY_URL":     "Wait for URL to contain text",
    "SCREENSHOT":     "Take a screenshot",
    "SCROLL_TO":      "Scroll to element or top/bottom",
    "HOVER":          "Hover mouse over element",
    "GET_TEXT":       "Get text and store in variable",
    "SLEEP":          "Pause for N seconds",
    "CLOSE_BROWSER":  "Close the browser",
    "SWITCH_FRAME":   "Switch into an iframe",
    "SWITCH_DEFAULT": "Switch back to main page",
    "HANDLE_OTP":     "Get OTP and type into field",
    "HANDLE_CAPTCHA": "Solve or bypass CAPTCHA",
}

KEYWORDS_NEEDING_LOCATOR = {
    "CLICK", "TYPE", "CLEAR", "SELECT", "WAIT_FOR",
    "ASSERT_TEXT", "ASSERT_VISIBLE", "HOVER", "GET_TEXT",
    "SCROLL_TO", "SWITCH_FRAME", "HANDLE_OTP",
}

KEYWORDS_NEEDING_VALUE = {
    "NAVIGATE", "TYPE", "SELECT", "ASSERT_TEXT", "ASSERT_URL",
    "VERIFY_URL", "SCREENSHOT", "SLEEP", "GET_TEXT",
    "HANDLE_OTP", "HANDLE_CAPTCHA",
}


def render_keyword_builder(tc_id: str = "TC_NEW", tc_name: str = "New Test") -> dict:
    """
    Full keyword-driven test case builder.
    Returns a dict with test case metadata and steps list.
    """
    st.subheader("🔧 Keyword Builder")
    st.caption("Build test cases visually without editing Excel directly.")

    # ── Test Case Info ────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    tc_id_input   = col1.text_input("Test Case ID",   value=tc_id,   key="kb_tc_id")
    tc_name_input = col2.text_input("Test Case Name", value=tc_name, key="kb_tc_name")
    tc_enabled    = col3.selectbox("Enabled", ["YES", "NO"],          key="kb_enabled")

    # ── Step Builder ──────────────────────────────────────────
    from ui.components.step_editor import render_step_editor
    steps = render_step_editor(key_prefix="kb")

    # ── Preview ───────────────────────────────────────────────
    if steps:
        st.divider()
        st.subheader("Preview")
        from ui.components.step_editor import render_step_table
        render_step_table(steps)

        # Export to Excel rows format
        excel_rows = []
        for step in steps:
            excel_rows.append([
                tc_id_input,
                tc_name_input,
                tc_enabled,
                step.get("step_no", ""),
                step.get("keyword", ""),
                step.get("locator", ""),
                step.get("strategy", "css"),
                step.get("value", ""),
                step.get("timeout", 10),
                "",  # DataSource
                "",  # Description
            ])

        import pandas as pd
        df = pd.DataFrame(excel_rows, columns=[
            "TestCaseID", "TestName", "Enabled", "StepNo",
            "Keyword", "Locator", "Strategy", "Value", "Timeout",
            "DataSource", "Description"
        ])

        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download as CSV (paste into Excel)",
            data=csv,
            file_name=f"{tc_id_input}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    return {
        "test_id":  tc_id_input,
        "name":     tc_name_input,
        "enabled":  tc_enabled == "YES",
        "steps":    steps,
    }


def render_keyword_reference() -> None:
    """Show a quick reference table of all keywords."""
    import pandas as pd
    st.subheader("📖 Keyword Reference")
    rows = [{"Keyword": k, "Description": v} for k, v in KEYWORD_HELP.items()]
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True, height=400)
