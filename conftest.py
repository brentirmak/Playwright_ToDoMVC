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
    Determine the logical browser name used for the test.

    Priority:

    1. Jenkins BROWSER_TYPE environment variable
    2. Local pytest --browser-type option
    3. Playwright --browser option
    4. Playwright --browser-channel option
    5. Unknown

    Examples:

        pytest --browser chromium
            -> Chrome

        pytest --browser firefox
            -> Firefox

        pytest --browser chromium --browser-channel msedge
            -> Edge

        BROWSER_TYPE=Chrome pytest --browser chromium
            -> Chrome
    """

    # -------------------------------------------------------------------------
    # 1. Jenkins/environment override
    # -------------------------------------------------------------------------

    env_browser = os.getenv("BROWSER_TYPE")

    if env_browser:
        return env_browser.strip()


    # -------------------------------------------------------------------------
    # 2. Explicit pytest --browser-type option
    # -------------------------------------------------------------------------

    if item is not None:

        try:
            cli_browser_type = item.config.getoption(
                "--browser-type"
            )

            if cli_browser_type:
                return cli_browser_type.strip()

        except Exception:
            pass


    # -------------------------------------------------------------------------
    # 3. Detect Playwright browser configuration
    # -------------------------------------------------------------------------

    if item is not None:

        try:

            browser = item.config.getoption("--browser")

            browser_channel = item.config.getoption(
                "--browser-channel"
            )

            # Firefox
            if browser == "firefox":
                return "Firefox"

            # WebKit
            if browser == "webkit":
                return "WebKit"

            # Chromium
            if browser == "chromium":

                # Microsoft Edge
                if browser_channel == "msedge":
                    return "Edge"

                # Standard Chromium configuration
                return "Chrome"

        except Exception:
            pass


    # -------------------------------------------------------------------------
    # 4. Unknown
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