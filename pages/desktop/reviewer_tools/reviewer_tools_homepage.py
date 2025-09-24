from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.desktop.base import Base
from pages.desktop.reviewer_tools.manual_review import ManualReview
from pages.desktop.reviewer_tools.content_review import ContentReview
from pages.desktop.reviewer_tools.reviewer_themes import ReviewerThemes
from pages.desktop.reviewer_tools.manual_review_log import ManualReviewLog
from pages.desktop.reviewer_tools.moderated_review_log import ModeratedReviewLog
from pages.desktop.reviewer_tools.ratings_awaiting_moderation import RatingsAwaitingModeration
from scripts import reusables


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
    _moderated_review_log_locator = (By.XPATH, "//h3[contains(text(),'User Ratings Moderation')]/following-sibling::ul//a[contains(text(),'Moderated Review Log')]")
    _content_review_link_locator = (By.XPATH, "//a[contains(text(),'Content Review')]")
    _manual_review_log_link_locator = (By.XPATH, "//h3[contains(text(),'Manual Review')]/following-sibling::ul//a[contains(text(),'Review Log')]")
    _addons_review_guide_locator = (By.XPATH, "//a[contains(text(),'Add-on Review Guide')]")
    _flagged_for_human_review_locator = (By.XPATH, "//a[contains(text(),'Flagged by MAD for Human Review')]")
    _themes_awaiting_review_locator = (By.XPATH, "//h3[contains(text(),'Themes')]/following-sibling::ul//a[contains(text(),'Awaiting Review')]")
    _themes_review_log_locator = (By.XPATH, "//h3[contains(text(),'Themes')]/following-sibling::ul//a[contains(text(),'Review Log')]")
    _themes_review_guide_locator = (By.XPATH, "//h3[contains(text(),'Themes')]/following-sibling::ul//a[contains(text(),'Review Guide')]")
    _add_ons_pending_rejection_locator = (By.XPATH, "//h3[contains(text(),'Admin Tools')]/following-sibling::ul//a[contains(text(),'Add-ons Pending Rejection')]")
    _user_ratings_moderation_guide_locator = (By.XPATH, "//h3[contains(text(),'User Ratings Moderation')]/following-sibling::ul//a[contains(text(),'Moderation Guide')]")
    _user_ratings_awaiting_moderation_locator = (By.XPATH, "//h3[contains(text(),'User Ratings Moderation')]/following-sibling::ul//a[contains(text(),'Ratings Awaiting Moderation')]")

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
    def themes_themes_awaiting_review(self):
        return self.find_element(*self._themes_awaiting_review_locator)

    @property
    def themes_review_log(self):
        return self.find_element(*self._themes_review_log_locator)

    @property
    def themes_review_guide(self):
        return self.find_element(*self._themes_review_guide_locator)

    @property
    def add_ons_pending_rejection(self):
        return self.find_element(*self._add_ons_pending_rejection_locator)

    @property
    def moderated_review_log(self):
        return self.find_element(*self._moderated_review_log_locator)

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

    @property
    def moderation_guide(self):
        return self.find_element(*self._user_ratings_moderation_guide_locator)

    @property
    def ratings_awaiting_moderation(self):
        return self.find_element(*self._user_ratings_awaiting_moderation_locator)

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

    def click_awaiting_review_link(self):
        self.find_element(*self._themes_awaiting_review_locator).click()
        return ReviewerThemes(self.driver, self.base_url).wait_for_themes_page_to_load()

    def click_manual_review_log_link(self):
        self.find_element(*self._manual_review_log_link_locator).click()
        return ManualReviewLog(self.driver, self.base_url).wait_for_page_to_load()

    def click_moderated_review_log_link(self):
        self.find_element(*self._moderated_review_log_locator).click()
        return ModeratedReviewLog(self.driver, self.base_url).wait_for_page_to_load()

    def click_ratings_awaiting_moderation(self):
        self.find_element(*self._user_ratings_awaiting_moderation_locator).click()
        return RatingsAwaitingModeration(self.driver, self.base_url).wait_for_page_to_load()

    def click_addon_review_guide_link(self):
        self.find_element(*self._addons_review_guide_locator).click()
        self.wait.until(EC.number_of_windows_to_be(2))
        current_tab = self.driver.window_handles[0]
        new_tab = self.driver.window_handles[1]
        self.driver.switch_to.window(new_tab)
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//span[@id='Add-on_Review_Guide']"))
        )
        self.driver.close()
        self.driver.switch_to.window(current_tab)

    def click_themes_review_guide_click(self):
        self.find_element(*self._themes_review_guide_locator).click()
        self.wait.until(EC.number_of_windows_to_be(2))
        current_tab = self.driver.window_handles[0]
        new_tab = self.driver.window_handles[1]
        self.driver.switch_to.window(new_tab)
        self.wait.until(
            EC.visibility_of_element_located((By.ID, "Background_Themes_Content_Guidelines"))
        )
        self.driver.close()
        self.driver.switch_to.window(current_tab)

    def click_moderation_guide_click(self):
        self.find_element(*self._user_ratings_moderation_guide_locator).click()
        self.wait.until(EC.number_of_windows_to_be(2))
        current_tab = self.driver.window_handles[0]
        new_tab = self.driver.window_handles[1]
        self.driver.switch_to.window(new_tab)
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//span[contains(text(),'Add-ons/Reviewers/Guide/Moderation')]"))
        )
        self.driver.close()
        self.driver.switch_to.window(current_tab)

    # Methods -------------------------------------------------------------
    def assert_reviewer_tools_section(self):
        assert (
            self.manual_review_link.is_displayed(),
            self.manual_review_log_link.is_displayed(),
            self.content_review_link.is_displayed(),
            self.addons_review_guide.is_displayed(),
            self.flagged_for_human_review.is_displayed(),
            self.themes_themes_awaiting_review.is_displayed(),
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