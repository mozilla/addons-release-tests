from selenium.webdriver.common.by import By
from pages.desktop.base import Base


class ReviewAddonPage(Base):
    URL_TEMPLATE = 'reviewers/review/'

    _addon_section_locator = (By.ID, 'addon')

    # Announcement section
    _announcement_section_locator = (By.CSS_SELECTOR, '.daily-message')
    _announcement_text_locator = (By.CSS_SELECTOR, '.featured-inner > h2')
    _announcement_close_locator = (By.CSS_SELECTOR, '.close')

    # Addon info section
    _addon_info_section_locator = (By.CSS_SELECTOR, '.addon-info')
    _addon_name_text_locator = (By.ID, 'addon-name')
    _addon_info_id_locator = (By.CSS_SELECTOR, '.addon-guid')
    _addon_internal_id_locator = (By.CSS_SELECTOR, '.addon-amo-id')

    # Abuse report Section
    _abuse_report_section_locator = (By.CSS_SELECTOR, '.abuse_reports')

    # Whiteboard section
    _whiteboard_section_locator = (By.ID, 'whiteboard_form')
    _whiteboard_public_locator = (By.CSS_SELECTOR, '.whiteboard-inner')
    _whiteboard_private_locator = (By.CSS_SELECTOR, '.whiteboard.private')
    _whiteboard_actions_locator = (By.CSS_SELECTOR, '.whiteboard-actions')

    # Sidenav section
    _actions_list_locator = (By.ID, 'actions-addon')
    _view_product_page_locator = (By.XPATH, "//ul[@id='actions-addon']//a[contains(text(), 'View Product Page')]")
    _edit_locator = (By.XPATH, "//ul[@id='actions-addon']//a[contains(text(), 'Edit')]")
    _admin_page_locator = (By.XPATH, "//ul[@id='actions-addon']//a[contains(text(), 'Admin Page')]")
    _statistics_locator = (By.XPATH, "//ul[@id='actions-addon']//a[contains(text(), 'Statistics')]")

    # Add-on History section
    _addon_history_text_locator = (By.ID, 'history')
    _addon_versions_history_locator = (By.ID, 'versions-history')

    # Reviewer Actions section
    _review_actions_sections_locator = (By.ID, 'review-actions')
    _reject_multiple_versions_locator = (By.XPATH, "//label[contains(text(), 'Reject Multiple Versions')]")
    _clear_pending_rejection_locator = (By.XPATH, "//label[contains(text(), 'Clear pending rejection')]")
    _clear_needs_human_review_locator = (By.XPATH, "//label[contains(text(), 'Clear Needs Human Review')]")
    _set_needs_human_review_locator = (By.XPATH, "//label[contains(text(), 'Set Needs Human Review')]")
    _reviewer_reply_locator = (By.XPATH, "//label[contains(text(), 'Reviewer reply')]")
    _force_disable_locator = (By.XPATH, "//label[contains(text(), 'Force disable')")
    _comment_locator = (By.XPATH, "//label[contains(text(), 'Comment')]")

    # More actions section
    _more_actions_section_locator = (By.ID, 'extra-review-actions')
    _notify_about_listed_versions_locator = (By.ID, 'notify_new_listed_versions')
    _notify_about_unlisted_versions_locator =(By.ID, 'notify_new_unlisted_versions')

    @staticmethod
    def open_content_review_page_for_addon(selenium, base_url, addon_string):
        return selenium.get(f"{base_url}/reviewer/review-content/{addon_string}")

    # Announcement section interaction methods

    @property
    def announcement_section(self):
        return self.find_element(*self._announcement_section_locator)

    @property
    def announcement_text(self):
        return self.find_element(*self._announcement_text_locator)

    @property
    def announcement_close_button(self):
        return self.find_element(*self._announcement_close_locator)

    # Addon info section interaction methods

    @property
    def addon_info_section(self):
        return self.find_element(*self._addon_info_section_locator)

    @property
    def addon_name_text(self):
        return self.find_element(*self._addon_name_text_locator)

    @property
    def addon_info_id(self):
        return self.find_element(*self._addon_info_id_locator)

    @property
    def addon_internal_id(self):
        return self.find_element(*self._addon_internal_id_locator)

    # Abuse report Section interaction methods

    @property
    def abuse_report_section(self):
        return self.find_element(*self._abuse_report_section_locator)

    # Whiteboard section interaction methods

    @property
    def whiteboard_section(self):
        return self.find_element(*self._whiteboard_section_locator)

    @property
    def whiteboard_public(self):
        return self.find_element(*self._whiteboard_public_locator)

    @property
    def whiteboard_private(self):
        return self.find_element(*self._whiteboard_private_locator)

    @property
    def whiteboard_actions(self):
        return self.find_element(*self._whiteboard_actions_locator)


    # Sidenav section interaction methods

    @property
    def actions_list(self):
        return self.find_element(*self._actions_list_locator)

    @property
    def view_products_page(self):
        return self.find_element(*self._view_product_page_locator)

    @property
    def edit_page(self):
        return self.find_element(*self._edit_locator)

    @property
    def admin_page(self):
        return self.find_element(*self._admin_page_locator)

    @property
    def statistics_page(self):
        return self.find_element(*self._statistics_locator)

    # Add-on History section interaction methods

    @property
    def addon_history_text(self):
        return self.find_element(*self._addon_history_text_locator)

    @property
    def addon_versions_history(self):
        return self.find_element(*self._addon_versions_history_locator)

    # Reviewer Actions section interaction methods

    @property
    def review_actions_section(self):
        return self.find_element(*self._review_actions_sections_locator)

    @property
    def reject_multiple_versions(self):
        return self.find_element(*self._reject_multiple_versions_locator)

    @property
    def clear_pending_rejection(self):
        return self.find_element(*self._clear_pending_rejection_locator)

    @property
    def clear_needs_human_review(self):
        return self.find_element(*self._clear_needs_human_review_locator)

    @property
    def set_needs_human_review(self):
        return self.find_element(*self._set_needs_human_review_locator)

    @property
    def reviewer_reply(self):
        return self.find_element(*self._reviewer_reply_locator)

    @property
    def force_disable(self):
        return self.find_element(*self._force_disable_locator)

    @property
    def comment(self):
        return self.find_element(*self._comment_locator)

    # More actions section interaction methods
    @property
    def more_actions_section(self):
        return self.find_element(*self._more_actions_section_locator)

    @property
    def more_actions_new_listed_versions(self):
        return self.find_element(*self._notify_about_listed_versions_locator)

    @property
    def more_actions_new_unlisted_versions(self):
        return self.find_element(*self._notify_about_unlisted_versions_locator)


    # Assert Methods
    def assert_announcement_section_displayed(self):
        assert self.announcement_section.is_displayed(), "Announcement section is not displayed"
        assert self.announcement_text.is_displayed(), "Announcement text is not displayed"
        assert self.announcement_close_button.is_displayed(), "Announcement close button is not displayed"

    def assert_addon_info_section_displayed(self):
        assert self.addon_info_section.is_displayed(), "Addon info section is not displayed"
        assert self.addon_name_text.is_displayed(), "Addon name text is not displayed"
        assert self.addon_info_id.is_displayed(), "Addon info ID is not displayed"
        assert self.addon_internal_id.is_displayed(), "Addon internal ID is not displayed"

    def assert_abuse_report_section_displayed(self):
        assert self.abuse_report_section.is_displayed(), "Abuse Report Section is not displayed"

    def assert_whiteboard_section_displayed(self):
        assert self.whiteboard_section.is_displayed(), "Whiteboard section is not displayed"
        assert self.whiteboard_public.is_displayed(), "Whiteboard public is not displayed"
        assert self.whiteboard_private.is_displayed(), "Whiteboard private is not displayed"
        assert self.whiteboard_actions.is_displayed(), "Whiteboard actions are not displayed"

    def assert_sidenav_section_displayed(self):
        assert self.actions_list.is_displayed(), "Actions list is not displayed"
        assert self.view_products_page.is_displayed(), "View products page link is not displayed"
        assert self.edit_page.is_displayed(), "Edit page link is not displayed"
        assert self.admin_page.is_displayed(), "Admin page link is not displayed"
        assert self.statistics_page.is_displayed(), "Statistics page link is not displayed"

    def assert_addon_history_section_displayed(self):
        assert self.addon_history_text.is_displayed(), "Addon history text is not displayed"
        assert self.addon_versions_history.is_displayed(), "Addon versions history is not displayed"

    def assert_reviewer_actions_section_displayed(self):
        assert self.reviewer_reply.is_displayed(), "Reviewer reply button is not displayed"
        assert self.comment.is_displayed(), "Comment button is not displayed"

    def assert_more_actions_section_displayed(self):
        assert self.more_actions_section.is_displayed(), "More actions section is not displayed"
        assert self.more_actions_new_listed_versions.is_displayed(), "Notify about new listed versions option is not displayed"
        assert self.more_actions_new_unlisted_versions.is_displayed(), "Notify about new unlisted versions option is not displayed"

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._addon_section_locator).is_displayed(),
            message="Addon Review Page was not loaded",
        )
        return self
