import os
import time

import pytest
from dotenv import load_dotenv

from utils.db import MySQLLogger


# =============================================================================
# LOAD ENVIRONMENT VARIABLES
# =============================================================================

load_dotenv()


# =============================================================================
# MYSQL CONFIGURATION
# =============================================================================

mysql_url = os.getenv("MYSQL_URL")
mysql_username = os.getenv("MYSQL_USERNAME")
mysql_password = os.getenv("MYSQL_PASSWORD")


# =============================================================================
# PYTEST OPTIONS
# =============================================================================

def pytest_addoption(parser):
    """
    Add custom pytest command-line options.
    """

    parser.addoption(
        "--browser-type",
        action="store",
        default=None,
        help="Logical browser name for MySQL logging: Chrome, Firefox, Edge, WebKit",
    )


# =============================================================================
# BROWSER TYPE DETECTION
# =============================================================================

def get_browser_type(item=None):
    """
    Determine the actual browser being used by Playwright.

    Priority:
        1. Jenkins BROWSER_TYPE environment variable
        2. Explicit pytest --browser-type option
        3. Actual Playwright browser fixture
        4. Playwright browser/channel configuration
        5. Unknown
    """

    # -------------------------------------------------------------------------
    # 1. Jenkins override
    # -------------------------------------------------------------------------

    env_browser = os.getenv("BROWSER_TYPE")

    if env_browser:
        return env_browser.strip()


    # -------------------------------------------------------------------------
    # 2. Explicit --browser-type
    # -------------------------------------------------------------------------

    if item is not None:

        try:
            cli_browser_type = item.config.getoption("--browser-type")

            if cli_browser_type:
                return cli_browser_type.strip()

        except Exception:
            pass


    # -------------------------------------------------------------------------
    # 3. Inspect the actual Playwright browser fixture
    # -------------------------------------------------------------------------

    if item is not None:

        try:
            browser = item.funcargs.get("browser")

            if browser is not None:

                # Get the actual Playwright browser type.
                browser_name = browser.browser_type.name

                # Chromium-based browser
                if browser_name == "chromium":

                    # Check whether this is Microsoft Edge.
                    launch_args = item.funcargs.get(
                        "browser_type_launch_args"
                    )

                    if launch_args:

                        channel = launch_args.get("channel")

                        if channel == "msedge":
                            return "Edge"

                    return "Chrome"


                # Firefox
                if browser_name == "firefox":
                    return "Firefox"


                # WebKit
                if browser_name == "webkit":
                    return "WebKit"

        except Exception as exc:
            print(
                f"[WARNING] Could not determine browser from "
                f"Playwright fixture: {exc}"
            )


    # -------------------------------------------------------------------------
    # 4. Fall back to pytest command-line options
    # -------------------------------------------------------------------------

    if item is not None:

        try:

            browser = item.config.getoption("--browser")

            browser_channel = item.config.getoption(
                "--browser-channel"
            )

            if browser == "firefox":
                return "Firefox"

            if browser == "webkit":
                return "WebKit"

            if browser == "chromium":

                if browser_channel == "msedge":
                    return "Edge"

                return "Chrome"

        except Exception:
            pass


    # -------------------------------------------------------------------------
    # 5. Nothing could be determined
    # -------------------------------------------------------------------------

    return "Unknown"
# =============================================================================
# BROWSER CONTEXT FIXTURE
# =============================================================================

@pytest.fixture(scope="class")
def browser_context(browser):
    """
    Create one browser context for the test class.
    """

    context = browser.new_context()

    yield context

    context.close()


# =============================================================================
# SHARED PAGE FIXTURE
# =============================================================================

@pytest.fixture(scope="class")
def shared_page(browser_context):
    """
    Create one shared Playwright page for the test class.
    """

    page = browser_context.new_page()

    yield page

    page.close()


# =============================================================================
# SLOW TEST FIXTURE
# =============================================================================

@pytest.fixture(autouse=True)
def slow_every_test():
    """
    Pause briefly after every test.
    """

    yield

    time.sleep(1)


# =============================================================================
# MYSQL LOGGER FIXTURE
# =============================================================================

@pytest.fixture(scope="session")
def db_logger():
    """
    Create one MySQL logger for the entire pytest session.
    """

    if not mysql_url:
        pytest.fail(
            "MYSQL_URL is not configured."
        )

    if not mysql_username:
        pytest.fail(
            "MYSQL_USERNAME is not configured."
        )

    if not mysql_password:
        pytest.fail(
            "MYSQL_PASSWORD is not configured."
        )

    logger = MySQLLogger(
        host=mysql_url,
        user=mysql_username,
        password=mysql_password,
        database="playwright",
    )

    yield logger

    logger.close()


# =============================================================================
# TEST RESULT DATABASE LOGGING
# =============================================================================

def pytest_runtest_makereport(item, call):
    """
    Runs after each pytest test phase.

    Only the actual test-call phase is recorded in MySQL.
    """

    if call.when != "call":
        return


    # -------------------------------------------------------------------------
    # Get MySQL logger
    # -------------------------------------------------------------------------

    db_logger = item.funcargs.get("db_logger")

    if not db_logger:
        return


    # -------------------------------------------------------------------------
    # Test information
    # -------------------------------------------------------------------------

    test_name = item.name

    status = (
        "passed"
        if call.excinfo is None
        else "failed"
    )

    duration = call.stop - call.start

    error_message = (
        str(call.excinfo.value)
        if call.excinfo
        else None
    )


    # -------------------------------------------------------------------------
    # Determine browser
    # -------------------------------------------------------------------------

    browser_type = get_browser_type(item)


    # -------------------------------------------------------------------------
    # Log result
    # -------------------------------------------------------------------------

    db_logger.log_result(
        test_name=test_name,
        browser_type=browser_type,
        status=status,
        duration=duration,
        error_message=error_message,
    )


# =============================================================================
# TODOMVC FLOW FAILURE HANDLING
# =============================================================================

def pytest_runtest_setup(item):
    """
    If a previous ToDoMVC flow test has failed, skip subsequent
    flow tests.
    """

    if getattr(
        item.session,
        "_todo_flow_failed",
        False
    ):

        if "TestToDoMVCFlow" in item.nodeid:

            pytest.skip(
                "Skipping: earlier step in flow failed"
            )