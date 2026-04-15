# KWAF — Keyword-driven Web Automation Framework

A production-grade, keyword-driven automation framework built in Python.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers
playwright install chromium

# 3. Create the Excel template
python assets/templates/create_template.py

# 4. Verify Phase 1 is complete
python tests/verify_phase1.py

# 5. List all test cases
python run.py --list

# 6. Run all enabled tests (headless)
python run.py --headless

# 7. Run with Playwright
python run.py --driver playwright --headless

# 8. Run single test
python run.py --test-id TC001 --headless

# 9. Open report
# Reports saved to: reports/output/report_*.html
```

## Project Structure

```
kwaf/
├── core/
│   ├── drivers/          # Selenium, Playwright, (Mobile, API in Phase 2)
│   ├── keywords/         # Keyword engine + 15 built-in actions
│   ├── test_cases/       # Excel parser + test case models
│   ├── data/             # Data providers (Excel + more in Phase 2)
│   ├── flow/             # Flow context + executor
│   └── reports/          # HTML reporter (PDF + Excel in Phase 2)
├── config/
│   └── config.yaml       # Master configuration
├── assets/
│   └── templates/        # Excel test suite template
├── tests/
│   └── verify_phase1.py  # Phase 1 completion checker
├── reports/output/       # Generated HTML reports
├── logs/                 # Execution logs
├── run.py                # CLI entry point
├── conftest.py           # Pytest fixtures
└── PROGRESS.md           # Build tracker
```

## Built-in Keywords (Phase 1)

| Keyword        | Description                            |
|----------------|----------------------------------------|
| NAVIGATE       | Go to a URL                            |
| CLICK          | Click an element                       |
| TYPE           | Type text into an input                |
| CLEAR          | Clear an input field                   |
| SELECT         | Select dropdown option                 |
| WAIT_FOR       | Wait until element is visible          |
| ASSERT_TEXT    | Assert element text contains value     |
| ASSERT_VISIBLE | Assert element is visible              |
| ASSERT_URL     | Assert URL contains text               |
| VERIFY_URL     | Wait + verify URL contains text        |
| SCREENSHOT     | Take a screenshot                      |
| SCROLL_TO      | Scroll to element or top/bottom        |
| HOVER          | Hover mouse over element               |
| GET_TEXT       | Get text and store in context variable |
| SLEEP          | Pause for N seconds                    |
| CLOSE_BROWSER  | Close the browser                      |
| SWITCH_FRAME   | Switch into an iframe                  |
| SWITCH_DEFAULT | Switch back to main content            |

## Locator Strategies

| Strategy     | Example                     |
|--------------|-----------------------------|
| css          | `#email`, `.btn-submit`     |
| xpath        | `//input[@name='email']`    |
| id           | `email`                     |
| name         | `email`                     |
| class        | `btn-primary`               |
| link_text    | `Click Here`                |
| partial_link | `Click`                     |

## Excel Test Suite Format

Sheet: `TestSuite`

| TestCaseID | TestName | Enabled | StepNo | Keyword | Locator | Strategy | Value | Timeout |
|---|---|---|---|---|---|---|---|---|
| TC001 | Login_Test | YES | 1 | NAVIGATE | | css | https://app.com | 10 |
| TC001 | Login_Test | YES | 2 | TYPE | #email | css | {email} | 5 |
| TC001 | Login_Test | YES | 3 | TYPE | #password | css | {password} | 5 |
| TC001 | Login_Test | YES | 4 | CLICK | #submit | css | | 5 |
| TC001 | Login_Test | YES | 5 | ASSERT_URL | | css | dashboard | 10 |

Use `{variable}` syntax to reference context variables or test data values.

## Configuration

Edit `config/config.yaml`:

```yaml
driver:
  default: "selenium"     # or "playwright"
  browser: "chrome"       # or "firefox", "edge"
  headless: false

data:
  excel:
    test_suite_path: "assets/templates/test_suite.xlsx"
```

## Phase Roadmap

- **Phase 1** — Core engine (current)
- **Phase 2** — DB providers + OTP (Firebase/Gmail) + CAPTCHA strategies
- **Phase 3** — Streamlit UI dashboard
- **Phase 4** — Parallel execution + GitHub Actions + Docker
- **Phase 5** — Docs + polish
