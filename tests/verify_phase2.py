"""
PHASE 2 VERIFICATION SCRIPT
============================
Run from your kwaf project root AFTER copying Phase 2 files in.

Usage:
    python tests/verify_phase2.py

All 10 checks must PASS before Phase 3 begins.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS_MARK = "PASS"
FAIL_MARK = "FAIL"
results   = []


def check(name: str, fn):
    try:
        fn()
        results.append((PASS_MARK, name))
        print(f"  [PASS]  {name}")
    except Exception as e:
        results.append((FAIL_MARK, name, str(e)))
        print(f"  [FAIL]  {name}")
        print(f"          -> {str(e)[:200]}")


print("\n" + "=" * 62)
print("  KWAF — Phase 2 Verification  (10 checks)")
print("=" * 62 + "\n")


# CHECK 1 — All Phase 2 files exist
def check_files():
    required = [
        "core/otp/__init__.py",
        "core/otp/base_otp.py",
        "core/otp/mock_otp.py",
        "core/otp/firebase_otp.py",
        "core/otp/gmail_imap_otp.py",
        "core/otp/otp_factory.py",
        "core/captcha/__init__.py",
        "core/captcha/base_captcha.py",
        "core/captcha/bypass_captcha.py",
        "core/captcha/twocaptcha_solver.py",
        "core/captcha/manual_pause_captcha.py",
        "core/captcha/captcha_factory.py",
        "core/data/sqlite_provider.py",
        "core/data/mysql_provider.py",
        "core/data/json_provider.py",
        "core/data/data_factory.py",
        "core/keywords/actions/otp_keyword.py",
        "core/keywords/actions/captcha_keyword.py",
    ]
    missing = [f for f in required if not os.path.exists(f)]
    if missing:
        raise FileNotFoundError("Missing:\n    " + "\n    ".join(missing))

check("All 18 Phase 2 files exist on disk", check_files)


# CHECK 2 — All Phase 2 modules import cleanly
def check_imports():
    import importlib
    modules = [
        "core.otp.base_otp",
        "core.otp.mock_otp",
        "core.otp.firebase_otp",
        "core.otp.gmail_imap_otp",
        "core.otp.otp_factory",
        "core.captcha.base_captcha",
        "core.captcha.bypass_captcha",
        "core.captcha.twocaptcha_solver",
        "core.captcha.manual_pause_captcha",
        "core.captcha.captcha_factory",
        "core.data.sqlite_provider",
        "core.data.mysql_provider",
        "core.data.json_provider",
        "core.data.data_factory",
    ]
    failed = []
    for mod in modules:
        try:
            importlib.import_module(mod)
        except Exception as e:
            failed.append(f"{mod}: {e}")
    if failed:
        raise ImportError("\n  ".join(failed))

check("All Phase 2 modules import without errors", check_imports)


# CHECK 3 — OTPFactory registers all 3 handlers
def check_otp_factory():
    from core.otp.otp_factory import OTPFactory
    available = OTPFactory.available()
    for name in ["mock", "firebase", "gmail"]:
        assert name in available, f"'{name}' not in OTPFactory. Got: {available}"

check("OTPFactory registers mock + firebase + gmail", check_otp_factory)


# CHECK 4 — MockOTP returns configured value
def check_mock_otp():
    from core.otp.mock_otp import MockOTPHandler
    handler = MockOTPHandler({"otp_value": "998877"})
    otp = handler.get_otp(timeout=5)
    assert otp == "998877", f"Expected '998877', got '{otp}'"
    handler.clear()  # should not raise

check("MockOTPHandler returns correct static OTP", check_mock_otp)


# CHECK 5 — OTPFactory creates MockOTP via factory
def check_otp_factory_mock():
    from core.otp.otp_factory import OTPFactory
    handler = OTPFactory.get("mock", {"otp_value": "112233"})
    otp = handler.get_otp()
    assert otp == "112233", f"Expected '112233', got '{otp}'"

check("OTPFactory.get('mock') creates and returns OTP correctly", check_otp_factory_mock)


# CHECK 6 — CaptchaFactory registers all 3 strategies
def check_captcha_factory():
    from core.captcha.captcha_factory import CaptchaFactory
    available = CaptchaFactory.available()
    for name in ["bypass", "twocaptcha", "manual"]:
        assert name in available, f"'{name}' not in CaptchaFactory. Got: {available}"

check("CaptchaFactory registers bypass + twocaptcha + manual", check_captcha_factory)


# CHECK 7 — DataFactory registers all 4 providers
def check_data_factory():
    from core.data.data_factory import DataFactory
    available = DataFactory.available_providers()
    for name in ["excel", "sqlite", "mysql", "json"]:
        assert name in available, f"'{name}' not in DataFactory. Got: {available}"

check("DataFactory registers excel + sqlite + mysql + json", check_data_factory)


# CHECK 8 — SQLiteProvider works end-to-end
def check_sqlite():
    import os
    from core.data.sqlite_provider import SQLiteProvider

    db_path  = "data/test_verify.db"
    os.makedirs("data", exist_ok=True)

    provider = SQLiteProvider(db_path=db_path)
    provider.connect()

    # Create a test table and insert rows
    from sqlalchemy import text
    provider._conn.execute(text("DROP TABLE IF EXISTS test_users"))
    provider._conn.execute(text(
        "CREATE TABLE test_users (id TEXT, username TEXT, email TEXT)"
    ))
    provider._conn.execute(text(
        "INSERT INTO test_users VALUES ('1', 'alice', 'alice@example.com')"
    ))
    provider._conn.execute(text(
        "INSERT INTO test_users VALUES ('2', 'bob', 'bob@example.com')"
    ))
    provider._conn.commit()

    rows = provider.get_all_rows("test_users")
    assert len(rows) == 2, f"Expected 2 rows, got {len(rows)}"

    row0 = provider.get_row("test_users", 0)
    assert row0["username"] == "alice", f"Expected 'alice', got {row0['username']}"

    found = provider.find_row("test_users", "username", "bob")
    assert found is not None and found["email"] == "bob@example.com"

    val = provider.get_value("test_users", 1, "username")
    assert val == "bob", f"Expected 'bob', got {val}"

    provider.disconnect()

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)

check("SQLiteProvider connect/read/find/value works correctly", check_sqlite)


# CHECK 9 — HANDLE_OTP keyword registered in KeywordRegistry
def check_otp_keyword():
    # Reset singleton so it re-discovers with new keywords
    import core.keywords.keyword_registry as kr_module
    kr_module.KeywordRegistry._instance = None

    from core.keywords.keyword_registry import KeywordRegistry
    reg = KeywordRegistry()
    assert reg.has_keyword("HANDLE_OTP"),     "HANDLE_OTP keyword not found"
    assert reg.has_keyword("HANDLE_CAPTCHA"), "HANDLE_CAPTCHA keyword not found"

check("HANDLE_OTP + HANDLE_CAPTCHA keywords auto-discovered", check_otp_keyword)


# CHECK 10 — JsonProvider reads data correctly
def check_json_provider():
    import json
    import os
    from core.data.json_provider import JsonProvider

    # Create temp JSON data file
    data_dir = "assets/data"
    os.makedirs(data_dir, exist_ok=True)
    test_file = os.path.join(data_dir, "test_data.json")

    sample = {
        "Users": [
            {"id": "1", "username": "json_user1", "role": "admin"},
            {"id": "2", "username": "json_user2", "role": "viewer"},
        ]
    }
    with open(test_file, "w") as f:
        json.dump(sample, f)

    provider = JsonProvider(data_dir=data_dir)
    provider.connect()

    rows = provider.get_all_rows("Users")
    assert len(rows) == 2, f"Expected 2 rows, got {len(rows)}"

    row0 = provider.get_row("Users", 0)
    assert row0["username"] == "json_user1"

    found = provider.find_row("Users", "role", "viewer")
    assert found is not None and found["username"] == "json_user2"

    provider.disconnect()
    os.remove(test_file)

check("JsonProvider reads/finds rows from JSON files correctly", check_json_provider)


# ── FINAL VERDICT ─────────────────────────────────────────────
passed_list = [r for r in results if r[0] == PASS_MARK]
failed_list = [r for r in results if r[0] == FAIL_MARK]
total       = len(results)

print(f"\n{'=' * 62}")
print(f"  Checks passed : {len(passed_list)} / {total}")
print(f"{'=' * 62}")

if not failed_list:
    print("""
  ALL 10 CHECKS PASSED — Phase 2 is COMPLETE.

  Next steps:
    1. Update PROGRESS.md -> Phase 2 STATUS: DONE
    2. Test OTP flow:
         Set otp.default = "mock" in config.yaml
         Add HANDLE_OTP keyword to your test suite Excel
    3. Test CAPTCHA bypass:
         Add HANDLE_CAPTCHA keyword with value = "bypass"
    4. Switch data source:
         Set data.default_provider = "sqlite" in config.yaml
    5. When ready: say "start phase 3"
""")
    sys.exit(0)
else:
    print(f"\n  {len(failed_list)} check(s) FAILED:\n")
    for r in failed_list:
        print(f"    [FAIL]  {r[1]}")
        if len(r) > 2:
            print(f"            -> {r[2][:300]}")
    print("""
  Fix the failing checks, then re-run:
      python tests/verify_phase2.py
""")
    sys.exit(1)
