from playwright.sync_api import Page


class TodoMVCPage:
    """
    Page Object for the TodoMVC React application.

    This class contains:
        - Locators
        - Navigation
        - User interactions

    Assertions remain in the test layer.
    """

    URL = "https://todomvc.com/examples/react/dist/"

    def __init__(self, page: Page):
        self.page = page

        # -------------------------------------------------------------------
        # Main page locators
        # -------------------------------------------------------------------

        self.text_input = page.get_by_test_id("text-input")

        self.footer = page.get_by_test_id("footer")

        self.todo_list = page.get_by_test_id("todo-list")

        self.clear_completed_button = page.get_by_role(
            "button",
            name="Clear completed",
        )

    # -----------------------------------------------------------------------
    # Navigation
    # -----------------------------------------------------------------------

    def open(self):
        """
        Navigate to the TodoMVC application.
        """
        self.page.goto(self.URL)

    # -----------------------------------------------------------------------
    # Todo creation
    # -----------------------------------------------------------------------

    def add_item(self, item: str):
        """
        Add a new TodoMVC item.

        Example:
            todo_page.add_item("Grocery Shopping")
        """
        self.text_input.fill(item)
        self.text_input.press("Enter")

    def add_item_with_double_click(self, item: str):
        """
        Add an item after double-clicking the input.

        This preserves the behavior from the original test_02.
        """
        self.text_input.dblclick()
        self.text_input.fill(item)
        self.text_input.press("Enter")

    # -----------------------------------------------------------------------
    # Todo completion
    # -----------------------------------------------------------------------

    def complete_item(self, item: str):
        """
        Mark a specific todo item as completed.
        """

        todo_item = self.page.get_by_role(
            "listitem"
        ).filter(
            has_text=item
        )

        todo_item.get_by_test_id(
            "todo-item-toggle"
        ).check()

    # -----------------------------------------------------------------------
    # Todo editing
    # -----------------------------------------------------------------------

    def edit_item(self, current_item: str, new_item: str):
        """
        Edit an existing todo item.
        """

        self.page.get_by_text(
            current_item
        ).dblclick()

        edit_input = self.todo_list.get_by_test_id(
            "text-input"
        )

        edit_input.fill(new_item)
        edit_input.press("Enter")

    # -----------------------------------------------------------------------
    # Completed items
    # -----------------------------------------------------------------------

    def clear_completed(self):
        """
        Remove all completed todo items.
        """
        self.clear_completed_button.click()

    # -----------------------------------------------------------------------
    # Convenience locators
    # -----------------------------------------------------------------------

    def item(self, item: str):
        """
        Return the locator for a specific todo item.

        This allows tests to make their own Playwright assertions.

        Example:
            expect(todo_page.item("Exercise")).to_be_visible()
        """

        return self.page.get_by_text(item)

    def item_toggle(self, item: str):
        """
        Return the checkbox/toggle locator for a specific todo item.

        Example:
            expect(
                todo_page.item_toggle("Play Soccer")
            ).to_be_visible()
        """

        return (
            self.page
            .get_by_role("listitem")
            .filter(has_text=item)
            .get_by_test_id("todo-item-toggle")
        )