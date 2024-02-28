from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.desktop.base import Base


class ManualReview(Base):
    URL_TEMPLATE = "reviewers/queue/extension"

    # Tab Navigation
    _manual_review_tab_locator = (By.XPATH, "//li[@class='selected']//a[contains(text(),'Manual Review')]")

    # Queue Viewing
    _addon_column_locator = (By.XPATH, "//th[contains(text(),'Add-on')]")
    _type_column_locator = (By.XPATH, "//th[contains(text(),'Type')]")
    _due_date_column_locator = (By.XPATH, "//a[contains(text(),'Due Date')]")
    _flag_column_locator = (By.XPATH, "//th[contains(text(),'Flags')]")
    _maliciousness_score_column_locator = (By.XPATH, "//a[contains(text(),'Maliciousness Score')]")
    _addon_list_locator = (By.CSS_SELECTOR, "#addon-queue > tbody > tr")

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._manual_review_tab_locator).is_displayed(),
            message="Manual Review Page was not loaded",
        )
        return self

    # Queue Viewing --------------------------------------------------------

    @property
    def addon_column(self):
        return self.find_element(*self._addon_column_locator)

    @property
    def type_column(self):
        return self.find_element(*self._type_column_locator)

    @property
    def due_date_column(self):
        return self.find_element(*self._due_date_column_locator)

    @property
    def flag_column(self):
        return self.find_element(*self._flag_column_locator)

    @property
    def maliciousness_score_column(self):
        return self.find_element(*self._maliciousness_score_column_locator)

    @property
    def addon_list(self):
        return self.find_element(*self._addon_list_locator)

    # Assert Methods ----------------------------------------------------------

    def assert_queue_viewing_manual_review(self):
        assert (
            self.addon_column.is_displayed(),
            "Add-on" in self.addon_column.text
        )
        assert (
            self.type_column.is_displayed(),
            "Type" in self.type_column.text
        )
        assert (
            self.due_date_column.is_displayed(),
            "Due Date" in self.due_date_column.text
        )
        assert (
            self.flag_column.is_displayed(),
            "Flags" in self.flag_column.text
        )
        assert (
            self.maliciousness_score_column.is_displayed(),
            "Maliciousness Score" in self.maliciousness_score_column.text
        )