from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.desktop.base import Base


class ReviewerThemes(Base):
    URL_TEMPLATE = "reviewers/queue/theme_new"

    _themes_new_locator = (By.XPATH, "//li[@class='selected']//a[contains(text(),'New')]")

    _addon_column_locator = (By.XPATH, "//th[contains(text(),'Add-on')]")
    _flags_column_locator = (By.XPATH, "//th[contains(text(),'Flags')]")
    _due_date_column_locator = (By.XPATH, "//th[contains(text(),'Due date')]")

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._themes_new_locator).is_displayed(),
            message="Themes New was not loaded",
        )
        return self

    @property
    def themes_selected(self):
        return self.find_element(*self._themes_new_locator)

    # Queue Viewing ----------------------------------------------------------

    @property
    def addon_column(self):
        return self.find_element(*self._addon_column_locator)

    @property
    def flags_column(self):
        return self.find_element(*self._flags_column_locator)

    @property
    def due_date_column(self):
        return self.find_element(*self._due_date_column_locator)

    # Assert Methods

    def assert_queue_viewing_themes_new(self):
        assert (
            self.addon_column.is_displayed(),
            "Add-on" in self.addon_column.text
        )
        assert (
            self.due_date_column.is_displayed(),
            "Due Date" in self.due_date_column.text
        )
        assert (
            self.flags_column.is_displayed(),
            "Flags" in self.flags_column.text
        )