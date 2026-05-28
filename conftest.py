import pytest
import time
from db import MySQLLogger
from dotenv import load_dotenv
import os

# 1. Load the environment variables from the .env file
load_dotenv()

# 2. Retrieve the secrets using os.getenv()
webdriver_remote_url = os.getenv("MYSQL_URL")
webdriver_username = os.getenv("MYSQL_USERNAME")
webdriver_password = os.getenv("MYSQL_PASSWORD")

@pytest.fixture(scope="class")
def browser_context(browser):
    context = browser.new_context()
    yield context
    context.close()

@pytest.fixture(scope="class")
def shared_page(browser_context):
    page = browser_context.new_page()
    yield page
    page.close()

@pytest.fixture(autouse=True)
def slow_every_test():
    yield
    time.sleep(1)

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

def pytest_runtest_makereport(item, call):
    """Hook that runs after each test phase."""
    if call.when == "call":  # Only log the test execution phase
        db_logger = item.funcargs.get("db_logger")
        if not db_logger:
            return

        test_name = item.name
        status = "passed" if call.excinfo is None else "failed"
        duration = call.stop - call.start
        error_message = str(call.excinfo.value) if call.excinfo else None

        db_logger.log_result(test_name, status, duration, error_message)