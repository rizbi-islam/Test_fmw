"""
PHASE 4 VERIFICATION SCRIPT
============================
Run from your kwaf project root after copying Phase 4 files in.

Usage:
    python tests/verify_phase4.py

All 8 checks must PASS before Phase 5 begins.
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
print("  KWAF — Phase 4 Verification  (8 checks)")
print("=" * 62 + "\n")


# CHECK 1 — All Phase 4 files exist
def check_files():
    required = [
        "Dockerfile",
        "docker-compose.yml",
        ".dockerignore",
        ".github/workflows/ci.yml",
        "run.py",
    ]
    missing = [f for f in required if not os.path.exists(f)]
    if missing:
        raise FileNotFoundError("Missing:\n    " + "\n    ".join(missing))

check("All Phase 4 files exist on disk", check_files)


# CHECK 2 — run.py has parallel flag
def check_parallel_flag():
    with open("run.py") as f:
        content = f.read()
    assert "--parallel" in content, "run.py missing --parallel flag"
    assert "_run_parallel" in content, "run.py missing _run_parallel function"
    assert "ThreadPoolExecutor" in content, "run.py missing ThreadPoolExecutor"

check("run.py has --parallel flag and ThreadPoolExecutor", check_parallel_flag)


# CHECK 3 — Parallel execution works with mock tests
def check_parallel_execution():
    from core.test_cases.test_case_model import TestCase, TestStep

    # Create 3 simple test cases
    test_cases = []
    for i in range(1, 4):
        tc = TestCase(test_id=f"TC_PAR_{i}", name=f"Parallel Test {i}", enabled=True)
        tc.add_step(TestStep(step_no=1, keyword="SLEEP", value="0.1"))
        test_cases.append(tc)

    import yaml
    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)
    config["driver"]["headless"] = True

    # Import parallel runner from run.py
    import importlib.util
    spec   = importlib.util.spec_from_file_location("run_module", "run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    result = module._run_parallel(test_cases, config, workers=2)
    assert result.total == 3, f"Expected 3 results, got {result.total}"

check("Parallel execution runs 3 tests with 2 workers correctly", check_parallel_execution)


# CHECK 4 — GitHub Actions file is valid YAML
def check_ci_yaml():
    import yaml
    with open(".github/workflows/ci.yml") as f:
        ci = yaml.safe_load(f)
    assert "jobs" in ci,   "ci.yml missing 'jobs'"
    assert "on"   in ci,   "ci.yml missing 'on' trigger"
    jobs = ci["jobs"]
    assert len(jobs) >= 1, "ci.yml has no jobs defined"
    # Check it has the right steps
    first_job = list(jobs.values())[0]
    step_names = [s.get("name","") for s in first_job.get("steps",[])]
    assert any("Python" in s for s in step_names),      "Missing Python setup step"
    assert any("dependencies" in s for s in step_names), "Missing install step"

check("GitHub Actions ci.yml is valid and has required steps", check_ci_yaml)


# CHECK 5 — Dockerfile is valid
def check_dockerfile():
    with open("Dockerfile") as f:
        content = f.read()
    assert "FROM python"     in content, "Dockerfile missing FROM python"
    assert "WORKDIR"         in content, "Dockerfile missing WORKDIR"
    assert "requirements.txt" in content, "Dockerfile missing requirements install"
    assert "playwright"       in content, "Dockerfile missing playwright install"
    assert "CMD"              in content, "Dockerfile missing CMD"

check("Dockerfile is valid and contains all required instructions", check_dockerfile)


# CHECK 6 — docker-compose.yml is valid YAML
def check_compose():
    import yaml
    with open("docker-compose.yml") as f:
        compose = yaml.safe_load(f)
    assert "services" in compose, "docker-compose.yml missing services"
    services = compose["services"]
    assert len(services) >= 2, f"Expected 2+ services, got {len(services)}"
    # Check for UI service with port mapping
    has_port = any(
        "ports" in svc for svc in services.values()
    )
    assert has_port, "No service exposes a port (UI service missing)"

check("docker-compose.yml valid with 2+ services including UI", check_compose)


# CHECK 7 — All previous phases still intact
def check_previous_phases():
    from core.drivers.driver_factory import DriverFactory
    from core.otp.otp_factory import OTPFactory
    from core.captcha.captcha_factory import CaptchaFactory
    from core.data.data_factory import DataFactory
    import core.keywords.keyword_registry as kr
    kr.KeywordRegistry._instance = None
    from core.keywords.keyword_registry import KeywordRegistry
    reg = KeywordRegistry()

    assert len(DriverFactory.available_drivers()) >= 2
    assert reg.has_keyword("HANDLE_OTP")
    assert reg.has_keyword("HANDLE_CAPTCHA")
    assert "firebase" in OTPFactory.available()
    assert "sqlite"   in DataFactory.available_providers()
    assert os.path.exists("ui/app.py")

check("Phase 1 + 2 + 3 all still intact after Phase 4 merge", check_previous_phases)


# CHECK 8 — CLI run.py --list still works
def check_cli():
    import subprocess
    result = subprocess.run(
        [sys.executable, "run.py", "--list"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, (
        f"CLI failed (code {result.returncode})\n"
        f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    )
    assert "TC" in result.stdout, f"No test cases in output:\n{result.stdout}"

check("CLI (run.py --list) works end-to-end", check_cli)


# ── FINAL VERDICT ─────────────────────────────────────────────
passed_list = [r for r in results if r[0] == PASS_MARK]
failed_list = [r for r in results if r[0] == FAIL_MARK]

print(f"\n{'=' * 62}")
print(f"  Checks passed : {len(passed_list)} / {len(results)}")
print(f"{'=' * 62}")

if not failed_list:
    print("""
  ALL 8 CHECKS PASSED — Phase 4 is COMPLETE.

  What you can now do:

  Parallel execution:
      python run.py --headless --parallel --workers 4

  Docker (build + run):
      docker build -t kwaf .
      docker run kwaf python run.py --headless

  Docker UI:
      docker-compose --profile ui up

  CI/CD:
      Push to GitHub -> Actions tab -> pipeline runs automatically

  When ready: say "start phase 5"
""")
    sys.exit(0)
else:
    print(f"\n  {len(failed_list)} check(s) FAILED:\n")
    for r in failed_list:
        print(f"    [FAIL]  {r[1]}")
        if len(r) > 2:
            print(f"            -> {r[2][:300]}")
    print("\n  Fix failing checks then re-run: python tests/verify_phase4.py\n")
    sys.exit(1)
