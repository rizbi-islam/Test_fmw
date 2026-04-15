"""
HTML Report Generator using Jinja2.
Produces a styled, self-contained HTML report with full test results.
Failed tests auto-expand. Screenshots are linked inline.
"""
import os
from datetime import datetime
from loguru import logger

from core.reports.base_reporter import BaseReporter

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KWAF Test Report</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f2f5;color:#333;font-size:14px}
  header{background:linear-gradient(135deg,#1a1a2e,#16213e);color:white;padding:24px 40px}
  header h1{font-size:22px;margin-bottom:4px}
  header p{opacity:.65;font-size:13px}
  .summary{display:flex;gap:12px;padding:20px 40px;background:white;border-bottom:1px solid #e8e8e8;flex-wrap:wrap}
  .stat{flex:1;min-width:100px;text-align:center;padding:14px 10px;border-radius:10px}
  .s-total{background:#e3f2fd;color:#1565c0}
  .s-pass{background:#e8f5e9;color:#1b5e20}
  .s-fail{background:#ffebee;color:#b71c1c}
  .s-skip{background:#fff8e1;color:#e65100}
  .stat .num{font-size:30px;font-weight:700}
  .stat .lbl{font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-top:3px}
  .content{padding:24px 40px;max-width:1200px;margin:0 auto}
  .tc-card{background:white;border-radius:10px;margin-bottom:14px;box-shadow:0 1px 4px rgba(0,0,0,.08);overflow:hidden}
  .tc-header{display:flex;align-items:center;padding:14px 18px;cursor:pointer;gap:12px;border-left:4px solid transparent}
  .tc-header:hover{background:#fafafa}
  .tc-header.PASS{border-left-color:#43a047}
  .tc-header.FAIL{border-left-color:#e53935}
  .tc-header.ERROR{border-left-color:#f57c00}
  .tc-header.SKIP{border-left-color:#fdd835}
  .badge{padding:3px 9px;border-radius:20px;font-size:11px;font-weight:700;text-transform:uppercase;flex-shrink:0}
  .badge-PASS{background:#e8f5e9;color:#2e7d32}
  .badge-FAIL{background:#ffebee;color:#c62828}
  .badge-ERROR{background:#fff3e0;color:#e65100}
  .badge-SKIP{background:#fff8e1;color:#f57f17}
  .tc-name{font-weight:600;flex:1}
  .tc-id{font-size:12px;color:#888;font-family:monospace}
  .tc-meta{font-size:12px;color:#aaa;flex-shrink:0}
  .steps{border-top:1px solid #f0f0f0}
  .step-row{display:flex;align-items:flex-start;padding:8px 18px;border-bottom:1px solid #f5f5f5;font-size:13px;gap:8px}
  .step-row:last-child{border-bottom:none}
  .step-row.PASS{background:#fdfffd}
  .step-row.FAIL{background:#fff6f6}
  .step-row.SKIP{background:#fffde7}
  .step-no{width:28px;font-weight:700;color:#ccc;flex-shrink:0;padding-top:1px}
  .step-kw{width:140px;font-family:monospace;font-size:12px;font-weight:600;color:#555;flex-shrink:0;padding-top:1px}
  .step-msg{flex:1;color:#444;word-break:break-word}
  .step-time{color:#bbb;font-size:11px;flex-shrink:0;padding-top:2px}
  .step-ss a{font-size:11px;color:#1565c0;text-decoration:none;padding:1px 6px;border:1px solid #1565c0;border-radius:3px}
  .tc-details{display:none}
  .tc-details.open{display:block}
  .chevron{font-size:12px;color:#ccc;transition:transform .2s;flex-shrink:0}
  .tc-details.open + .tc-header .chevron{transform:rotate(90deg)}
  footer{text-align:center;padding:20px;color:#aaa;font-size:12px;margin-top:10px}
  @media(max-width:600px){.content{padding:12px}.summary{padding:12px}}
</style>
</head>
<body>
<header>
  <h1>KWAF — Test Execution Report</h1>
  <p>Suite: {{ suite.suite_name }} &nbsp;&bull;&nbsp; Generated: {{ generated_at }}</p>
</header>
<div class="summary">
  <div class="stat s-total"><div class="num">{{ suite.total }}</div><div class="lbl">Total</div></div>
  <div class="stat s-pass"><div class="num">{{ suite.passed }}</div><div class="lbl">Passed</div></div>
  <div class="stat s-fail"><div class="num">{{ suite.failed }}</div><div class="lbl">Failed</div></div>
  <div class="stat s-skip"><div class="num">{{ suite.skipped }}</div><div class="lbl">Skipped</div></div>
</div>
<div class="content">
{% for result in suite.results %}
<div class="tc-card">
  <div class="tc-header {{ result.status }}" onclick="toggle('tc_{{ loop.index }}')">
    <span class="chevron">&#9654;</span>
    <span class="badge badge-{{ result.status }}">{{ result.status }}</span>
    <span class="tc-id">{{ result.test_id }}</span>
    <span class="tc-name">{{ result.test_name }}</span>
    <span class="tc-meta">{{ result.total_steps }} steps &nbsp;&bull;&nbsp; {{ result.elapsed_seconds }}s</span>
  </div>
  <div class="tc-details" id="tc_{{ loop.index }}">
    <div class="steps">
    {% for step in result.step_results %}
    <div class="step-row {{ step.status }}">
      <span class="step-no">#{{ step.step_no }}</span>
      <span class="step-kw">{{ step.keyword }}</span>
      <span class="step-msg">{{ step.message }}</span>
      {% if step.screenshot %}
      <span class="step-ss"><a href="{{ step.screenshot }}" target="_blank">screenshot</a></span>
      {% endif %}
      <span class="step-time">{{ step.elapsed_ms }}ms</span>
    </div>
    {% endfor %}
    {% if result.error_message %}
    <div class="step-row FAIL">
      <span class="step-no">ERR</span>
      <span class="step-kw">ERROR</span>
      <span class="step-msg" style="color:#c62828">{{ result.error_message }}</span>
    </div>
    {% endif %}
    </div>
  </div>
</div>
{% endfor %}
</div>
<footer>KWAF Automation Framework &nbsp;&bull;&nbsp; Phase 1 &nbsp;&bull;&nbsp; {{ generated_at }}</footer>
<script>
function toggle(id){
  const el=document.getElementById(id);
  el.classList.toggle('open');
}
document.addEventListener('DOMContentLoaded',function(){
  document.querySelectorAll('.badge-FAIL,.badge-ERROR').forEach(function(b){
    const card=b.closest('.tc-card');
    if(card){
      const details=card.querySelector('.tc-details');
      if(details) details.classList.add('open');
    }
  });
});
</script>
</body>
</html>
"""


class HtmlReporter(BaseReporter):
    """Generates self-contained styled HTML test report."""

    def generate(self, suite_result) -> str:
        from jinja2 import Template

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = suite_result.suite_name.replace(" ", "_").replace("/", "_")
        filename = f"report_{safe_name}_{ts}.html"
        filepath = os.path.join(self.output_dir, filename)

        # Proxy class to expose step dicts as attributes
        class StepProxy:
            def __init__(self, d):
                for k, v in d.items():
                    setattr(self, k, v)

        for result in suite_result.results:
            result.step_results = [StepProxy(s.to_dict()) for s in result.step_results]

        template = Template(HTML_TEMPLATE)
        html = template.render(
            suite=suite_result,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        logger.success(f"[HtmlReporter] Report -> {filepath}")
        return filepath
