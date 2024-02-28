from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.desktop.base import Base
from pages.desktop.reviewer_tools.manual_review import ManualReview
from pages.desktop.reviewer_tools.content_review import ContentReview
from pages.desktop.reviewer_tools.reviewer_themes import ReviewerThemes


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
    _manual_review_link_locator = (By.XPATH, "//a[contains(text(),'Manual Review')]")
    _content_review_link_locator = (By.XPATH, "//a[contains(text(),'Content Review')]")
    _manual_review_log_link_locator = (By.XPATH, "//a[contains(text(),'Review Log')]")
    _addons_review_guide_locator = (By.XPATH, "//a[contains(text(),'Add-on Review Guide')]")
    _flagged_for_human_review_locator = (By.XPATH, "//a[contains(text(),'Flagged by MAD for Human Review')]")
    _themes_new_locator = (By.XPATH, "//a[contains(text(),'New')]")
    _themes_updates_locator = (By.XPATH, "//a[contains(text(),'Updates')]")
    _themes_review_log_locator = (By.XPATH, "//h3[contains(text(),'Themes')]/following-sibling::ul//a[contains(text(),'Review Log')]")
    _themes_review_guide_locator = (By.XPATH, "//h3[contains(text(),'Themes')]/following-sibling::ul//a[contains(text(),'Review Guide')]")
    _add_ons_pending_rejection_locator = (By.XPATH, "//h3[contains(text(),'Admin Tools')]/following-sibling::ul//a[contains(text(),'Add-ons Pending Rejection')]")

    # Footer section
    _mozilla_logo_footer_locator = (By.CSS_SELECTOR, ".Icon-mozilla")

    # Tab Navigation
    _manual_review_tab_locator = (By.CSS_SELECTOR, ".tabnav > li:nth-child(1) > a")
    _flagged_by_mad_for_human_review_tab_locator = (By.CSS_SELECTOR, ".tabnav > li:nth-child(2) > a")
    _new_tab_locator = (By.CSS_SELECTOR, ".tabnav > li:nth-child(3) > a")
    _updates_tab_locator = (By.CSS_SELECTOR, ".tabnav > li:nth-child(4) > a")
    _content_review_tab_locator = (By.CSS_SELECTOR, ".tabnav > li:nth-child(5) > a")
    _pending_rejection_tab_locator = (By.CSS_SELECTOR, ".tabnav > li:nth-child(6) > a")

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

    # Footer Section

    @property
    def mozilla_logo(self):
        return self.find_element(*self._mozilla_logo_footer_locator)

    # Interaction methods -------------------------------------------------
    def click_manual_review_link(self):
        self.find_element(*self._manual_review_link_locator).click()
        return ManualReview(self.driver, self.base_url).wait_for_page_to_load()

    def click_content_review_link(self):
        self.find_element(*self._content_review_link_locator).click()
        return ContentReview(self.driver, self.base_url).wait_for_page_to_load()

    def click_themes_new_link(self):
        self.find_element(*self._themes_new_locator).click()
        return ReviewerThemes(self.driver, self.base_url).wait_for_themes_new_page_to_load()

    def click_themes_updates_link(self):
        self.find_element(*self._themes_updates_locator).click()
        return ReviewerThemes(self.driver, self.base_url).wait_for_themes_update_page_to_load()


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
            self.content_review_tab.is_displayed(),
            "Content Review" in self.content_review_tab.text
        )
        assert (
            self.pending_rejection_tab.is_displayed(),
            "Pending Rejection" in self.pending_rejection_tab.text
        )