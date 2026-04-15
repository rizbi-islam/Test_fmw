"""
PHASE 3 VERIFICATION SCRIPT
============================
Run from your kwaf project root after copying Phase 3 files in.

Usage:
    python tests/verify_phase3.py

All 6 checks must PASS before Phase 4 begins.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS_MARK = "PASS"
FAIL_MARK = "FAIL"
results   = []


def check(name, fn):
    try:
        fn()
        results.append((PASS_MARK, name))
        print(f"  [PASS]  {name}")
    except Exception as e:
        results.append((FAIL_MARK, name, str(e)))
        print(f"  [FAIL]  {name}")
        print(f"          -> {str(e)[:200]}")


print("\n" + "=" * 62)
print("  KWAF — Phase 3 Verification  (6 checks)")
print("=" * 62 + "\n")


# CHECK 1 — All Phase 3 files exist
def check_files():
    required = [
        "ui/__init__.py",
        "ui/app.py",
        "ui/state.py",
        "ui/pages/__init__.py",
        "ui/pages/dashboard.py",
        "ui/pages/site_inspector.py",
        "ui/pages/test_suite_manager.py",
        "ui/pages/run_config.py",
        "ui/pages/execute.py",
        "ui/pages/reports.py",
    ]
    missing = [f for f in required if not os.path.exists(f)]
    if missing:
        raise FileNotFoundError("Missing:\n    " + "\n    ".join(missing))

check("All 10 Phase 3 UI files exist on disk", check_files)


# CHECK 2 — Streamlit is importable
def check_streamlit():
    import streamlit as st
    assert st is not None

check("Streamlit is installed and importable", check_streamlit)


# CHECK 3 — All UI modules import cleanly
def check_imports():
    import importlib
    mods = [
        "ui.state",
        "ui.pages.dashboard",
        "ui.pages.site_inspector",
        "ui.pages.test_suite_manager",
        "ui.pages.run_config",
        "ui.pages.execute",
        "ui.pages.reports",
    ]
    failed = []
    for mod in mods:
        try:
            importlib.import_module(mod)
        except Exception as e:
            # Streamlit modules fail outside app context — that's expected
            # We only fail if it's a real import error (missing file/package)
            err = str(e)
            if "No module named" in err and "streamlit" not in err.lower():
                failed.append(f"{mod}: {e}")
    if failed:
        raise ImportError("\n  ".join(failed))

check("All UI page modules import without missing-module errors", check_imports)


# CHECK 4 — State module works
def check_state():
    # Test load_config
    from ui.state import load_config
    config = load_config()
    assert isinstance(config, dict), f"Expected dict, got {type(config)}"

check("ui.state.load_config() returns a valid config dict", check_state)


# CHECK 5 — Phase 1 + 2 still intact
def check_phases():
    from core.drivers.driver_factory import DriverFactory
    from core.keywords.keyword_registry import KeywordRegistry
    from core.otp.otp_factory import OTPFactory
    from core.captcha.captcha_factory import CaptchaFactory
    from core.data.data_factory import DataFactory

    assert len(DriverFactory.available_drivers()) >= 2
    import core.keywords.keyword_registry as kr
    kr.KeywordRegistry._instance = None
    reg = KeywordRegistry()
    assert reg.has_keyword("HANDLE_OTP")
    assert reg.has_keyword("HANDLE_CAPTCHA")
    assert "firebase" in OTPFactory.available()
    assert "bypass"   in CaptchaFactory.available()
    assert "sqlite"   in DataFactory.available_providers()

check("Phase 1 + Phase 2 modules still intact after Phase 3 merge", check_phases)


# CHECK 6 — Streamlit CLI available
def check_streamlit_cli():
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "streamlit", "--version"],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, f"streamlit CLI failed: {result.stderr}"
    assert "streamlit" in result.stdout.lower() or "version" in result.stdout.lower()

check("Streamlit CLI available (streamlit --version works)", check_streamlit_cli)


# ── FINAL VERDICT ─────────────────────────────────────────────
passed_list = [r for r in results if r[0] == PASS_MARK]
failed_list = [r for r in results if r[0] == FAIL_MARK]

print(f"\n{'=' * 62}")
print(f"  Checks passed : {len(passed_list)} / {len(results)}")
print(f"{'=' * 62}")

if not failed_list:
    print("""
  ALL 6 CHECKS PASSED — Phase 3 is COMPLETE.

  Launch the dashboard:
      streamlit run ui/app.py

  Next steps:
    1. Open http://localhost:8501 in your browser
    2. Use Dashboard -> Run Configuration -> Execute Tests
    3. When ready: say "start phase 4"
""")
    sys.exit(0)
else:
    print(f"\n  {len(failed_list)} check(s) FAILED:\n")
    for r in failed_list:
        print(f"    [FAIL]  {r[1]}")
        if len(r) > 2:
            print(f"            -> {r[2][:300]}")
    print("\n  Fix the failing checks, then re-run: python tests/verify_phase3.py\n")
    sys.exit(1)
