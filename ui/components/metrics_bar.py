"""
Metrics Bar Component.
Reusable summary bar shown after test execution.
"""
import streamlit as st


def render_metrics_bar(total: int, passed: int, failed: int, skipped: int) -> None:
    """Render a 4-column metrics summary bar."""
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total",   total)
    c2.metric("✅ Passed",  passed,  delta=f"{int(passed/total*100) if total else 0}%")
    c3.metric("❌ Failed",  failed,  delta=f"-{failed}"  if failed  else None,
              delta_color="inverse")
    c4.metric("⏭️ Skipped", skipped, delta=f"-{skipped}" if skipped else None,
              delta_color="off")


def render_status_badge(status: str) -> str:
    """Return a colored emoji badge for a status string."""
    return {
        "PASS":  "✅ PASS",
        "FAIL":  "❌ FAIL",
        "SKIP":  "⏭️ SKIP",
        "ERROR": "⚠️ ERROR",
    }.get(status.upper(), f"❓ {status}")
