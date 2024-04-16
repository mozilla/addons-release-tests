from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from pages.desktop.base import Base
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from scripts import reusables


class ContentReviewAddonPage(Base):
    URL_TEMPLATE = 'review/review-content'

    _addon_name_locator = (By.CSS_SELECTOR, '#addon-name > span:nth-child(2) > em')
    _approve_content_locator = (By.XPATH, "//label[contains(text(), 'Approve Content')]")
    _save_changes_locator = (By.CSS_SELECTOR, "div.review-actions-section:nth-child(16) > input")
    _reject_multiple_version_locator = (By.XPATH, "//label[contains(text(), 'Reject Multiple Versions')]")
    _content_approved_text = (By.XPATH, "//th[contains(text(), 'Content approved')]")
    _content_rejected_text = (By.XPATH, "th[contains(text(), 'Content rejected')]")
    _first_version_option_locator = (By.CSS_SELECTOR, "option.data-toggle")
    _first_review_action_locator = (By.CSS_SELECTOR, "#id_reasons_0")
    _select_versions_locator = (By.CSS_SELECTOR, "select.data-toggle")

    @property
    def addon_name(self):
        return self.find_element(*self._addon_name_locator)

    @property
    def approve_content(self):
        return self.find_element(*self._approve_content_locator)

    @property
    def reject_multiple_versions(self):
        return self.find_element(*self._reject_multiple_version_locator)

    @property
    def save_changes(self):
        return self.find_element(*self._save_changes_locator)

    @property
    def content_approved_text(self):
        self.wait.until(
            EC.visibility_of_element_located(self._content_approved_text)
        )
        return self.find_element(*self._content_approved_text)

    @property
    def content_rejected_text(self):
        self.wait.until(
            EC.visibility_of_element_located(self._content_rejected_text)
        )
        return self.find_element(*self._content_rejected_text)

    def click_approve_content(self):
        self.wait.until(
            EC.visibility_of_element_located(self._approve_content_locator)
        )
        self.find_element(*self._approve_content_locator).click()

    def click_reject_multiple_versions(self):
        self.wait.until(
            EC.visibility_of_element_located(self._reject_multiple_version_locator)
        )
        self.find_element(*self._reject_multiple_version_locator).click()

    def select_version_option(self):
        self.wait.until(
            EC.visibility_of_element_located(self._select_versions_locator)
        )
        option_element = self.driver.find_element(By.CSS_SELECTOR, "option.data-toggle")
        reusables.scroll_into_view(self.driver, option_element)
        option_element.click()

    def click_first_review_action(self):
        self.wait.until(
            EC.visibility_of_element_located(self._first_review_action_locator)
        )
        self.find_element(*self._first_review_action_locator).click()

    def click_save_changes(self):
        self.wait.until(
            EC.visibility_of_element_located(self._save_changes_locator)
        )
        self.find_element(*self._save_changes_locator).click()
        self.wait.until(
            EC.visibility_of_element_located(self._content_approved_text)
        )

    @staticmethod
    def open_content_review_addon_page(selenium, addon_string):
        return selenium.get(f"https://reviewers.addons.allizom.org/en-US/reviewers/review-content/{addon_string}")

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._addon_name_locator).is_displayed(),
            message="Content Review Page was not loaded",
        )
        return self
