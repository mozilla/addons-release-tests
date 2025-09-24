import os
import time
from pathlib import Path
from pypom import Page

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

from pages.desktop.developers.manage_versions import ManageVersions


class SubmitAddon(Page):
    """A class holding all the components used for addon submissions in DevHub"""

    _my_addons_page_logo_locator = (By.CSS_SELECTOR, ".site-titles")
    _submission_form_header_locator = (By.CSS_SELECTOR, ".is_addon")
    _addon_distribution_header_locator = (
        By.CSS_SELECTOR,
        ".addon-submission-process h3",
    )
    _developer_notification_box_locator = (By.CSS_SELECTOR, ".notification-box")
    _distribution_page_explainer_locator = (
        By.CSS_SELECTOR,
        ".addon-submission-process p:nth-of-type(1)",
    )
    _distribution_agreement_checkbox_locator = (By.ID, "id_distribution_agreement")
    _distribution_agreement_link_locator = (
        By.CSS_SELECTOR,
        ".addon-submission-process li:nth-of-type(1) a",
    )
    _review_policies_checkbox_locator = (By.ID, "id_review_policy")
    _review_policies_link_locator = (
        By.CSS_SELECTOR,
        ".addon-submission-process li:nth-of-type(2) a",
    )
    _user_consent_text_locator = (
        By.CSS_SELECTOR,
        ".addon-submission-process p:nth-of-type(2)",
    )
    _recaptcha_locator = (By.ID, "id_recaptcha")
    _recaptcha_checkbox_locator = (By.ID, "recaptcha-anchor")
    _recaptcha_checkbox_is_selected_locator = (
        By.CSS_SELECTOR,
        'span[aria-checked="true"]',
    )
    _accept_agreement_button = (By.ID, "accept-agreement")
    _cancel_agreement_button = (By.CSS_SELECTOR, ".submit-buttons a")
    _dev_accounts_info_link_locator = (By.CSS_SELECTOR, ".addon-submission-process > p:nth-child(3) > a")

    _listed_option_locator = (By.CSS_SELECTOR, 'input[value="listed"]')
    _listed_option_helptext_locator = (
        By.CSS_SELECTOR,
        "label[for='id_channel_0'] span[class='helptext']",
    )
    _unlisted_option_locator = (By.CSS_SELECTOR, 'input[value="unlisted"]')
    _unlisted_option_helptext_locator = (
        By.CSS_SELECTOR,
        "label[for='id_channel_1'] span[class='helptext']",
    )
    _distribution_and_signing_helptext_locator = (
        By.CSS_SELECTOR,
        ".addon-submit-distribute p:nth-of-type(3)",
    )
    _addon_policies_helptext_locator = (
        By.CSS_SELECTOR,
        ".addon-submit-distribute p:nth-of-type(4)",
    )
    _change_distribution_link_locator = (By.CSS_SELECTOR, ".addon-submit-distribute a")
    _continue_button_locator = (By.CSS_SELECTOR, ".addon-submission-field button")
    _file_upload_process_helptext_locator = (By.CSS_SELECTOR, ".new-addon-file p")
    _upload_file_button_locator = (By.CSS_SELECTOR, "#upload-addon")
    _accepted_file_types_locator = (By.CLASS_NAME, "upload-details")
    _compatibility_helptext_locator = (By.CSS_SELECTOR, ".compatible-apps label")
    _compatibility_error_message_locator = (By.CSS_SELECTOR, ".errorlist li")
    _firefox_compat_checkbox_locator = (By.CSS_SELECTOR, ".app.firefox input")
    _android_compat_checkbox_locator = (By.CSS_SELECTOR, ".app.android input")
    _android_compat_pop_up = (By.ID, "modal-confirm-android-compatibility")
    _android_compat_yes_button = (By.CSS_SELECTOR, "#modal-confirm-android-compatibility > form > div > button")
    _create_theme_subheader_locator = (
        By.CSS_SELECTOR,
        ".addon-create-theme-section h3",
    )
    _create_theme_button_locator = (By.ID, "wizardlink")
    _submit_file_button_locator = (By.ID, "submit-upload-file-finish")
    _addon_validation_success_locator = (By.CSS_SELECTOR, "#upload-status-bar.bar-success")
    _validation_fail_bar_locator = (By.CLASS_NAME, "bar-fail")
    _validation_support_link_locator = (By.CSS_SELECTOR, "#upload-status-results a")
    _validation_failed_message_locator = (
        By.CSS_SELECTOR,
        "#upload-status-results strong",
    )
    _validation_warning_message_locator = (By.CSS_SELECTOR, ".submission-warning p")
    _validation_summary_link_locator = (By.CSS_SELECTOR, ".submission-warning a")
    _validation_fail_reason_locator = (By.CSS_SELECTOR, "#upload_errors li")
    _validation_status_text_locator = (By.ID, "upload-status-text")
    _validation_success_message_locator = (By.ID, "upload-status-results")
    _failed_validation_message_locator = (By.CSS_SELECTOR, "#upload-status-results > strong:nth-child(2)")


    @property
    def my_addons_page_logo(self):
        self.wait.until(
            EC.visibility_of_element_located(self._my_addons_page_logo_locator)
        )
        return self.find_element(*self._my_addons_page_logo_locator)

    @property
    def submission_form_header(self):
        self.wait.until(
            EC.visibility_of_element_located(self._submission_form_header_locator)
        )
        return self.find_element(*self._submission_form_header_locator)

    @property
    def submission_form_subheader(self):
        self.wait.until(
            EC.visibility_of_element_located(self._addon_distribution_header_locator)
        )
        return self.find_element(*self._addon_distribution_header_locator)

    @property
    def developer_notification_box(self):
        self.wait.until(
            EC.visibility_of_element_located(self._developer_notification_box_locator)
        )
        return self.find_element(*self._developer_notification_box_locator)

    @property
    def distribution_page_explainer(self):
        self.wait.until(
            EC.visibility_of_element_located(self._distribution_page_explainer_locator)
        )
        return self.find_element(*self._distribution_page_explainer_locator).text

    @property
    def distribution_agreement_checkbox(self):
        self.wait.until(
            EC.visibility_of_element_located(
                self._distribution_agreement_checkbox_locator
            )
        )
        return self.find_element(*self._distribution_agreement_checkbox_locator)

    @property
    def distribution_agreement_article_link(self):
        self.wait.until(
            EC.visibility_of_element_located(self._distribution_agreement_link_locator)
        )
        return self.find_element(*self._distribution_agreement_link_locator)

    @property
    def review_policies_checkbox(self):
        self.wait.until(
            EC.visibility_of_element_located(self._review_policies_checkbox_locator)
        )
        return self.find_element(*self._review_policies_checkbox_locator)

    @property
    def review_policies_article_link(self):
        self.wait.until(
            EC.visibility_of_element_located(self._review_policies_link_locator)
        )
        return self.find_element(*self._review_policies_link_locator)

    def click_extension_workshop_article_link(self, link, text):
        """Clicks on the Distribution agreement and the Policies links
        which open an Extension Workshop article page in a new tab"""
        link.click()
        self.wait.until(
            EC.number_of_windows_to_be(2),
            message=f"Number of windows was {len(self.driver.window_handles)}, expected 2",
        )
        new_tab = self.driver.window_handles[1]
        self.driver.switch_to.window(new_tab)
        self.wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".page-hero h1"), text)
        )
        self.driver.close()
        # return to the main tab
        self.driver.switch_to.window(self.driver.window_handles[0])

    @property
    def user_consent_text(self):
        self.wait.until(
            EC.visibility_of_element_located(self._user_consent_text_locator)
        )
        return self.find_element(*self._user_consent_text_locator).text

    @property
    def recaptcha(self):
        self.wait.until(EC.visibility_of_element_located(self._recaptcha_locator))
        return self.find_element(*self._recaptcha_locator)

    def click_recaptcha_checkbox(self):
        """reCAPTCHA is stored in an iframe; switch to the iframe and click on the checkbox"""
        el = self.find_element(By.CSS_SELECTOR, 'iframe[title="reCAPTCHA"]')
        self.driver.switch_to.frame(el)
        self.find_element(*self._recaptcha_checkbox_locator).click()

    @property
    def accept_agreement(self):
        self.wait.until(EC.visibility_of_element_located(self._accept_agreement_button))
        return self.find_element(*self._accept_agreement_button)

    @property
    def cancel_agreement(self):
        self.wait.until(EC.visibility_of_element_located(self._cancel_agreement_button))
        return self.find_element(*self._cancel_agreement_button)

    def click_dev_accounts_info_link(self):
        """click on the Developer account info link and check that the
        correct Extension Workshop article is opened"""
        self.find_element(*self._dev_accounts_info_link_locator).click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".page-hero h1"), "Developer accounts"
            )
        )

    @property
    def listed_option_helptext(self):
        self.wait.until(
            EC.visibility_of_element_located(self._listed_option_helptext_locator)
        )
        return self.find_element(*self._listed_option_helptext_locator).text

    @property
    def unlisted_option_helptext(self):
        self.wait.until(
            EC.visibility_of_element_located(self._unlisted_option_helptext_locator)
        )
        return self.find_element(*self._unlisted_option_helptext_locator)

    @property
    def update_url_link(self):
        return self.unlisted_option_helptext.find_element(By.CSS_SELECTOR, "a")

    @property
    def listed_option_radiobutton(self):
        self.wait.until(EC.visibility_of_element_located(self._listed_option_locator))
        return self.find_element(*self._listed_option_locator)

    def select_listed_option(self):
        self.wait.until(EC.element_to_be_clickable(self._listed_option_locator))
        self.find_element(*self._listed_option_locator).click()

    def select_unlisted_option(self):
        self.wait.until(EC.element_to_be_clickable(self._unlisted_option_locator))
        self.find_element(*self._unlisted_option_locator).click()

    @property
    def distribution_and_signing_helptext(self):
        self.wait.until(
            EC.visibility_of_element_located(
                self._distribution_and_signing_helptext_locator
            )
        )
        return self.find_element(*self._distribution_and_signing_helptext_locator)

    @property
    def distribution_and_signing_link(self):
        return self.distribution_and_signing_helptext.find_element(By.CSS_SELECTOR, "a")

    @property
    def addon_policies_helptext(self):
        self.wait.until(
            EC.visibility_of_element_located(self._addon_policies_helptext_locator)
        )
        return self.find_element(*self._addon_policies_helptext_locator)

    @property
    def addon_policies_link(self):
        return self.addon_policies_helptext.find_element(By.CSS_SELECTOR, "a")

    def change_version_distribution(self):
        """Changes the distribution (listed/unlisted) when submitting a new version"""
        self.find_element(*self._change_distribution_link_locator).click()
        self.wait.until(EC.visibility_of_element_located(self._listed_option_locator))

    def click_continue(self):
        self.find_element(*self._continue_button_locator).click()

    @property
    def file_upload_helptext(self):
        self.wait.until(
            EC.visibility_of_element_located(self._file_upload_process_helptext_locator)
        )
        return self.find_elements(*self._file_upload_process_helptext_locator)

    def upload_addon(self, addon):
        """Selects an addon from the 'sample-addons' folder and uploads it"""
        button = self.find_element(*self._upload_file_button_locator)
        archive = Path(f"{os.getcwd()}/sample-addons/{addon}")
        button.send_keys(str(archive))

    @property
    def accepted_file_types(self):
        self.wait.until(
            EC.visibility_of_element_located(self._accepted_file_types_locator)
        )
        return self.find_element(*self._accepted_file_types_locator).text

    @property
    def compatibility_helptext(self):
        self.wait.until(
            EC.visibility_of_element_located(self._compatibility_helptext_locator)
        )
        return self.find_elements(*self._compatibility_helptext_locator)[0].text

    @property
    def compatibility_error_message(self):
        self.wait.until(
            EC.visibility_of_element_located(self._compatibility_error_message_locator)
        )
        return self.find_element(*self._compatibility_error_message_locator).text

    @property
    def firefox_compat_checkbox(self):
        return self.find_element(*self._firefox_compat_checkbox_locator)

    @property
    def android_compat_checkbox(self):
        self.wait.until(
            EC.visibility_of_element_located(self._android_compat_checkbox_locator)
        )
        return self.find_element(*self._android_compat_checkbox_locator)

    @property
    def android_compat_pop_up(self):
        self.wait.until(
            EC.visibility_of_element_located(self._android_compat_pop_up)
        )
        return self.find_element(*self._android_compat_pop_up)

    @property
    def android_compat_yes_button(self):
        self.wait.until(
            EC.visibility_of_element_located(self._android_compat_yes_button)
        )
        return self.find_element(*self._android_compat_yes_button)

    @property
    def create_theme_subheader(self):
        self.wait.until(
            EC.visibility_of_element_located(self._create_theme_subheader_locator)
        )
        return self.find_element(*self._create_theme_subheader_locator).text

    def click_create_theme_button(self):
        self.find_element(*self._create_theme_button_locator).click()
        return ThemeWizard(self.driver, self.base_url).wait_for_page_to_load()

    def is_validation_successful(self, retries=3, delay=2, timeout=10):
        """
        Wait for addon validation to complete; if not successful, the test will fail
        Retry validation check up to `retries` times with `delay` seconds between tries.
        Each try has its own `timeout`.
        """
        for attempt in range(retries):
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located(self._addon_validation_success_locator)
                )
                return True  # Found -> success
            except TimeoutException:
                if attempt < retries - 1:
                    time.sleep(delay)  # Wait before retry
                else:
                    raise  # Final failure

    @property
    def failed_validation_bar(self):
        self.wait.until(
            EC.visibility_of_element_located(self._validation_fail_bar_locator)
        )
        return self.find_element(*self._validation_fail_bar_locator)

    @property
    def validation_status_title(self):
        self.wait.until(
            EC.visibility_of_element_located(self._validation_status_text_locator)
        )
        return self.find_element(*self._validation_status_text_locator).text

    def click_validation_support_link(self):
        self.find_element(*self._validation_support_link_locator).click()
        self.wait.until(
            EC.number_of_windows_to_be(2),
            message=f"Number of windows was {len(self.driver.window_handles)}, expected 2",
        )
        new_tab = self.driver.window_handles[1]
        self.driver.switch_to.window(new_tab)
        self.wait.until(EC.url_contains("/mozilla/addons-linter/"))
        self.driver.close()
        # return to the main tab
        self.driver.switch_to.window(self.driver.window_handles[0])

    def is_validation_failed(self):
        self.wait.until(
            EC.visibility_of_element_located(self._validation_fail_bar_locator)
        )

    @property
    def validation_failed_message(self):
        self.wait.until(
            EC.visibility_of_element_located(self._validation_failed_message_locator)
        )
        return self.find_element(*self._validation_failed_message_locator).text

    @property
    def validation_failed_reason(self):
        self.wait.until(
            EC.visibility_of_element_located(self._validation_fail_reason_locator)
        )
        return self.find_elements(*self._validation_fail_reason_locator)

    @property
    def validation_warning_message(self):
        self.wait.until(
            EC.visibility_of_element_located(self._validation_warning_message_locator)
        )
        return self.find_element(*self._validation_warning_message_locator).text

    def click_validation_summary(self):
        self.find_element(*self._validation_summary_link_locator).click()
        self.wait.until(
            EC.number_of_windows_to_be(2),
            message=f"Number of windows was {len(self.driver.window_handles)}, expected 2",
        )
        new_tab = self.driver.window_handles[1]
        self.driver.switch_to.window(new_tab)
        self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "results")))
        return ValidationResults(self.driver, self.base_url)

    @property
    def success_validation_message(self):
        self.wait.until(
            EC.visibility_of_element_located(self._validation_success_message_locator)
        )
        return self.find_element(*self._validation_success_message_locator)

    def click_continue_upload_button(self):
        self.find_element(*self._submit_file_button_locator).click()
        return UploadSource(self.driver, self.base_url)

    def submit_button_disabled(self):
        self.find_element(*self._submit_file_button_locator).get_attribute("disabled")

    @property
    def failed_validation_message(self):
        return self.find_element(*self._failed_validation_message_locator)


class ValidationResults(Page):
    _validation_results_header_locator = (
        By.CSS_SELECTOR,
        "div[class='section'] header h2",
    )
    _validation_summary_shelf_locator = (By.CLASS_NAME, "tiers")
    _validation_general_results_locator = (By.ID, "suite-results-tier-1")
    _validation_security_results_locator = (By.ID, "suite-results-tier-2")
    _validation_extension_results_locator = (By.ID, "suite-results-tier-3")
    _validation_localization_results_locator = (By.ID, "suite-results-tier-4")
    _validation_compatibility_results_locator = (By.ID, "suite-results-tier-5")

    @property
    def validation_results_header(self):
        self.wait.until(
            EC.visibility_of_element_located(self._validation_results_header_locator)
        )
        return self.find_element(*self._validation_results_header_locator).text

    @property
    def validation_summary_shelf(self):
        self.wait.until(
            EC.visibility_of_element_located(self._validation_results_header_locator)
        )
        return self.find_element(*self._validation_summary_shelf_locator)

    @property
    def validation_general_results(self):
        self.wait.until(
            EC.visibility_of_element_located(self._validation_general_results_locator)
        )
        return self.find_element(*self._validation_general_results_locator)

    @property
    def validation_security_results(self):
        self.wait.until(
            EC.visibility_of_element_located(self._validation_security_results_locator)
        )
        return self.find_element(*self._validation_security_results_locator)

    @property
    def validation_extension_results(self):
        self.wait.until(
            EC.visibility_of_element_located(self._validation_extension_results_locator)
        )
        return self.find_element(*self._validation_extension_results_locator)

    @property
    def validation_localization_results(self):
        self.wait.until(
            EC.visibility_of_element_located(
                self._validation_localization_results_locator
            )
        )
        return self.find_element(*self._validation_localization_results_locator)

    @property
    def validation_compatibility_results(self):
        self.wait.until(
            EC.visibility_of_element_located(
                self._validation_compatibility_results_locator
            )
        )
        return self.find_element(*self._validation_compatibility_results_locator)


class UploadSource(Page):
    _submit_source_code_page_header_locator = (
        By.CSS_SELECTOR,
        ".addon-submission-process h3",
    )
    _yes_submit_source_radio_button_locator = (By.ID, "id_has_source_0")
    _no_submit_source_radio_button_locator = (By.ID, "id_has_source_1")
    _choose_source_file_button_locator = (By.ID, "id_source")
    _continue_button_locator = (
        By.CSS_SELECTOR,
        ".submission-buttons button:nth-child(1)",
    )
    _upload_source_error_message_locator = (By.CSS_SELECTOR, ".errorlist li")
    _cancel_and_disable_version_locator = (
        By.CSS_SELECTOR,
        ".confirm-submission-cancel",
    )
    _cancel_and_disable_explainer_text_locator = (
        By.CSS_SELECTOR,
        "#modal-confirm-submission-cancel p",
    )
    _cancel_version_confirm_button_locator = (
        By.CSS_SELECTOR,
        ".modal-confirm-submission-cancel .delete-button",
    )
    _yes_cancel_and_disable_version = (By.CSS_SELECTOR, "button.delete-button:nth-child(1)")
    _do_not_cancel_version_link_locator = (By.CSS_SELECTOR, "#modal-confirm-submission-cancel > form > div > a")
    _release_notes_field_locator = (By.ID, "trans-release_notes")
    _notes_to_reviewer_locator = (By.ID, "id_approval_notes")
    _version_submitted_text_locator = (By.CLASS_NAME, ".addon-submission-process h3")

    @property
    def submit_source_page_header(self):
        self.wait.until(
            EC.visibility_of_element_located(
                self._submit_source_code_page_header_locator
            )
        )
        return self.find_element(*self._submit_source_code_page_header_locator).text

    def select_yes_to_submit_source(self):
        self.wait.until(
            EC.visibility_of_element_located(
                self._yes_submit_source_radio_button_locator
            )
        )
        self.find_element(*self._yes_submit_source_radio_button_locator).click()

    def select_no_to_omit_source(self):
        self.find_element(*self._no_submit_source_radio_button_locator).click()

    def choose_source(self, file):
        button = self.find_element(*self._choose_source_file_button_locator)
        archive = Path(f"{os.getcwd()}/sample-addons/{file}")
        button.send_keys(str(archive))

    def continue_unlisted_submission(self):
        self.find_element(*self._continue_button_locator).click()
        return SubmissionConfirmationPage(
            self.driver, self.base_url
        ).wait_for_page_to_load()

    def continue_listed_submission(self):
        self.find_element(*self._continue_button_locator).click()
        return ListedAddonSubmissionForm(
            self.driver, self.base_url
        ).wait_for_page_to_load()

    @property
    def source_upload_fail_message(self):
        self.wait.until(
            EC.visibility_of_element_located(self._upload_source_error_message_locator)
        )
        return self.find_element(*self._upload_source_error_message_locator).text

    def click_cancel_and_disable_version(self):
        self.find_element(*self._cancel_and_disable_version_locator).click()

    @property
    def cancel_and_disable_explainer_text(self):
        self.wait.until(
            EC.visibility_of_element_located(
                self._cancel_and_disable_explainer_text_locator
            )
        )
        return self.find_element(*self._cancel_and_disable_explainer_text_locator).text

    def click_do_not_cancel_version(self):
        return self.find_element(*self._do_not_cancel_version_link_locator).click()

    def confirm_cancel_and_disable_version(self):
        self.find_element(*self._yes_cancel_and_disable_version).click()
        return ManageVersions(self.driver, self.base_url).wait_for_page_to_load()

    def release_notes_field(self):
        self.wait.until(
            EC.visibility_of_element_located(
                self._release_notes_field_locator
            )
        )
        return self.find_element(*self._release_notes_field_locator)

    def notes_to_reviewers_field(self):
        self.wait.until(
            EC.visibility_of_element_located(
                self._notes_to_reviewer_locator
            )
        )
        return self.find_element(*self._notes_to_reviewer_locator)

    def version_submitted_text(self):
        self.wait.until(
            EC.visibility_of_element_located(
                self._version_submitted_text_locator
            )
        )
        return self.find_element(*self._version_submitted_text_locator).text

class ListedAddonSubmissionForm(Page):
    _addon_name_field_locator = (By.CSS_SELECTOR, "#trans-name input:nth-child(1)")
    _edit_addon_slug_link_locator = (By.ID, "edit_slug")
    _edit_addon_slug_field_locator = (By.ID, "id_slug")
    _addon_summary_field_locator = (By.ID, "id_summary_0")
    _addon_detail_fields_info_text_locator = (By.CSS_SELECTOR, ".edit-addon-details")
    _summary_character_count_locator = (
        By.CSS_SELECTOR,
        ".char-count[data-for-startswith='id_summary_'] > b",
    )
    _addon_description_field_locator = (By.ID, "id_description_0")
    _is_experimental_checkbox_locator = (By.ID, "id_is_experimental")
    _requires_payment_checkbox_locator = (By.ID, "id_requires_payment")
    _categories_section_locator = (By.ID, "addon-categories-edit")
    _categories_locator = (
        By.CSS_SELECTOR,
        ".addon-app-cats:nth-of-type(1) > ul input",
    )
    # _android_categories_locator = (
    #     By.CSS_SELECTOR,
    #     ".addon-app-cats:nth-of-type(2) > ul input",
    # )
    _email_input_field_locator = (By.ID, "id_support_email_0")
    _support_site_input_field_locator = (By.ID, "id_support_url_0")
    _license_options_locator = (By.CLASS_NAME, "license")
    _license_details_link_locator = (By.CSS_SELECTOR, ".xx.extra")
    _custom_license_name_locator = (By.ID, "id_license-name")
    _custom_license_text_locator = (By.ID, "id_license-text")
    _privacy_policy_checkbox_locator = (By.ID, "id_has_priv")
    _privacy_policy_textarea_locator = (By.ID, "id_privacy_policy_0")
    _reviewer_notes_textarea_locator = (By.ID, "id_approval_notes")
    _submit_addon_button_locator = (
        By.CSS_SELECTOR,
        ".submission-buttons button:nth-child(1)",
    )
    _cancel_addon_submission_button_locator = (
        By.CSS_SELECTOR,
        ".submission-buttons button:nth-child(2)",
    )
    # _theme_categories_locator = (By.CSS_SELECTOR, '#addon-categories-edit > ul input') - temporary not available
    _theme_categories_locator = (By.CSS_SELECTOR, ".addon-app-cats")
    _theme_category_abstract_locator = (By.CSS_SELECTOR, "#id_categories > div:nth-child(1) > label")
    _theme_licence_sharing_rights_locator = (
        By.CSS_SELECTOR,
        "#cc-chooser ul:nth-of-type(1) input",
    )
    _theme_license_commercial_use_locator = (
        By.CSS_SELECTOR,
        "#cc-chooser ul:nth-of-type(2) input",
    )
    _theme_license_creation_rights_locator = (
        By.CSS_SELECTOR,
        "#cc-chooser ul:nth-of-type(3) input",
    )
    _selected_theme_license_locator = (By.CSS_SELECTOR, "#cc-license")
    _open_theme_licenses_list_locator = (By.CLASS_NAME, "select-license")
    _theme_licenses_list_locator = (By.CSS_SELECTOR, "#id_license-builtin input")

    def wait_for_page_to_load(self):
        self.wait.until(
            EC.visibility_of_element_located(self._addon_summary_field_locator)
        )
        return self

    def set_addon_name(self, value):
        self.find_element(*self._addon_name_field_locator).send_keys(value)

    def clear_addon_name(self):
        self.find_element(*self._addon_name_field_locator).clear()

    @property
    def theme_category_abstract(self):
        return self.find_element(*self._theme_category_abstract_locator)

    @property
    def addon_name_field(self):
        self.wait.until(
            EC.visibility_of_element_located(self._addon_name_field_locator)
        )
        return self.find_element(*self._addon_name_field_locator)

    def edit_addon_slug(self, value):
        self.find_element(*self._edit_addon_slug_link_locator).click()
        edit_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self._edit_addon_slug_field_locator)
        )
        edit_field.send_keys(value)

    def set_addon_summary(self, value):
        self.find_element(*self._addon_summary_field_locator).send_keys(value)

    def addon_detail_fields_info_text(self):
        self.find_elements(*self._addon_detail_fields_info_text_locator)

    @property
    def summary_character_count(self):
        self.wait.until(
            EC.visibility_of_element_located(self._summary_character_count_locator)
        )
        return self.find_element(*self._summary_character_count_locator).text

    def set_addon_description(self, value):
        self.find_element(*self._addon_description_field_locator).send_keys(value)

    @property
    def is_experimental(self):
        self.wait.until(
            EC.visibility_of_element_located(self._is_experimental_checkbox_locator)
        )
        return self.find_element(*self._is_experimental_checkbox_locator)

    @property
    def requires_payment(self):
        self.wait.until(
            EC.visibility_of_element_located(self._requires_payment_checkbox_locator)
        )
        return self.find_element(*self._requires_payment_checkbox_locator)

    @property
    def categories_section(self):
        self.wait.until(
            EC.visibility_of_element_located(self._categories_section_locator)
        )
        return self.find_element(*self._categories_section_locator)

    def select_categories(self, count):
        self.find_elements(*self._categories_locator)[count].click()

    # def select_android_categories(self, count):
    #     self.find_elements(*self._android_categories_locator)[count].click()

    def select_theme_categories(self, count):
        self.find_elements(*self._theme_categories_locator)[count].click()

    def email_input_field(self, value):
        self.find_element(*self._email_input_field_locator).send_keys(value)

    def support_site_input_field(self, value):
        self.find_element(*self._support_site_input_field_locator).send_keys(value)

    @property
    def select_license_options(self):
        self.wait.until(EC.visibility_of_element_located(self._license_options_locator))
        return self.find_elements(*self._license_options_locator)

    def license_option_names(self, count, value):
        return self.select_license_options[count].get_attribute(value)

    def license_details_link(self):
        self.wait.until(
            EC.visibility_of_element_located(self._license_details_link_locator)
        )
        self.find_element(*self._license_details_link_locator).click()

    def set_custom_license_name(self, value):
        self.wait.until(
            EC.visibility_of_element_located(self._custom_license_name_locator)
        )
        self.find_element(*self._custom_license_name_locator).send_keys(value)

    def set_custom_license_text(self, value):
        self.wait.until(
            EC.visibility_of_element_located(self._custom_license_text_locator)
        )
        self.find_element(*self._custom_license_text_locator).send_keys(value)

    def select_theme_licence_sharing_rights(self, count):
        self.wait.until(
            EC.visibility_of_element_located(self._theme_licence_sharing_rights_locator)
        )
        self.find_elements(*self._theme_licence_sharing_rights_locator)[count].click()

    def select_theme_license_commercial_use(self, count):
        self.wait.until(
            EC.visibility_of_element_located(self._theme_license_commercial_use_locator)
        )
        self.find_elements(*self._theme_license_commercial_use_locator)[count].click()

    def select_theme_license_creation_rights(self, count):
        self.find_elements(*self._theme_license_creation_rights_locator)[count].click()

    @property
    def generated_theme_license(self):
        self.wait.until(
            EC.visibility_of_element_located(self._selected_theme_license_locator)
        )
        return self.find_element(*self._selected_theme_license_locator)

    def open_theme_licenses_list(self):
        self.wait.until(
            EC.visibility_of_element_located(self._open_theme_licenses_list_locator)
        )
        self.find_element(*self._open_theme_licenses_list_locator).click()

    def select_theme_license_from_list(self):
        self.wait.until(
            EC.visibility_of_element_located(self._theme_licenses_list_locator)
        )
        self.find_elements(*self._theme_licenses_list_locator)

    def set_privacy_policy(self, value):
        self.wait.until(
            EC.element_to_be_clickable(self._privacy_policy_checkbox_locator)
        )
        self.find_element(*self._privacy_policy_checkbox_locator).click()
        self.find_element(*self._privacy_policy_textarea_locator).send_keys(value)

    def set_reviewer_notes(self, value):
        self.find_element(*self._reviewer_notes_textarea_locator).send_keys(value)

    def submit_addon(self):
        self.find_element(*self._submit_addon_button_locator).click()
        return SubmissionConfirmationPage(
            self.driver, self.base_url
        ).wait_for_page_to_load()

    def cancel_submission(self):
        self.find_element(*self._cancel_addon_submission_button_locator).click()
        from pages.desktop.developers.edit_addon import EditAddon

        return EditAddon(self.driver, self.base_url).wait_for_page_to_load()


class ThemeWizard(Page):
    _wizard_header_locator = (By.CSS_SELECTOR, ".addon-submission-process > h3")
    _theme_name_input_field = (By.ID, "theme-name")
    _upload_theme_image_button_locator = (By.ID, "header-img")
    _uploaded_image_preview_locator = (By.CLASS_NAME, "preview.loaded")
    _change_image_button_locator = (By.CLASS_NAME, "reset")
    _browser_preview_locator = (By.ID, "preview-svg-root")
    _browser_preview_header_image_locator = (By.ID, "svg-header-img")
    _submit_theme_button_locator = (By.CLASS_NAME, "button.upload")
    _cancel_submission_button_locator = (
        By.CSS_SELECTOR,
        ".submission-buttons .delete-button",
    )

    def wait_for_page_to_load(self):
        self.wait.until(EC.visibility_of_element_located((By.ID, "theme-header")))
        return self

    @property
    def wizard_header(self):
        self.wait.until(EC.visibility_of_element_located(self._wizard_header_locator))
        return self.find_element(*self._wizard_header_locator).text

    def set_theme_name(self, value):
        self.find_element(*self._theme_name_input_field).send_keys(value)

    def upload_theme_header(self, img):
        button = self.find_element(*self._upload_theme_image_button_locator)
        header_img = Path(f"{os.getcwd()}/img/{img}")
        button.send_keys(str(header_img))

    @property
    def uploaded_image_preview(self):
        self.wait.until(
            EC.visibility_of_element_located(self._uploaded_image_preview_locator)
        )
        return self.find_element(*self._uploaded_image_preview_locator)

    @property
    def uploaded_image_source(self):
        """Fetch the source of the uploaded theme image"""
        return self.uploaded_image_preview.get_attribute("src")

    @property
    def browser_preview(self):
        self.wait.until(EC.visibility_of_element_located(self._browser_preview_locator))
        return self.find_element(*self._browser_preview_locator)

    @property
    def browser_preview_image(self):
        """Fetch the source of tha generated theme preview image"""
        return self.find_element(
            *self._browser_preview_header_image_locator
        ).get_attribute("href")

    def submit_theme(self):
        self.find_element(*self._submit_theme_button_locator).click()
        time.sleep(10)
        return ListedAddonSubmissionForm(
            self.driver, self.base_url
        ).wait_for_page_to_load()

    def cancel_submission(self):
        self.find_element(*self._cancel_submission_button_locator).click()
        return SubmitAddon(self.driver, self.base_url).wait_for_page_to_load()


class SubmissionConfirmationPage(Page):
    _confirmation_page_header_locator = (
        By.CSS_SELECTOR,
        ".addon-submission-process h3",
    )
    _confirmation_messages_locator = (By.CSS_SELECTOR, ".addon-submission-process p")
    _manage_listing_button_locator = (By.LINK_TEXT, "Go to My Submissions")
    _edit_version_button_locator = (
        By.CSS_SELECTOR,
        ".addon-submission-process p:nth-child(6) > a",
    )
    _edit_listing_button_locator = (By.LINK_TEXT, "Manage Listing")
    _theme_preview_locator = (By.CSS_SELECTOR, ".addon-submission-process img")

    def wait_for_page_to_load(self):
        self.wait.until(
            EC.visibility_of_element_located(self._confirmation_page_header_locator)
        )
        return self

    @property
    def submission_confirmation_messages(self):
        self.wait.until(
            EC.visibility_of_element_located(self._confirmation_messages_locator)
        )
        return self.find_elements(*self._confirmation_messages_locator)

    def click_manage_listing_button(self):
        self.wait.until(EC.element_to_be_clickable(self._manage_listing_button_locator))
        self.find_element(*self._manage_listing_button_locator).click()
        from pages.desktop.developers.addons_manage import ManageAddons

        return ManageAddons(self.driver, self.base_url).wait_for_page_to_load()

    def click_edit_version_button(self):
        self.wait.until(EC.element_to_be_clickable(self._edit_version_button_locator))
        self.find_element(*self._edit_version_button_locator).click()
        return ManageVersions(self.driver, self.base_url)

    def click_edit_listing_button(self):
        self.wait.until(EC.element_to_be_clickable(self._edit_listing_button_locator))
        self.find_element(*self._edit_listing_button_locator).click()
        from pages.desktop.developers.edit_addon import EditAddon

        return EditAddon(self.driver, self.base_url).wait_for_page_to_load()

    @property
    def generated_theme_preview(self):
        return self.find_element(*self._theme_preview_locator)
