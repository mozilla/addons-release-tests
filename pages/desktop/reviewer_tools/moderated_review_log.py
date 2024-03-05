from selenium.webdriver.common.by import By
from pages.desktop.base import Base
from pages.desktop.reviewer_tools.log_details import LogDetails
from selenium.webdriver.support import expected_conditions as EC
from scripts import reusables
from selenium.webdriver.support.select import Select


class ModeratedReviewLog(Base):
    URL_TEMPLATE = "reviewers/moderationlog"

    _moderated_review_log_text_locator = (By.XPATH, "//h2[contains(text(),'Moderated Review Log')]")
    _table_date_column_locator = (By.XPATH, "//table[@class='data-grid']//th[contains(text(),'Date')]")
    _table_event_column_locator = (By.XPATH, "//table[@class='data-grid']//th[contains(text(),'Event')]")
    _select_filter_type_locator = (By.CSS_SELECTOR, "select#id_filter")
    _filter_button_locator = (By.XPATH, "//button[@type='submit']")
    _more_details_list_locator = (By.XPATH, "//a[@class='more-details']")

    # Interaction Methods -----------------------------------------------------------------------

    @property
    def moderated_review_log_text(self):
        return self.find_element(*self._moderated_review_log_text_locator)

    @property
    def table_date_column(self):
        return self.find_element(*self._table_date_column_locator)

    @property
    def table_event_column(self):
        return self.find_element(*self._table_event_column_locator)

    @property
    def select_filter_type(self):
        return self.find_element(*self._select_filter_type_locator)

    @property
    def filter_button(self):
        return self.find_element(*self._filter_button_locator)

    @property
    def more_details_list(self):
        return self.find_element(*self._more_details_list_locator)

    # Click methods -------------------------------------------------------------
    def click_more_details_link(self):
        self.find_element(*self._more_details_list_locator).click()
        return LogDetails(self.driver, self.base_url).wait_for_page_to_load()

    def moderated_action_picker(self, value):
        self.wait.until(EC.visibility_of_element_located(self._select_filter_type_locator))
        select = Select(self.find_element(*self._select_filter_type_locator))
        select.select_by_visible_text(value)

    # Assert Method ---------------------------------------------------------------------------
    def assert_moderated_review_log_page_elements(self):
        assert self.moderated_review_log_text.is_displayed(), "Moderated review log text is not displayed"
        assert self.table_date_column.is_displayed(), "Table date column is not displayed"
        assert self.table_event_column.is_displayed(), "Table event column is not displayed"
        assert self.select_filter_type.is_displayed(), "Select filter type is not displayed"
        assert self.filter_button.is_displayed(), "Filter button is not displayed"
        assert self.more_details_list.is_displayed(), "More details list is not displayed"

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._moderated_review_log_text_locator).is_displayed(),
            message="Moderated Review Log was not loaded",
        )
        assert "Moderated Review Log" in self.moderated_review_log_text.text
        return self
