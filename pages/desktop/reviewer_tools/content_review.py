from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.desktop.base import Base


class ContentReview(Base):
    URL_TEMPLATE = "reviewers/queue/content_review"

    # Current tab
    _content_review_tab_locator = (By.CSS_SELECTOR, ".selected")

    # Queue viewing
    _addon_column_locator = (By.CSS_SELECTOR, ".listing-header > th:nth-child(2)")
    _flags_column_locator = (By.CSS_SELECTOR, ".listing-header > th:nth-child(3)")
    _last_updated_column_locator = (By.CSS_SELECTOR, ".listing-header > th:nth-child(4)")
    _maliciousness_score_column_locator = (By.CSS_SELECTOR, ".listing-header > th:nth-child(5)")

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._content_review_tab_locator).is_displayed(),
            message="Content Review Page was not loaded",
        )
        return self

    # Queue Viewing --------------------------------------------------------

    @property
    def addon_column(self):
        return self.find_element(*self._addon_column_locator)

    @property
    def flag_column(self):
        return self.find_element(*self._flags_column_locator)

    @property
    def last_updated_column(self):
        return self.find_element(*self._last_updated_column_locator)

    @property
    def maliciousness_score(self):
        return self.find_element(*self._maliciousness_score_column_locator)

    # Assert Methods ----------------------------------------------------------

    def assert_queue_viewing_content_review(self):
        assert (
            self.addon_column.is_displayed(),
            "Add-on" in self.addon_column.text
        )
        assert (
            self.flag_column.is_displayed(),
            "Flags" in self.flag_column.text
        )
        assert (
            self.last_updated_column.is_displayed(),
            "Last Updated" in self.last_updated_column.text
        )
        assert (
            self.maliciousness_score.is_displayed(),
            "Maliciousness Score" in self.maliciousness_score.text
        )
