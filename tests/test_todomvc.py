import pytest
from playwright.sync_api import expect

from pages.todomvc_page import TodoMVCPage


@pytest.mark.usefixtures("slow_every_test")
@pytest.mark.usefixtures("shared_page")
class TestToDoMVCFlow:
    """
    Sequential TodoMVC test flow.

    All tests intentionally use the same Playwright page.

    Test sequence:

        01. Open homepage
        02. Add Exercise
        03. Add Grocery Shopping
        04. Add Study
        05. Add Walk the dog
        06. Complete Grocery Shopping and Study
        07. Clear completed items
        08. Rename Exercise to Play Soccer
    """

    # -----------------------------------------------------------------------
    # Test 01 - Homepage
    # -----------------------------------------------------------------------

    def test_01_homepage(self, shared_page, db_logger):
        print("\nStarting test_01_homepage transaction")
        todo = TodoMVCPage(shared_page)

        print("\nWill open the ToDoMVC homepage")
        todo.open()

        expect(todo.text_input).to_be_visible()
        print("ToDoMVC homepage is visible")
        print("Ended test_01_homepage transaction")

    # -----------------------------------------------------------------------
    # Test 02 - Add Exercise
    # -----------------------------------------------------------------------

    def test_02_enter_exercise_item(self, shared_page, db_logger):
        print("\nStarting test_02_enter_exercise_item transaction")   
        todo = TodoMVCPage(shared_page)

        print("Will add Exercise item")
        todo.add_item_with_double_click("Exercise")
        print("Exercise item added")

        expect(todo.footer).to_contain_text(
            "1 item left"
        )
        print("Verified - 1 item left")
        print("Ended test_02_enter_exercise_item transaction")

    # -----------------------------------------------------------------------
    # Test 03 - Add Grocery Shopping
    # -----------------------------------------------------------------------

    def test_03_enter_shopping_item(self, shared_page, db_logger):
        print("\nStarting test_03_enter_shopping_item transaction")
        todo = TodoMVCPage(shared_page)

        print("Will add Grocery Shopping item")
        todo.add_item("Grocery Shopping")
        print("Grocery Shopping item added")    

        expect(todo.footer).to_contain_text(
            "2 items left"
        )
        print("Verified - 2 items left")
        print("Ended test_03_enter_shopping_item transaction")

    # -----------------------------------------------------------------------
    # Test 04 - Add Study
    # -----------------------------------------------------------------------

    def test_04_enter_study_item(self, shared_page, db_logger):
        print("\nStarting test_04_enter_study_item transaction")
        todo = TodoMVCPage(shared_page)

        print("Will add Study item")
        todo.add_item("Study")
        print("Study item added")

        expect(todo.footer).to_contain_text(
            "3 items left"
        )
        print("Verified - 3 items left")
        print("Ended test_04_enter_study_item transaction")

    # -----------------------------------------------------------------------
    # Test 05 - Add Walk the dog
    # -----------------------------------------------------------------------

    def test_05_enter_walkthedog_item(self, shared_page, db_logger):
        print("\nStarting test_05_enter_walkthedog_item transaction")
        todo = TodoMVCPage(shared_page)

        print("Will add Walk the dog item")
        todo.add_item("Walk the dog")
        print("Walk the dog item added")

        expect(todo.footer).to_contain_text(
            "4 items left"
        )
        print("Verified - 4 items left")
        print("Ended test_05_enter_walkthedog_item transaction")

    # -----------------------------------------------------------------------
    # Test 06 - Complete items
    # -----------------------------------------------------------------------

    def test_06_complete_items(self, shared_page, db_logger):
        print("\nStarting test_06_complete_items transaction")
        todo = TodoMVCPage(shared_page)

        print("Will complete Grocery Shopping") 
        todo.complete_item("Grocery Shopping")
        print("Grocery Shopping completed")
        expect(todo.todo_list).to_match_aria_snapshot(
            "- text: Grocery Shopping"
        )
        print("Verified - Grocery Shopping completed")
        print("Will complete Study")
        todo.complete_item("Study")
        print("Study completed")

        expect(todo.todo_list).to_match_aria_snapshot(
            "- text: Study"
        )
        print("Verified - Study completed")
        print("Ended test_06_complete_items transaction")

    # -----------------------------------------------------------------------
    # Test 07 - Clear completed items
    # -----------------------------------------------------------------------

    def test_07_clear_items(self, shared_page, db_logger):
        print("\nStarting test_07_clear_items transaction")
        todo = TodoMVCPage(shared_page)

        print("Will clear completed items")
        todo.clear_completed()
        print("Completed items cleared")

        expect(todo.footer).to_contain_text(
            "2 items left"
        )
        print("Verified - 2 items left")
        print("Ended test_07_clear_items transaction")

    # -----------------------------------------------------------------------
    # Test 08 - Change Exercise to Play Soccer
    # -----------------------------------------------------------------------

    def test_08_change_exercise_item(self, shared_page, db_logger):
        print("\nStarting test_08_change_exercise_item transaction")
        todo = TodoMVCPage(shared_page)

        print("Will change Exercise to Play Soccer")
        todo.edit_item(
            current_item="Exercise",
            new_item="Play Soccer",
        )
        print("Exercise changed to Play Soccer")

        expect(
            todo.item("Play Soccer")
        ).to_be_visible()
        print("Verified - Play Soccer is visible")
        expect(
            todo.item_toggle("Play Soccer")
        ).to_be_visible()
        print("Verified - Play Soccer toggle is visible")
        print("Ended test_08_change_exercise_item transaction")