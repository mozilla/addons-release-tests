from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.desktop.base import Base


class ManualReview(Base):
    URL_TEMPLATE = "reviewers/queue/extension"

    # Tab Navigation
    _manual_review_tab_locator = (By.CSS_SELECTOR, ".tabnav > li:nth-child(1) > a")
    _flagged_by_mad_for_human_review_tab_locator = (By.CSS_SELECTOR, ".tabnav > li:nth-child(2) > a")
    _new_tab_locator = (By.CSS_SELECTOR, ".tabnav > li:nth-child(3) > a")
    _updates_tab_locator = (By.CSS_SELECTOR, ".tabnav > li:nth-child(4) > a")
    _content_review_tab_locator = (By.CSS_SELECTOR, ".tabnav > li:nth-child(5) > a")
    _pending_rejection_tab_locator = (By.CSS_SELECTOR, ".tabnav > li:nth-child(6) > a")

    # Queue Viewing
    _addon_column_locator = (By.CSS_SELECTOR, ".listing-header > th:nth-child(2)")
    _type_column_locator = (By.CSS_SELECTOR, ".listing-header > th:nth-child(3)")
    _due_date_column_locator = (By.CSS_SELECTOR, ".listing-header > th:nth-child(4)")
    _flag_column_locator = (By.CSS_SELECTOR, ".listing-header > th:nth-child(5)")
    _maliciousness_score_column_locator = (By.CSS_SELECTOR, ".listing-header > th:nth-child(6)")
    _addon_list_locator = (By.CSS_SELECTOR, "#addon-queue > tbody > tr")

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._manual_review_tab_locator).is_displayed(),
            message="Manual Review Page was not loaded",
        )
        return

    # Tab Navigation ----------------------------------------------------------
    @property
    def manual_review_tab(self):
        return self.find_element(*self._manual_review_tab_locator)

    @property
    def flagged_by_mad_for_human_review_tab(self):
        return self.find_element(*self._flagged_by_mad_for_human_review_tab_locator)

    @property
    def new_tab(self):
        return self.find_element(*self._new_tab_locator)

    @property
    def updates_tab(self):
        return self.find_element(*self._updates_tab_locator)

    @property
    def content_review_tab(self):
        return self.find_element(*self._content_review_tab_locator)

    @property
    def pending_rejection_tab(self):
        return self.find_element(*self._pending_rejection_tab_locator)

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

    def assert_tab_viewing(self):
        assert (
            self.manual_review_tab.is_displayed(),
            "Manual Review" in self.manual_review_tab.text
        )
        assert (
            self.flagged_by_mad_for_human_review_tab.is_displayed(),
            "Flagged by MAD for Human Review" in self.flagged_by_mad_for_human_review_tab.text
        )
        assert (
            self.new_tab.is_displayed(),
            "New" in self.new_tab.text
        )
        assert (
            self.updates_tab.is_displayed(),
            "Updates" in self.updates_tab.text
        )
        assert (
            self.flag_column.is_displayed(),
            "Flags" in self.flag_column.text
        )
        assert (
            self.pending_rejection_tab.is_displayed(),
            "Pending Rejection" in self.pending_rejection_tab.text
        )

    def assert_queue_viewing(self):
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
            self.manual_review_tab.is_displayed(),
            "Manual Review" in self.manual_review_tab.text
        )
        assert (
            self.manual_review_tab.is_displayed(),
            "Manual Review" in self.manual_review_tab.text
        )
        assert (
            self.maliciousness_score_column.is_displayed(),
            "Maliciousness Score" in self.maliciousness_score_column.text
        )