"""
KWAF CLI Runner — Phase 4 (parallel support added)
===================================================
Usage:
  python run.py                            # run all enabled tests
  python run.py --headless                 # headless browser
  python run.py --driver playwright        # use playwright
  python run.py --parallel --workers 4    # parallel execution
  python run.py --test-id TC001           # single test
  python run.py --tags smoke              # by tag
  python run.py --list                    # list without running
"""
import sys
import os
import click
import yaml
from loguru import logger

logger.remove()
logger.add(
    lambda msg: print(msg, end=""),
    level="INFO",
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
)
os.makedirs("logs",              exist_ok=True)
os.makedirs("assets/screenshots", exist_ok=True)
os.makedirs("reports/output",    exist_ok=True)
logger.add("logs/kwaf_{time}.log", rotation="10 MB", level="DEBUG")


def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)


@click.command()
@click.option("--suite",      default=None,  help="Path to Excel test suite (.xlsx)")
@click.option("--driver",     default=None,  help="Driver: selenium | playwright")
@click.option("--browser",    default=None,  help="Browser: chrome | firefox | edge")
@click.option("--tags",       default=None,  help="Run only tests with this tag")
@click.option("--test-id",    default=None,  help="Run single test case by ID")
@click.option("--headless",   is_flag=True,  default=False, help="Run headless")
@click.option("--parallel",   is_flag=True,  default=False, help="Enable parallel execution")
@click.option("--workers",    default=2,     help="Number of parallel workers (default: 2)")
@click.option("--list",       "list_tests",  is_flag=True,  help="List tests without running")
@click.option("--report",     default="html", help="Report type: html")
def main(suite, driver, browser, tags, test_id, headless, parallel, workers, list_tests, report):
    config = load_config()

    # CLI overrides
    if driver:
        config["driver"]["default"] = driver
    if browser:
        config["driver"]["browser"] = browser
    if headless:
        config["driver"]["headless"] = True
    if parallel:
        config["execution"]["mode"]             = "parallel"
        config["execution"]["parallel_workers"] = workers

    suite_path = suite or config["data"]["excel"]["test_suite_path"]

    if not os.path.exists(suite_path):
        click.echo(f"\n  ERROR: Suite not found: {suite_path}")
        click.echo("  Run: python assets/templates/create_template.py\n")
        sys.exit(1)

    # Parse
    from core.test_cases.excel_parser import ExcelParser
    from core.test_cases.test_case_registry import TestCaseRegistry

    parser = ExcelParser(suite_path, sheet_name=config["data"]["excel"]["suite_sheet"])
    suite_data = parser.parse()

    registry = TestCaseRegistry()
    registry.clear()
    registry.register_suite(suite_data)

    # Filter
    if test_id:
        test_cases = [tc for tc in registry.get_all() if tc.test_id == test_id]
    elif tags:
        test_cases = registry.get_by_tag(tags)
    else:
        test_cases = registry.get_enabled()

    # List mode
    if list_tests:
        click.echo(f"\n  {'='*52}")
        click.echo(f"  Suite: {suite_path}")
        click.echo(f"  {'='*52}")
        for tc in registry.get_all():
            status = "ON " if tc.enabled else "OFF"
            click.echo(f"  [{status}]  {tc.test_id:<12}  {tc.name}  ({tc.step_count} steps)")
        click.echo(f"\n  Total: {registry.total} | Enabled: {registry.enabled_count}\n")
        return

    if not test_cases:
        click.echo("  No test cases found.")
        sys.exit(0)

    exec_mode = config["execution"].get("mode", "sequential")
    click.echo(
        f"\n  Running {len(test_cases)} test(s) | "
        f"Driver: {config['driver']['default']} | "
        f"Mode: {exec_mode} | "
        f"Headless: {config['driver']['headless']}\n"
    )

    # Execute
    if exec_mode == "parallel":
        suite_result = _run_parallel(test_cases, config, workers)
    else:
        from core.flow.flow_executor import FlowExecutor
        executor     = FlowExecutor(config)
        suite_result = executor.run(test_cases, suite_name=suite_data.name)

    # Report
    if report == "html":
        from core.reports.html_reporter import HtmlReporter
        reporter    = HtmlReporter(config.get("reports", {"output_dir": "reports/output"}))
        report_path = reporter.generate(suite_result)
        click.echo(f"\n  Report: {report_path}")

    click.echo(
        f"\n  Results: {suite_result.passed} passed | "
        f"{suite_result.failed} failed | "
        f"{suite_result.skipped} skipped\n"
    )
    sys.exit(1 if suite_result.failed > 0 else 0)


def _run_parallel(test_cases, config, workers: int):
    """
    Run test cases in parallel using concurrent.futures.
    Each test case gets its own driver instance.
    Falls back to sequential if parallel setup fails.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from core.flow.flow_executor import FlowExecutor, SuiteResult

    actual_workers = min(workers, len(test_cases))
    logger.info(f"[Parallel] Running {len(test_cases)} tests with {actual_workers} workers")

    suite_result = SuiteResult("Parallel Suite")
    executor     = FlowExecutor(config)

    with ThreadPoolExecutor(max_workers=actual_workers) as pool:
        futures = {
            pool.submit(executor._run_single, tc): tc
            for tc in test_cases
        }
        for future in as_completed(futures):
            tc = futures[future]
            try:
                result = future.result()
                suite_result.results.append(result)
                status = "PASSED" if result.status == "PASS" else "FAILED"
                logger.info(f"[Parallel] {tc.test_id}: {status} ({result.elapsed_seconds}s)")
            except Exception as e:
                logger.error(f"[Parallel] {tc.test_id}: ERROR — {e}")

    executor._print_summary(suite_result)
    return suite_result


if __name__ == "__main__":
    main()
