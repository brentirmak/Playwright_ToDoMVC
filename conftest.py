import os
import time

import pytest
from dotenv import load_dotenv

from utils.db import MySQLLogger


# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------

load_dotenv()

mysql_url = os.getenv("MYSQL_URL")
mysql_username = os.getenv("MYSQL_USERNAME")
mysql_password = os.getenv("MYSQL_PASSWORD")


# ---------------------------------------------------------------------------
# Playwright fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="class")
def browser_context(browser):
    """
    Create one browser context for the entire test class.

    All tests in TestToDoMVCFlow therefore share the same browser context.
    """
    context = browser.new_context()

    yield context

    context.close()


@pytest.fixture(scope="class")
def shared_page(browser_context):
    """
    Create one Playwright page for the entire test class.

    This is intentional because the TodoMVC tests form a sequential flow:

        test_01 -> test_02 -> test_03 -> ... -> test_08

    Each test builds on the state created by the previous test.
    """
    page = browser_context.new_page()

    yield page

    page.close()


# ---------------------------------------------------------------------------
# Test pacing
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def slow_every_test():
    """
    Add a short delay after every test.

    This can make local execution easier to observe and debug.
    """
    yield

    time.sleep(1)


# ---------------------------------------------------------------------------
# MySQL logging
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def db_logger():
    """
    Create one MySQL logger for the entire pytest session.
    """
    logger = MySQLLogger(
        host=mysql_url,
        user=mysql_username,
        password=mysql_password,
        database="playwright",
    )

    yield logger

    logger.close()


# ---------------------------------------------------------------------------
# Test result logging
# ---------------------------------------------------------------------------

def pytest_runtest_makereport(item, call):
    """
    Log the result of each test execution to MySQL.

    Only the actual test-call phase is logged.
    Fixture setup/teardown is not logged as a separate test result.
    """

    if call.when != "call":
        return

    db_logger = item.funcargs.get("db_logger")

    if not db_logger:
        return

    test_name = item.name

    status = "passed" if call.excinfo is None else "failed"

    duration = call.stop - call.start

    error_message = (
        str(call.excinfo.value)
        if call.excinfo
        else None
    )

    db_logger.log_result(
        test_name=test_name,
        status=status,
        duration=duration,
        error_message=error_message,
    )

    # -----------------------------------------------------------------------
    # Mark the sequential TodoMVC flow as failed.
    #
    # If one test fails, subsequent tests in TestToDoMVCFlow will be skipped.
    # -----------------------------------------------------------------------

    if call.excinfo is not None:
        if "TestToDoMVCFlow" in item.nodeid:
            item.session._todo_flow_failed = True


# ---------------------------------------------------------------------------
# Sequential TodoMVC flow handling
# ---------------------------------------------------------------------------

def pytest_runtest_setup(item):
    """
    Stop the sequential TodoMVC flow after the first failure.

    Because all tests share the same Playwright page, continuing after an
    earlier failure could cause misleading downstream failures.
    """

    if getattr(item.session, "_todo_flow_failed", False):

        if "TestToDoMVCFlow" in item.nodeid:
            pytest.skip(
                "Skipping: earlier step in TestToDoMVCFlow failed"
            )