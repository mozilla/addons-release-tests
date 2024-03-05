from selenium.webdriver.common.by import By
from pages.desktop.base import Base
from scripts import reusables


class ManualReviewLog(Base):
    URL_TEMPLATE = 'reviewers/review_log'

    _page_header_text_locator = (By.XPATH, "//h2[contains(text(),'Add-on Review Log')]")
    _no_results_text_locator = (By.CSS_SELECTOR, "p.no-results")
    _search_field_locator = (By.XPATH, "//input[@id='id_search']")
    _filter_button_locator = (By.XPATH, "//button[@type='submit']")
    _review_log_table_locator = (By.ID, 'log-listing')
    _review_log_table_date_locator = (By.XPATH, "//table[@id='log-listing']//th[contains(text(),'Date')]")
    _review_log_table_event_locator = (By.XPATH, "//table[@id='log-listing']//th[contains(text(),'Event')]")
    _review_log_table_reviewer_locator = (By.XPATH, "//table[@id='log-listing']//th[contains(text(),'Reviewer')]")
    _show_comments_first_row_locator = (By.CSS_SELECTOR, "a.comments.show")
    _hide_comments_first_row_locator = (By.XPATH, "a.comments.hide")

    # Interaction Methods ----------------------------------------------------------
    @property
    def page_header_text(self):
        return self.find_element(*self._page_header_text_locator)

    @property
    def no_results_text(self):
        return self.find_element(*self._no_results_text_locator)

    @property
    def search_field(self):
        return self.find_element(*self._search_field_locator)

    @property
    def filter_button(self):
        return self.find_element(*self._filter_button_locator)

    @property
    def review_log_table(self):
        return self.find_element(*self._review_log_table_locator)

    @property
    def review_log_table_date(self):
        return self.find_element(*self._review_log_table_date_locator)

    @property
    def review_log_table_event(self):
        return self.find_element(*self._review_log_table_event_locator)

    @property
    def review_log_table_reviewer(self):
        return self.find_element(*self._review_log_table_reviewer_locator)

    @property
    def show_comments_first_row(self):
        return self.find_element(*self._show_comments_first_row_locator)

    @property
    def hide_comments_first_row(self):
        return self.find_element(*self._hide_comments_first_row_locator)

    # Click Methods -----------------------------------------------------------
    def click_show_comments_first_row(self):
        return self.find_element(*self._show_comments_first_row_locator).click()

    def click_hide_comments_first_row(self):
        return self.find_element(*self.hide_comments_first_row).click()

    def click_filter_button(self):
        return self.find_element(*self._filter_button_locator).click()

    # Write in field methods -----------------------------------------------------
    def write_in_search_field(self, value):
        return self.find_element(*self._search_field_locator).send_keys(value)

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._page_header_text_locator).is_displayed(),
            message="Manual Review Log was not loaded",
        )
        assert "Add-on Review Log" in self.page_header_text.text
        return self

    # Assert Method
    def assert_review_page_elements(self):
        assert self.page_header_text.is_displayed(), "Page header text is not displayed"
        assert self.search_field.is_displayed(), "Search field is not displayed"
        assert self.filter_button.is_displayed(), "Filter button is not displayed"
        assert self.review_log_table.is_displayed(), "Review log table is not displayed"
        assert self.review_log_table_date.is_displayed(), "Review log table date is not displayed"
        assert self.review_log_table_event.is_displayed(), "Review log table event is not displayed"
        assert self.review_log_table_reviewer.is_displayed(), "Review log table reviewer is not displayed"
        assert self.show_comments_first_row.is_displayed(), "Show comments button for first row is not displayed"

    def assert_no_results_search(self, value):
        self.write_in_search_field(reusables.get_random_string(5))
        self.click_filter_button()
        self.wait.until(
            lambda _: self.find_element(*self._no_results_text_locator).is_displayed(),
            message="No results text did not appear",
        )
        assert value in self.no_results_text.text
