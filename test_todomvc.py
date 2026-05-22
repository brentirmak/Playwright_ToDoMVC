import re
from playwright.sync_api import Page, expect
import pytest

@pytest.mark.usefixtures("slow_every_test")
@pytest.mark.usefixtures("shared_page")
class TestToDoMVCFlow:
    def test_01_homepage(self, shared_page):
        shared_page.goto("https://todomvc.com/examples/react/dist/")
        expect(shared_page.get_by_test_id("text-input")).to_be_visible()

    def test_02_enter_exercise_item(self, shared_page):
        shared_page.get_by_test_id("text-input").dblclick()
        shared_page.get_by_test_id("text-input").fill("Exercise")
        shared_page.get_by_test_id("text-input").press("Enter")
        expect(shared_page.get_by_test_id("footer")).to_contain_text("1 item left")

    def test_03_enter_shopping_item(self, shared_page):
        shared_page.get_by_test_id("text-input").fill("Grocery Shopping")
        shared_page.get_by_test_id("text-input").press("Enter")
        expect(shared_page.get_by_test_id("footer")).to_contain_text("2 items left")

    def test_04_enter_study_item(self, shared_page):
        shared_page.get_by_test_id("text-input").fill("Study")
        shared_page.get_by_test_id("text-input").press("Enter")
        expect(shared_page.get_by_test_id("footer")).to_contain_text("3 items left")

    def test_05_enter_walkthedog_item(self, shared_page):
        shared_page.get_by_test_id("text-input").fill("Walk the dog")
        shared_page.get_by_test_id("text-input").press("Enter")
        expect(shared_page.get_by_test_id("footer")).to_contain_text("4 items left")

    def test_06_complete_items(self, shared_page):
        shared_page.get_by_role("listitem").filter(has_text="Grocery Shopping").get_by_test_id("todo-item-toggle").check()
        expect(shared_page.get_by_test_id("todo-list")).to_match_aria_snapshot("- text: Grocery Shopping")
        shared_page.get_by_role("listitem").filter(has_text="Study").get_by_test_id("todo-item-toggle").check()
        expect(shared_page.get_by_test_id("todo-list")).to_match_aria_snapshot("- text: Study")

    def test_07_clear_items(self, shared_page):
        shared_page.get_by_role("button", name="Clear completed").click()
        expect(shared_page.get_by_test_id("footer")).to_contain_text("2 items left")

    def test_08_change_exercise_item(self, shared_page):
        shared_page.get_by_text("Exercise").dblclick()
        shared_page.get_by_test_id("todo-list").get_by_test_id("text-input").fill("Play Soccer")
        shared_page.get_by_test_id("todo-list").get_by_test_id("text-input").press("Enter")
        expect(shared_page.get_by_text("Play Soccer")).to_be_visible()
        expect(shared_page.get_by_role("listitem").filter(has_text="Play Soccer").get_by_test_id("todo-item-toggle")).to_be_visible()

