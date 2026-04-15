"""
PHASE 1 VERIFICATION SCRIPT
============================
Run this script to confirm Phase 1 is 100% complete and ready.

Usage:
    python tests/verify_phase1.py

All 12 checks must PASS before you proceed to Phase 2.
"""
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS_MARK = "PASS"
FAIL_MARK = "FAIL"
results = []


def check(name: str, fn):
    try:
        fn()
        results.append((PASS_MARK, name))
        print(f"  [PASS]  {name}")
    except Exception as e:
        results.append((FAIL_MARK, name, str(e)))
        print(f"  [FAIL]  {name}")
        print(f"          -> {e}")


print("\n" + "=" * 62)
print("  KWAF — Phase 1 Verification  (12 checks)")
print("=" * 62 + "\n")


# CHECK 1 — All required files exist
def check_files():
    required = [
        "config/config.yaml",
        "requirements.txt",
        "conftest.py",
        "run.py",
        "core/__init__.py",
        "core/drivers/__init__.py",
        "core/drivers/base_driver.py",
        "core/drivers/selenium_driver.py",
        "core/drivers/playwright_driver.py",
        "core/drivers/driver_factory.py",
        "core/keywords/__init__.py",
        "core/keywords/base_keyword.py",
        "core/keywords/keyword_registry.py",
        "core/keywords/keyword_executor.py",
        "core/keywords/actions/__init__.py",
        "core/keywords/actions/navigate.py",
        "core/keywords/actions/click.py",
        "core/keywords/actions/type_text.py",
        "core/keywords/actions/clear.py",
        "core/keywords/actions/select.py",
        "core/keywords/actions/wait.py",
        "core/keywords/actions/assert_keyword.py",
        "core/keywords/actions/screenshot.py",
        "core/keywords/actions/scroll.py",
        "core/keywords/actions/hover.py",
        "core/keywords/actions/get_text.py",
        "core/keywords/actions/verify_url.py",
        "core/keywords/actions/sleep.py",
        "core/keywords/actions/close_browser.py",
        "core/keywords/actions/switch_frame.py",
        "core/test_cases/__init__.py",
        "core/test_cases/test_case_model.py",
        "core/test_cases/excel_parser.py",
        "core/test_cases/test_case_registry.py",
        "core/data/__init__.py",
        "core/data/base_provider.py",
        "core/data/excel_provider.py",
        "core/data/data_factory.py",
        "core/flow/__init__.py",
        "core/flow/flow_context.py",
        "core/flow/flow_executor.py",
        "core/reports/__init__.py",
        "core/reports/base_reporter.py",
        "core/reports/html_reporter.py",
        "assets/templates/create_template.py",
    ]
    missing = [f for f in required if not os.path.exists(f)]
    if missing:
        raise FileNotFoundError("Missing:\n    " + "\n    ".join(missing))

check("All 44 Phase 1 files exist on disk", check_files)


# CHECK 2 — All modules import without errors
def check_imports():
    import importlib
    modules = [
        "core.drivers.base_driver",
        "core.drivers.selenium_driver",
        "core.drivers.playwright_driver",
        "core.drivers.driver_factory",
        "core.keywords.base_keyword",
        "core.keywords.keyword_registry",
        "core.keywords.keyword_executor",
        "core.test_cases.test_case_model",
        "core.test_cases.excel_parser",
        "core.test_cases.test_case_registry",
        "core.data.base_provider",
        "core.data.excel_provider",
        "core.data.data_factory",
        "core.flow.flow_context",
        "core.flow.flow_executor",
        "core.reports.base_reporter",
        "core.reports.html_reporter",
    ]
    failed = []
    for mod in modules:
        try:
            importlib.import_module(mod)
        except Exception as e:
            failed.append(f"{mod}: {e}")
    if failed:
        raise ImportError("\n  ".join(failed))

check("All 17 modules import without errors", check_imports)


# CHECK 3 — DriverFactory registers both drivers
def check_driver_factory():
    from core.drivers.driver_factory import DriverFactory
    available = DriverFactory.available_drivers()
    assert "selenium" in available,   f"'selenium' missing. Got: {available}"
    assert "playwright" in available, f"'playwright' missing. Got: {available}"

check("DriverFactory registers selenium + playwright", check_driver_factory)


# CHECK 4 — KeywordRegistry discovers all 15 keywords
def check_keyword_registry():
    from core.keywords.keyword_registry import KeywordRegistry
    reg = KeywordRegistry()
    expected = [
        "NAVIGATE", "CLICK", "TYPE", "CLEAR", "SELECT",
        "WAIT_FOR", "ASSERT_TEXT", "ASSERT_VISIBLE", "ASSERT_URL",
        "SCREENSHOT", "SCROLL_TO", "HOVER", "GET_TEXT",
        "VERIFY_URL", "SLEEP", "CLOSE_BROWSER",
        "SWITCH_FRAME", "SWITCH_DEFAULT",
    ]
    missing = [kw for kw in expected if not reg.has_keyword(kw)]
    if missing:
        raise AssertionError(f"Missing keywords: {missing}")
    total = len(reg.all_keywords())
    assert total >= 15, f"Expected 15+ keywords, got {total}"

check("KeywordRegistry auto-discovers all 15+ keywords", check_keyword_registry)


# CHECK 5 — FlowContext variable resolution
def check_flow_context():
    from core.flow.flow_context import FlowContext
    ctx = FlowContext(config={"base_url": "https://example.com"})
    ctx.set("username", "john_doe")
    ctx.set("page", "login")

    result = ctx.resolve("{base_url}/{page}?user={username}")
    assert result == "https://example.com/login?user=john_doe", f"Got: {result}"

    # Unknown variable should remain unchanged
    result2 = ctx.resolve("{unknown_var}")
    assert result2 == "{unknown_var}", f"Should stay unresolved, got: {result2}"

    # Test reset
    ctx.reset()
    assert ctx.get("username") is None

check("FlowContext resolves variables and resets correctly", check_flow_context)


# CHECK 6 — TestCase / TestSuite models
def check_models():
    from core.test_cases.test_case_model import TestCase, TestStep, TestSuite

    tc = TestCase(test_id="TC_MODEL", name="Model Test", enabled=True)
    s1 = TestStep(step_no=1, keyword="NAVIGATE", value="https://example.com")
    s2 = TestStep(step_no=2, keyword="CLICK", locator="#btn")
    tc.add_step(s1)
    tc.add_step(s2)

    assert tc.step_count == 2
    assert tc.steps[0]["keyword"] == "NAVIGATE"
    assert tc.steps[1]["locator"] == "#btn"

    suite = TestSuite(suite_id="S1", name="Test Suite")
    suite.add_test_case(tc)
    assert suite.total == 1
    assert suite.enabled_count == 1

    tc.enabled = False
    assert suite.enabled_count == 0

check("TestCase + TestSuite models build and filter correctly", check_models)


# CHECK 7 — Excel template creation and parsing
def check_excel():
    template_path = "assets/templates/test_suite.xlsx"
    if not os.path.exists(template_path):
        exec(open("assets/templates/create_template.py").read())

    from core.test_cases.excel_parser import ExcelParser
    parser = ExcelParser(template_path, sheet_name="TestSuite")
    suite = parser.parse()

    assert suite.total >= 2,         f"Expected 2+ test cases, got {suite.total}"
    assert suite.enabled_count >= 2, f"Expected 2+ enabled, got {suite.enabled_count}"

    tc = suite.test_cases[0]
    assert tc.step_count >= 3, f"TC001 should have 3+ steps, got {tc.step_count}"

check("Excel template created and parsed correctly", check_excel)


# CHECK 8 — TestCaseRegistry enable/disable
def check_registry():
    from core.test_cases.test_case_registry import TestCaseRegistry
    from core.test_cases.excel_parser import ExcelParser

    reg = TestCaseRegistry()
    reg.clear()

    parser = ExcelParser("assets/templates/test_suite.xlsx", sheet_name="TestSuite")
    suite = parser.parse()
    reg.register_suite(suite)

    assert reg.total >= 2

    # Disable TC001
    reg.disable("TC001")
    enabled_ids = [tc.test_id for tc in reg.get_enabled()]
    assert "TC001" not in enabled_ids, f"TC001 should be disabled. Enabled: {enabled_ids}"

    # Re-enable
    reg.enable("TC001")
    enabled_ids = [tc.test_id for tc in reg.get_enabled()]
    assert "TC001" in enabled_ids

    # get_by_id
    tc = reg.get_by_id("TC001")
    assert tc is not None and tc.test_id == "TC001"

check("TestCaseRegistry enable/disable/get_by_id works", check_registry)


# CHECK 9 — ExcelProvider reads TestData sheet
def check_excel_provider():
    from core.data.excel_provider import ExcelProvider

    provider = ExcelProvider(filepath="assets/templates/test_suite.xlsx")
    provider.connect()

    rows = provider.get_all_rows("TestData")
    assert len(rows) >= 1, f"Expected data rows, got {len(rows)}"
    assert "username" in rows[0], f"'username' missing. Keys: {list(rows[0].keys())}"

    row0 = provider.get_row("TestData", 0)
    assert row0["username"] == "testuser1"

    val = provider.get_value("TestData", 0, "email")
    assert val is not None and "@" in str(val)

    found = provider.find_row("TestData", "username", "testuser2")
    assert found is not None and found["username"] == "testuser2"

    provider.disconnect()

check("ExcelProvider reads rows, values, and find_row correctly", check_excel_provider)


# CHECK 10 — DataFactory returns ExcelProvider
def check_data_factory():
    from core.data.data_factory import DataFactory
    from core.data.excel_provider import ExcelProvider

    available = DataFactory.available_providers()
    assert "excel" in available, f"'excel' missing. Got: {available}"

    provider = DataFactory.get("excel", {"filepath": "assets/templates/test_suite.xlsx"})
    assert isinstance(provider, ExcelProvider), f"Expected ExcelProvider, got {type(provider)}"

check("DataFactory creates ExcelProvider correctly", check_data_factory)


# CHECK 11 — HtmlReporter generates valid HTML file
def check_html_reporter():
    from core.reports.html_reporter import HtmlReporter
    from core.flow.flow_executor import SuiteResult
    from core.keywords.keyword_executor import TestCaseResult, StepResult
    from datetime import datetime

    config = {"output_dir": "reports/output"}
    reporter = HtmlReporter(config)

    suite = SuiteResult("Verification Run")

    r1 = TestCaseResult("TC_PASS", "A Passing Test")
    r1.status = "PASS"
    r1.finished_at = datetime.now()
    r1.step_results = [
        StepResult(1, "NAVIGATE", "PASS", "Navigated OK", "", 120.5),
        StepResult(2, "CLICK",    "PASS", "Clicked OK",   "", 45.3),
    ]
    suite.results.append(r1)

    r2 = TestCaseResult("TC_FAIL", "A Failing Test")
    r2.status = "FAIL"
    r2.finished_at = datetime.now()
    r2.error_message = "Element not found"
    r2.step_results = [
        StepResult(1, "NAVIGATE", "PASS", "Navigated OK",      "", 110.2),
        StepResult(2, "CLICK",    "FAIL", "Element not found", "", 5001.0),
    ]
    suite.results.append(r2)

    path = reporter.generate(suite)

    assert os.path.exists(path), f"Report file not found: {path}"
    with open(path, encoding="utf-8") as f:
        content = f.read()

    assert "KWAF"             in content
    assert "Verification Run" in content
    assert "TC_PASS"          in content
    assert "TC_FAIL"          in content
    assert "NAVIGATE"         in content

check("HtmlReporter generates valid HTML with pass/fail tests", check_html_reporter)


# CHECK 12 — CLI run.py --list works end-to-end
def check_cli():
    import subprocess
    result = subprocess.run(
        [sys.executable, "run.py", "--list"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"CLI exited with code {result.returncode}\n"
        f"STDOUT: {result.stdout}\n"
        f"STDERR: {result.stderr}"
    )
    assert "TC001" in result.stdout or "TC002" in result.stdout, (
        f"No test cases shown in output:\n{result.stdout}"
    )

check("CLI (run.py --list) works end-to-end without errors", check_cli)


# ── FINAL VERDICT ─────────────────────────────────────────────────
passed_list  = [r for r in results if r[0] == PASS_MARK]
failed_list  = [r for r in results if r[0] == FAIL_MARK]
total        = len(results)

print(f"\n{'=' * 62}")
print(f"  Checks passed : {len(passed_list)} / {total}")
print(f"{'=' * 62}")

if not failed_list:
    print("""
  ALL 12 CHECKS PASSED — Phase 1 is COMPLETE.

  Next steps:
    1. Update PROGRESS.md -> Phase 1 STATUS: DONE
    2. Run a live smoke test:
         python run.py --headless
    3. Open the HTML report in your browser
    4. When ready: say "start phase 2"
""")
    sys.exit(0)
else:
    print(f"\n  {len(failed_list)} check(s) FAILED:\n")
    for r in failed_list:
        print(f"    [FAIL]  {r[1]}")
        if len(r) > 2:
            print(f"            -> {r[2][:200]}")
    print("""
  Fix the failing checks, then re-run this script.
  All 12 must pass before Phase 2 begins.
""")
    sys.exit(1)
