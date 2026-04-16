# KWAF — User Guide

Complete guide to writing and running tests with KWAF.

---

## 1. Quick Start (5 Minutes)

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Create blank test template
python assets/templates/blank_template.py

# Fill in your test cases (see Section 3)
# Then run:
python run.py --list           # see all tests
python run.py --headless       # run all tests
streamlit run ui\app.py        # open UI dashboard
```

---

## 2. Project Structure

```
kwaf/
├── assets/
│   ├── templates/
│   │   ├── test_suite.xlsx        ← your test cases live here
│   │   └── blank_test_suite.xlsx  ← clean starting template
│   └── screenshots/               ← failure screenshots auto-saved here
├── config/
│   └── config.yaml                ← all settings (driver, OTP, DB, etc.)
├── core/                          ← framework engine (do not edit)
├── reports/output/                ← HTML/PDF/Excel reports saved here
├── ui/                            ← Streamlit dashboard
├── run.py                         ← CLI entry point
└── docs/
    ├── USER_GUIDE.md              ← this file
    └── KEYWORD_REFERENCE.md      ← all keywords explained
```

---

## 3. Writing Your First Test

### Step 1 — Open the Excel template

Open `assets/templates/blank_test_suite.xlsx` in Excel.

### Step 2 — Fill the TestData sheet

Add your test data variables here. Each row is one dataset.

| RowID | username | password | email | base_url |
|---|---|---|---|---|
| row1 | admin | Admin@123 | admin@myapp.com | https://myapp.com |
| row2 | user1 | User@123  | user1@myapp.com | https://myapp.com |

### Step 3 — Fill the TestSuite sheet

Each group of rows with the same TestCaseID = one test case.

| TestCaseID | TestName | Enabled | StepNo | Keyword | Locator | Strategy | Value | Timeout |
|---|---|---|---|---|---|---|---|---|
| TC001 | Admin_Login | YES | 1 | NAVIGATE | | css | {base_url}/login | 10 |
| TC001 | Admin_Login | YES | 2 | TYPE | #email | css | {username} | 5 |
| TC001 | Admin_Login | YES | 3 | TYPE | #password | css | {password} | 5 |
| TC001 | Admin_Login | YES | 4 | CLICK | #submit | css | | 5 |
| TC001 | Admin_Login | YES | 5 | ASSERT_URL | | css | dashboard | 10 |
| TC001 | Admin_Login | YES | 6 | SCREENSHOT | | css | login_success.png | 5 |

### Step 4 — Run it

```bash
python run.py --list           # confirm TC001 shows up
python run.py --headless       # run with browser hidden
python run.py                  # run with browser visible
```

---

## 4. Configuration

Edit `config/config.yaml` to change settings.

### Switch Browser
```yaml
driver:
  default: selenium     # or playwright
  browser: chrome       # or firefox, edge
  headless: false       # true = no browser window
```

### Switch Data Source
```yaml
data:
  default_provider: excel    # start here
  # Later switch to:
  # default_provider: sqlite
  # default_provider: mysql
```

### Set Base URL per Environment
```yaml
environment:
  name: staging
  base_url: https://staging.myapp.com
```

Then in your test use `{base_url}` as the value for NAVIGATE steps.

---

## 5. Running Tests

### Basic Run
```bash
python run.py --headless
```

### Run a Single Test
```bash
python run.py --test-id TC001 --headless
```

### Run by Tag
Add tags to your test case in the TestSuite sheet (Tags column),
then filter:
```bash
python run.py --tags smoke --headless
```

### Parallel Execution (Phase 4)
```bash
python run.py --headless --parallel --workers 4
```
Use `--driver playwright` for best parallel results on Windows.

### Using the UI
```bash
streamlit run ui\app.py
# Open http://localhost:8501
```

---

## 6. Reports

Reports are automatically saved to `reports/output/` after every run.

Three formats available:

| Format | How to generate | File |
|---|---|---|
| HTML | Default — always generated | `report_*.html` |
| PDF | See Section 7 | `report_*.pdf` |
| Excel | See Section 7 | `results_*.xlsx` |

Open HTML reports directly in your browser.

---

## 7. Generating PDF and Excel Reports

Add this to your run script or call programmatically:

```python
import yaml
from core.reports.pdf_reporter import PdfReporter
from core.reports.excel_reporter import ExcelReporter

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

report_config = config.get("reports", {"output_dir": "reports/output"})

# After running tests and getting suite_result:
pdf_reporter   = PdfReporter(report_config)
excel_reporter = ExcelReporter(report_config)

pdf_path   = pdf_reporter.generate(suite_result)
excel_path = excel_reporter.generate(suite_result)
```

Or via CLI (coming in a future update):
```bash
python run.py --headless --report pdf
python run.py --headless --report excel
python run.py --headless --report all
```

---

## 8. OTP Testing

### Using Mock OTP (Development)
In `config.yaml`:
```yaml
otp:
  default: mock
  mock:
    otp_value: "123456"
```

In your Excel test:
```
Keyword: HANDLE_OTP | Locator: #otp-field | Value: mock | Timeout: 5
```

### Using Firebase OTP (Free, Production)

1. Create project at https://console.firebase.google.com
2. Download service account JSON → save as `config/firebase_credentials.json`
3. In your phone app, write the received OTP to Firebase path `otp/device1`
4. Configure:
```yaml
otp:
  default: firebase
  firebase:
    credentials_path: config/firebase_credentials.json
    database_url: https://your-project.firebaseio.com
    otp_path: otp/device1
```

---

## 9. Site Inspector

Automatically discover form fields on any site:

```python
from core.inspector.site_inspector import SiteInspector

inspector = SiteInspector(driver_type="playwright", headless=True)
fields    = inspector.inspect("https://yourapp.com/login")
steps     = inspector.generate_skeleton("TC010", "Login_Test",
                                         "https://yourapp.com/login", fields)
inspector.export_to_excel(steps, "assets/templates/tc010_skeleton.xlsx")
```

Or use the **Site Inspector** page in the Streamlit UI.

---

## 10. CI/CD with GitHub Actions

Push to GitHub and tests run automatically:

```bash
git init
git add .
git commit -m "Add KWAF tests"
git remote add origin https://github.com/you/your-repo.git
git push -u origin main
```

Go to your repo → **Actions** tab → see the pipeline running.
Artifacts (reports, screenshots) are downloadable from the Actions run page.

---

## 11. Troubleshooting

| Problem | Fix |
|---|---|
| `No module named 'loguru'` | `pip install loguru` |
| `ChromeDriver not found` | `pip install webdriver-manager` (auto-downloads driver) |
| `WinError 193` in parallel | Use `--driver playwright` for parallel runs |
| Streamlit `localhost refused` | Use `--server.address=0.0.0.0` or try `http://127.0.0.1:8501` |
| `Module not found 'ui'` | Run from project root: `streamlit run ui\app.py` |
| Element not found | Check locator in browser DevTools (F12 → Elements → right-click → Copy selector) |
| Test passes locally, fails in CI | Add `--headless` flag; CI has no display |
