import os
import time

import pytest
from dotenv import load_dotenv

from utils.db import MySQLLogger


###############################################################################
# LOAD ENVIRONMENT VARIABLES
###############################################################################

load_dotenv()


###############################################################################
# MYSQL CONFIGURATION
###############################################################################

webdriver_remote_url = os.getenv("MYSQL_URL")
webdriver_username = os.getenv("MYSQL_USERNAME")
webdriver_password = os.getenv("MYSQL_PASSWORD")


###############################################################################
# BROWSER TYPE
#
# This is supplied by Jenkins:
#
#   BROWSER_TYPE=Chrome
#   BROWSER_TYPE=Firefox
#   BROWSER_TYPE=Edge
#
###############################################################################

def get_browser_type():

    browser_type = os.getenv("BROWSER_TYPE", "Unknown")

    return browser_type


###############################################################################
# BROWSER CONTEXT
###############################################################################

@pytest.fixture(scope="class")
def browser_context(browser):

    context = browser.new_context()

    yield context

    context.close()


###############################################################################
# SHARED PAGE
###############################################################################

@pytest.fixture(scope="class")
def shared_page(browser_context):

    page = browser_context.new_page()

    yield page

    page.close()


###############################################################################
# SLOW TEST FIXTURE
###############################################################################

@pytest.fixture(autouse=True)
def slow_every_test():

    yield

    time.sleep(1)


###############################################################################
# MYSQL LOGGER
###############################################################################

@pytest.fixture(scope="session")
def db_logger():

    logger = MySQLLogger(
        host=webdriver_remote_url,
        user=webdriver_username,
        password=webdriver_password,
        database="playwright"
    )

    yield logger

    logger.close()


###############################################################################
# PYTEST RESULT HOOK
###############################################################################

def pytest_runtest_makereport(item, call):

    """
    Runs after each pytest test phase.

    Results are stored in MySQL with:

        test_name
        browser_type
        status
        duration
        error_message
        executed_at
    """

    if call.when != "call":
        return


    db_logger = item.funcargs.get("db_logger")

    if not db_logger:
        return


    ###########################################################################
    # TEST INFORMATION
    ###########################################################################

    test_name = item.name

    browser_type = get_browser_type()

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


    ###########################################################################
    # LOG RESULT
    ###########################################################################

    db_logger.log_result(
        test_name=test_name,
        browser_type=browser_type,
        status=status,
        duration=duration,
        error_message=error_message
    )


###############################################################################
# FLOW FAILURE HANDLING
###############################################################################

def pytest_runtest_setup(item):

    if getattr(item.session, "_todo_flow_failed", False):

        if "TestToDoMVCFlow" in item.nodeid:

            pytest.skip(
                "Skipping: earlier step in flow failed"
            )