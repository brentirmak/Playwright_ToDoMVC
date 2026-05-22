import pytest
import time

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