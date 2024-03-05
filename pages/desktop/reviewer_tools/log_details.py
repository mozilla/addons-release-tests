from selenium.webdriver.common.by import By
from pages.desktop.base import Base


class LogDetails(Base):
    _log_details_text_locator = (By.XPATH, "//h2[contains(text(),'Log details')]")

    _review_author_text_locator = (By.XPATH, "//dt[contains(text(),'Review Author')]")
    _addon_title_text_locator = (By.XPATH, "//dt[contains(text(),'Add-on Title')]")
    _review_text_locator = (By.XPATH, "//dt[contains(text(),'Review Text')]")
    _undelete_button_locator = (By.CSS_SELECTOR, "input#submit-undelete-review")

    # Log details section interaction methods

    @property
    def log_details_text(self):
        return self.find_element(*self._log_details_text_locator)

    @property
    def review_author_text(self):
        return self.find_element(*self._review_author_text_locator)

    @property
    def addon_title_text(self):
        return self.find_element(*self._addon_title_text_locator)

    @property
    def review_text(self):
        return self.find_element(*self._review_text_locator)

    @property
    def undelete_button(self):
        return self.find_element(*self._undelete_button_locator)

    # Assert Method
    def assert_log_details_section_elements(self):
        assert self.review_author_text.is_displayed(), "Review author text is not displayed"
        assert self.addon_title_text.is_displayed(), "Addon title text is not displayed"
        assert self.review_text.is_displayed(), "Review text is not displayed"
        assert self.undelete_button.is_displayed(), "Undelete button is not displayed"

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._log_details_text_locator).is_displayed(),
            message="Log details was not loaded",
        )
        assert "Log details" in self.log_details_text.text
        return self
