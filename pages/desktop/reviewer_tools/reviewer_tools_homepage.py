from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.desktop.base import Base
from pages.desktop.reviewer_tools.manual_review import ManualReview


class ReviewerToolsHomepage(Base):
    URL_TEMPLATE = "reviewers/"

    # Header section
    _site_title_locator = (By.CSS_SELECTOR, ".site-title > a:nth-child(1) > strong")
    _user_header_locator = (By.CSS_SELECTOR, ".user")
    _tools_header_locator = (By.CSS_SELECTOR, ".tools")
    _back_to_addons_locator = (By.CSS_SELECTOR, ".return")

    # Announcement section
    _announcement_section_locator = (By.CSS_SELECTOR, ".featured.daily-message")

    # Reviewer tools section
    _manual_review_link_locator = (By.CSS_SELECTOR, ".listing > ul:nth-child(2) > li:nth-child(1) > a")
    _content_review_link_locator = (By.CSS_SELECTOR, ".listing > ul:nth-child(6) > li:nth-child(1) > a")
    _manual_review_log_link_locator = (By.CSS_SELECTOR, ".listing > ul:nth-child(2) > li:nth-child(2) > a")
    _addons_review_guide_locator = (By.CSS_SELECTOR, ".listing > ul:nth-child(2) > li:nth-child(3) > a")
    _flagged_for_human_review_locator = (By.CSS_SELECTOR, ".listing > ul:nth-child(4) > li:nth-child(1) > a")
    _themes_new_locator = (By.CSS_SELECTOR, ".listing > ul:nth-child(8) > li:nth-child(1) > a")
    _themes_updates_locator = (By.CSS_SELECTOR, ".listing > ul:nth-child(8) > li:nth-child(2) > a")
    _themes_review_log_locator = (By.CSS_SELECTOR, ".listing > ul:nth-child(8) > li:nth-child(3) > a")
    _themes_review_guide_locator = (By.CSS_SELECTOR, ".listing > ul:nth-child(8) > li:nth-child(4) > a")
    _add_ons_pending_rejection_locator = (By.CSS_SELECTOR, ".listing > ul:nth-child(10) > li:nth-child(1) > a")

    # Footer section
    _mozilla_logo_footer_locator = (By.CSS_SELECTOR, ".Icon-mozilla")

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._site_title_locator).is_displayed(),
            message="Reviewer Tools Homepage was not loaded",
        )
        return self

    # Header ---------------------------------------------------------
    @property
    def site_title(self):
        self.wait.until(
            EC.visibility_of_element_located(self._site_title_locator)
        )
        return self.find_element(*self._site_title_locator)

    @property
    def user_header(self):
        return self.find_element(*self._user_header_locator)

    @property
    def tools_header(self):
        return self.find_element(*self._tools_header_locator)

    # Announcement -----------------------------------------------------
    @property
    def announcement_section(self):
        return self.find_element(*self._announcement_section_locator)

    # Reviewer tools section -------------------------------------------
    @property
    def manual_review_link(self):
        return self.find_element(*self._manual_review_link_locator)

    @property
    def content_review_link(self):
        return self.find_element(*self._content_review_link_locator)

    @property
    def manual_review_log_link(self):
        return self.find_element(*self._manual_review_log_link_locator)

    @property
    def addons_review_guide(self):
        return self.find_element(*self._addons_review_guide_locator)

    @property
    def flagged_for_human_review(self):
        return self.find_element(*self._flagged_for_human_review_locator)

    @property
    def themes_new(self):
        return self.find_element(*self._themes_new_locator)

    @property
    def themes_updates(self):
        return self.find_element(*self._themes_updates_locator)

    @property
    def themes_review_log(self):
        return self.find_element(*self._themes_review_log_locator)

    @property
    def themes_review_guide(self):
        return self.find_element(*self._themes_review_guide_locator)

    @property
    def add_ons_pending_rejection(self):
        return self.find_element(*self._add_ons_pending_rejection_locator)

    # Footer Section

    @property
    def mozilla_logo(self):
        return self.find_element(*self._mozilla_logo_footer_locator)

    # Interaction methods -------------------------------------------------
    def click_manual_review_link(self):
        self.find_element(*self._manual_review_link_locator).click()
        return ManualReview(self.driver, self.base_url).wait_for_page_to_load()

    # Methods -------------------------------------------------------------
    def assert_reviewer_tools_section(self):
        assert (
            self.manual_review_link.is_displayed(),
            self.manual_review_log_link.is_displayed(),
            self.content_review_link.is_displayed(),
            self.addons_review_guide.is_displayed(),
            self.flagged_for_human_review.is_displayed(),
            self.themes_new.is_displayed(),
            self.themes_updates.is_displayed(),
            self.themes_review_log.is_displayed(),
            self.themes_review_guide.is_displayed(),
            self.add_ons_pending_rejection.is_displayed()
        )
