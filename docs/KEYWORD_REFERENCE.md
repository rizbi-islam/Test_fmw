# KWAF — Keyword Reference Guide

Complete reference for all 20 built-in keywords.

---

## How Keywords Work

Every keyword follows this pattern in Excel:

| TestCaseID | TestName | Enabled | StepNo | Keyword | Locator | Strategy | Value | Timeout |
|---|---|---|---|---|---|---|---|---|
| TC001 | Login | YES | 1 | NAVIGATE | | css | https://app.com | 10 |
| TC001 | Login | YES | 2 | TYPE | #email | css | {email} | 5 |

- **Locator** — CSS selector, XPath, ID, name, etc.
- **Strategy** — `css` / `xpath` / `id` / `name` / `class` / `link_text`
- **Value** — URL, text, variable `{name}`, or filename
- **Timeout** — seconds to wait (default: 10)

Variables use `{variable_name}` syntax and resolve from TestData sheet or context.

---

## Navigation Keywords

### NAVIGATE
Go to a URL.
```
Keyword:  NAVIGATE
Value:    https://example.com  OR  {base_url}/login
```

### VERIFY_URL
Wait until URL contains expected text.
```
Keyword:  VERIFY_URL
Value:    dashboard
Timeout:  10
```

---

## Input Keywords

### TYPE
Clear a field and type text.
```
Keyword:  TYPE
Locator:  #email
Strategy: css
Value:    {email}    (resolves from TestData)
```

### CLEAR
Clear an input field without typing.
```
Keyword:  CLEAR
Locator:  #search-box
```

### SELECT
Choose a dropdown option.
```
Keyword:     SELECT
Locator:     #country
Value:       Bangladesh
select_by:   text   (or value)
```

---

## Click & Interaction Keywords

### CLICK
Click any element.
```
Keyword:  CLICK
Locator:  #submit-btn
Strategy: css
```

### HOVER
Move mouse over element (for dropdowns, tooltips).
```
Keyword:  HOVER
Locator:  #menu-item
```

### SCROLL_TO
Scroll to an element or page direction.
```
Keyword:  SCROLL_TO
Locator:  #footer-section     (scroll to element)
— OR —
Value:    bottom               (scroll to page bottom)
Value:    top                  (scroll to page top)
```

---

## Wait Keywords

### WAIT_FOR
Wait until element is visible.
```
Keyword:  WAIT_FOR
Locator:  #loading-complete
Timeout:  15
```

### SLEEP
Hard pause for N seconds. Use sparingly.
```
Keyword:  SLEEP
Value:    2
```

---

## Assertion Keywords

### ASSERT_TEXT
Assert element contains expected text.
```
Keyword:  ASSERT_TEXT
Locator:  h1
Value:    Welcome, John
```

### ASSERT_VISIBLE
Assert element exists and is visible.
```
Keyword:  ASSERT_VISIBLE
Locator:  #success-message
```

### ASSERT_URL
Assert current URL contains text.
```
Keyword:  ASSERT_URL
Value:    /dashboard
```

---

## Data Keywords

### GET_TEXT
Read element text and store in a context variable.
```
Keyword:  GET_TEXT
Locator:  #order-number
Value:    order_id       (variable name to store in)
```
Later steps can use `{order_id}` to reference this value.

---

## Screenshot Keyword

### SCREENSHOT
Take a screenshot and save it.
```
Keyword:  SCREENSHOT
Value:    login_success.png    (filename, optional)
```
Screenshots are saved to `assets/screenshots/`.

---

## Frame Keywords

### SWITCH_FRAME
Switch browser context into an iframe.
```
Keyword:  SWITCH_FRAME
Locator:  #payment-iframe
```

### SWITCH_DEFAULT
Switch back to main page from iframe.
```
Keyword:  SWITCH_DEFAULT
```

---

## Browser Keywords

### CLOSE_BROWSER
Close the browser at the end of a test.
```
Keyword:  CLOSE_BROWSER
```

---

## OTP Keywords

### HANDLE_OTP
Get OTP from configured source and type into field.
```
Keyword:  HANDLE_OTP
Locator:  #otp-input
Value:    mock        (or firebase / gmail)
Timeout:  30
```

Configure OTP source in `config/config.yaml` under `otp:` section.

**Mock OTP** (for test environments):
```yaml
otp:
  default: mock
  mock:
    otp_value: "123456"
```

**Firebase OTP** (free, real-time):
```yaml
otp:
  default: firebase
  firebase:
    credentials_path: config/firebase_credentials.json
    database_url: https://your-project.firebaseio.com
    otp_path: otp/device1
```

**Gmail IMAP OTP**:
```yaml
otp:
  default: gmail
  gmail:
    email: test@gmail.com
    app_password: "xxxx xxxx xxxx xxxx"
    subject_filter: "Your OTP"
```

---

## CAPTCHA Keywords

### HANDLE_CAPTCHA
Solve or bypass CAPTCHA.
```
Keyword:  HANDLE_CAPTCHA
Value:    bypass       (or twocaptcha / manual)
```

Configure in `config/config.yaml` under `captcha:` section.

---

## Locator Strategy Guide

| Strategy | Example | When to use |
|---|---|---|
| `css` | `#email`, `.btn-primary`, `input[type="email"]` | Default — fastest, most reliable |
| `xpath` | `//input[@name="email"]` | Complex conditions, text matching |
| `id` | `email` | When element has a unique id |
| `name` | `email` | Form input name attribute |
| `class` | `btn-primary` | Single class (avoid for shared classes) |
| `link_text` | `Click Here` | Exact anchor text |
| `partial_link` | `Click` | Partial anchor text |

---

## Variable System

Variables let you reference test data without hardcoding values.

**Define in TestData sheet:**
| RowID | email | password | base_url |
|---|---|---|---|
| row1 | user@test.com | Pass@123 | https://staging.app.com |

**Use in TestSuite with `{variable_name}`:**
```
Value: {email}        → resolves to "user@test.com"
Value: {base_url}/login  → resolves to "https://staging.app.com/login"
```

**Variables set during execution** (via GET_TEXT):
```
Step 1: GET_TEXT  #order-number  →  stored as {order_number}
Step 2: ASSERT_TEXT  #confirm   →  value = {order_number}
```

---

## Multi-Page Flow Example

```
StepNo | Keyword      | Locator         | Value
1      | NAVIGATE     |                 | {base_url}/login
2      | TYPE         | #email          | {email}
3      | TYPE         | #password       | {password}
4      | CLICK        | #login-btn      |
5      | VERIFY_URL   |                 | /dashboard
6      | ASSERT_TEXT  | .welcome-msg    | Welcome
7      | CLICK        | #new-order      |
8      | VERIFY_URL   |                 | /orders/new
9      | TYPE         | #product-name   | {product}
10     | CLICK        | #submit-order   |
11     | ASSERT_URL   |                 | /orders/success
12     | SCREENSHOT   |                 | order_success.png
```

---

## OTP Flow Example

```
StepNo | Keyword      | Locator         | Value
1      | NAVIGATE     |                 | {base_url}/login
2      | TYPE         | #phone          | {phone}
3      | CLICK        | #send-otp       |
4      | SLEEP        |                 | 2
5      | HANDLE_OTP   | #otp-input      | firebase
6      | CLICK        | #verify-btn     |
7      | VERIFY_URL   |                 | /dashboard
```
