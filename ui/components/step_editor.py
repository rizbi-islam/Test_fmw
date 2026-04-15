"""
Reusable Step Editor Component.
Used in Test Suite Manager to add/edit individual test steps inline.
"""
import streamlit as st


def render_step_editor(existing_steps: list = None, key_prefix: str = "step") -> list:
    """
    Renders an interactive step editor.
    Returns the list of step dicts built by the user.

    Args:
        existing_steps: pre-populate with existing steps
        key_prefix:     unique key prefix to avoid widget collisions
    """
    KEYWORDS = [
        "NAVIGATE", "CLICK", "TYPE", "CLEAR", "SELECT",
        "WAIT_FOR", "ASSERT_TEXT", "ASSERT_VISIBLE", "ASSERT_URL",
        "VERIFY_URL", "SCREENSHOT", "SCROLL_TO", "HOVER",
        "GET_TEXT", "SLEEP", "CLOSE_BROWSER",
        "SWITCH_FRAME", "SWITCH_DEFAULT",
        "HANDLE_OTP", "HANDLE_CAPTCHA",
    ]
    STRATEGIES = ["css", "xpath", "id", "name", "class", "link_text", "partial_link"]

    # Init session state for steps
    state_key = f"{key_prefix}_steps"
    if state_key not in st.session_state:
        st.session_state[state_key] = existing_steps or []

    steps = st.session_state[state_key]

    # ── Existing Steps ────────────────────────────────────────
    if steps:
        st.write(f"**{len(steps)} step(s) defined:**")
        to_delete = None

        for idx, step in enumerate(steps):
            with st.expander(
                f"Step {step.get('step_no', idx+1):02d} — {step.get('keyword','?')}  "
                f"| {step.get('locator','') or step.get('value','')}",
                expanded=False,
            ):
                c1, c2, c3 = st.columns([2, 2, 1])
                step["keyword"]  = c1.selectbox(
                    "Keyword", KEYWORDS,
                    index=KEYWORDS.index(step.get("keyword", "NAVIGATE")) if step.get("keyword") in KEYWORDS else 0,
                    key=f"{key_prefix}_{idx}_kw",
                )
                step["locator"]  = c2.text_input("Locator",  value=step.get("locator", ""),  key=f"{key_prefix}_{idx}_loc")
                step["strategy"] = c3.selectbox(
                    "Strategy", STRATEGIES,
                    index=STRATEGIES.index(step.get("strategy", "css")) if step.get("strategy") in STRATEGIES else 0,
                    key=f"{key_prefix}_{idx}_str",
                )
                cv1, cv2, cv3 = st.columns([3, 1, 1])
                step["value"]   = cv1.text_input("Value",   value=step.get("value", ""),   key=f"{key_prefix}_{idx}_val")
                step["timeout"] = cv2.number_input("Timeout", min_value=1, max_value=120,
                                                    value=int(step.get("timeout", 10)),     key=f"{key_prefix}_{idx}_to")
                step["enabled"] = cv3.checkbox("Enabled", value=step.get("enabled", True), key=f"{key_prefix}_{idx}_en")

                if st.button("🗑️ Delete Step", key=f"{key_prefix}_{idx}_del"):
                    to_delete = idx

        if to_delete is not None:
            steps.pop(to_delete)
            # Re-number
            for i, s in enumerate(steps):
                s["step_no"] = i + 1
            st.session_state[state_key] = steps
            st.rerun()

    # ── Add New Step ──────────────────────────────────────────
    st.divider()
    st.write("**Add New Step**")

    nc1, nc2, nc3 = st.columns([2, 2, 1])
    new_keyword  = nc1.selectbox("Keyword",  KEYWORDS,  key=f"{key_prefix}_new_kw")
    new_locator  = nc2.text_input("Locator", value="",  key=f"{key_prefix}_new_loc")
    new_strategy = nc3.selectbox("Strategy", STRATEGIES, key=f"{key_prefix}_new_str")

    nv1, nv2 = st.columns([3, 1])
    new_value   = nv1.text_input("Value",   value="",   key=f"{key_prefix}_new_val")
    new_timeout = nv2.number_input("Timeout", min_value=1, max_value=120, value=10, key=f"{key_prefix}_new_to")

    if st.button("➕ Add Step", key=f"{key_prefix}_add", use_container_width=True):
        new_step = {
            "step_no":  len(steps) + 1,
            "keyword":  new_keyword,
            "locator":  new_locator,
            "strategy": new_strategy,
            "value":    new_value,
            "timeout":  new_timeout,
            "enabled":  True,
        }
        steps.append(new_step)
        st.session_state[state_key] = steps
        st.rerun()

    return steps


def render_step_table(steps: list) -> None:
    """Render steps as a clean read-only table."""
    if not steps:
        st.info("No steps defined.")
        return

    import pandas as pd
    rows = []
    for s in steps:
        rows.append({
            "#":        s.get("step_no", ""),
            "Keyword":  s.get("keyword", ""),
            "Locator":  s.get("locator", ""),
            "Strategy": s.get("strategy", ""),
            "Value":    s.get("value", ""),
            "Timeout":  s.get("timeout", ""),
            "Enabled":  "✅" if s.get("enabled", True) else "⏸️",
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
