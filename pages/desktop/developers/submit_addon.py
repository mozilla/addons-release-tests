import os
from pathlib import Path
from pypom import Page

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.developers.manage_versions import ManageVersions


class SubmitAddon(Page):
    """A class holding all the components used for addon submissions in DevHub"""

    _my_addons_page_logo_locator = (By.CSS_SELECTOR, '.site-titles')
    _submission_form_header_locator = (By.CSS_SELECTOR, '.is_addon')
    _addon_distribution_header_locator = (
        By.CSS_SELECTOR,
        '.addon-submission-process h3',
    )
    _listed_option_locator = (By.CSS_SELECTOR, 'input[value="listed"]')
    _unlisted_option_locator = (By.CSS_SELECTOR, 'input[value="unlisted"]')
    _change_distribution_link_locator = (By.CSS_SELECTOR, '.addon-submit-distribute a')
    _continue_button_locator = (By.CSS_SELECTOR, '.addon-submission-field button')
    _upload_file_button_locator = (By.CSS_SELECTOR, '.invisible-upload input')
    _firefox_compat_checkbox_locator = (By.CSS_SELECTOR, '.app.firefox input')
    _android_compat_checkbox_locator = (By.CSS_SELECTOR, '.app.android input')
    _create_theme_button_locator = (By.ID, 'wizardlink')
    _submit_file_button_locator = (By.ID, 'submit-upload-file-finish')
    _addon_validation_success_locator = (By.CLASS_NAME, 'bar-success')
    _validation_fail_message_locator = (By.CLASS_NAME, 'status-fail')
    _validation_success_message_locator = (By.ID, 'upload-status-results')

    @property
    def my_addons_page_logo(self):
        return self.find_element(*self._my_addons_page_logo_locator)

    @property
    def submission_form_header(self):
        return self.find_element(*self._submission_form_header_locator)

    @property
    def distribution_header(self):
        return self.find_element(*self._addon_distribution_header_locator)

    def select_listed_option(self):
        self.find_element(*self._listed_option_locator).click()

    def select_unlisted_option(self):
        self.find_element(*self._unlisted_option_locator).click()

    def change_version_distribution(self):
        """Changes the distribution (listed/unlisted) when submitting a new version"""
        self.find_element(*self._change_distribution_link_locator).click()
        self.wait.until(EC.visibility_of_element_located(self._listed_option_locator))

    def click_continue(self):
        self.find_element(*self._continue_button_locator).click()

    def upload_addon(self, addon):
        """Selects an addon from the 'sample-addons' folder and uploads it"""
        button = self.find_element(*self._upload_file_button_locator)
        path = Path(os.getcwd())
        archive = path / 'sample-addons' / addon
        button.send_keys(str(archive))

    @property
    def firefox_compat_checkbox(self):
        return self.find_element(*self._firefox_compat_checkbox_locator)

    @property
    def android_compat_checkbox(self):
        return self.find_element(*self._android_compat_checkbox_locator)

    def is_validation_successful(self):
        """Wait for addon validation to complete; if not successful, the test will fail"""
        self.wait.until(
            EC.visibility_of_element_located(self._addon_validation_success_locator)
        )

    @property
    def failed_validation_message(self):
        return self.find_element(*self._validation_fail_message_locator)

    @property
    def success_validation_message(self):
        return self.find_element(*self._validation_success_message_locator)

    def click_continue_upload_button(self):
        self.find_element(*self._submit_file_button_locator).click()
        return UploadSource(self.selenium, self.base_url)

    def submit_button_disabled(self):
        self.find_element(*self._submit_file_button_locator).get_attribute('disabled')


class UploadSource(Page):
    _submit_source_code_page_header_locator = (
        By.CSS_SELECTOR,
        '.addon-submission-process h3',
    )
    _yes_submit_source_radio_button_locator = (By.ID, 'id_has_source_0')
    _no_submit_source_radio_button_locator = (By.ID, 'id_has_source_1')
    _continue_button_locator = (
        By.CSS_SELECTOR,
        '.submission-buttons button:nth-child(1)',
    )

    @property
    def submit_source_page_header(self):
        return self.find_element(*self._submit_source_code_page_header_locator).text

    def select_yes_to_submit_source(self):
        self.find_element(*self._yes_submit_source_radio_button_locator).click()

    def select_no_to_omit_source(self):
        self.find_element(*self._no_submit_source_radio_button_locator).click()

    def continue_unlisted_submission(self):
        self.find_element(*self._continue_button_locator).click()
        return SubmissionConfirmationPage(
            self.selenium, self.base_url
        ).wait_for_page_to_load()


class SubmissionConfirmationPage(Page):
    _confirmation_page_header_locator = (
        By.CSS_SELECTOR,
        '.addon-submission-process h3',
    )
    _confirmation_messages_locator = (By.CSS_SELECTOR, '.addon-submission-process p')
    _manage_listing_button_locator = (By.LINK_TEXT, 'Go to My Submissions')
    _edit_version_button_locator = (
        By.CSS_SELECTOR,
        '.addon-submission-process p:nth-child(6) > a',
    )
    _edit_listing_button_locator = (By.LINK_TEXT, 'Manage Listing')
    _theme_preview_locator = (By.CSS_SELECTOR, '.addon-submission-process img')

    def wait_for_page_to_load(self):
        self.wait.until(
            EC.visibility_of_element_located(self._confirmation_page_header_locator)
        )
        return self

    @property
    def submission_confirmation_messages(self):
        return self.find_elements(*self._confirmation_messages_locator)

    def click_manage_listing_button(self):
        self.find_element(*self._manage_listing_button_locator).click()
        from pages.desktop.developers.addons_manage import ManageAddons

        return ManageAddons(self.selenium, self.base_url).wait_for_page_to_load()

    def click_edit_version_button(self):
        self.find_element(*self._edit_version_button_locator).click()
        return ManageVersions(self.selenium, self.base_url)

    def click_edit_listing_button(self):
        self.find_element(*self._edit_listing_button_locator).click()
        from pages.desktop.developers.edit_addon import EditAddon

        return EditAddon(self.selenium, self.base_url).wait_for_page_to_load()

    @property
    def generated_theme_preview(self):
        return self.find_element(*self._theme_preview_locator)
