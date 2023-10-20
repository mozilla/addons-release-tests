from pypom import Page

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class ManageAuthorsAndLicenses(Page):
    _radio_button_mozilla_public_license_selector = (By.XPATH, 'id_builtin_0')
    _radio_button_gnu_general_public_license_selector = (By.ID, 'id_builtin_1')
    _save_changes_button_selector = (By.CSS_SELECTOR, 'div.listing-footer button')
    _notification_box_success_selector = (By.CSS_SELECTOR, '.notification-box > h2:nth-child(1)')
    _authors_text_selector = (By.CSS_SELECTOR, 'tbody:nth-child(1) > tr:nth-child(1) > th')
    _licenses_text_selector = (By.CSS_SELECTOR, 'tbody:nth-child(1) > tr:nth-child(3) > th:nth-child(1) > span')
    _license_agreement_selector = (By.CSS_SELECTOR, 'tbody:nth-child(1) > tr:nth-child(4) > th:nth-child(1) > span')
    _license_agreement_checkbox = (By.ID, 'id_has_eula')
    _please_specify_license_text_selector = (By.CSS_SELECTOR, '.eula > label:nth-child(1)')
    _license_agreement_textbox_selector = (By.ID, 'id_eula_0')
    _privacy_policy_selector = (By.CSS_SELECTOR, 'tbody:nth-child(1) > tr:nth-child(5) > th:nth-child(1) > span')
    _privacy_policy_checkbox_selector = (By.ID, 'id_has_priv')
    _please_specify_privacy_policy_text_selector = (By.CSS_SELECTOR, '.priv > label:nth-child(1)')
    _privacy_policy_textbox_selector = (By.ID, 'id_privacy_policy_0')


    @property
    def radio_button_mozilla_public_license(self):
        return self.find_element(*self._radio_button_mozilla_public_license_selector)

    @property
    def radio_button_general_public_license(self):
        return self.find_element(*self._radio_button_gnu_general_public_license_selector)

    @property
    def notification_box_success(self):
        return self.find_element(*self._notification_box_success_selector)

    @property
    def authors_text_element(self):
        return self.find_element(*self._authors_text_selector)

    @property
    def license_text_element(self):
        return self.find_element(*self._licenses_text_selector)

    @property
    def license_agreement_selector(self):
        return self.find_element(*self._license_agreement_selector)

    @property
    def license_agreement_checkbox(self):
        return self.find_element(*self._license_agreement_checkbox)

    @property
    def please_specify_license_text(self):
        return self.find_element(*self._please_specify_license_text_selector)

    @property
    def license_agreeement_textbox(self):
        return self.find_element(*self._license_agreement_textbox_selector)

    @property
    def privacy_policy(self):
        return self.find_element(*self._privacy_policy_selector)

    @property
    def privacy_policy_checkbox(self):
        return self.find_element(*self._privacy_policy_checkbox_selector)

    @property
    def please_specify_privacy_policy_text(self):
        return self.find_element(*self._please_specify_privacy_policy_text_selector)

    @property
    def privacy_policy_textbox(self):
        return self.find_element(*self._privacy_policy_textbox_selector)

    @staticmethod
    def open_manage_authors_and_licenses_page(selenium, base_url, addon):
        return selenium.get(f"{base_url}/developers/addon/{addon}/ownership")

    def wait_for_page_to_load(self):
        self.wait.until(
            EC.visibility_of_element_located(self._radio_button_gnu_general_public_license_selector)
        )
        return self

    def wait_for_notification_box_success(self):
        self.wait.until(
            EC.visibility_of_element_located(self._notification_box_success_selector)
        )
        return self

    def click_mozilla_public_license(self):
        return self.find_element(*self._radio_button_mozilla_public_license_selector).click()

    def click_general_public_license(self):
        return self.find_element(*self._radio_button_gnu_general_public_license_selector).click()

    def click_save_changes_button(self):
        return self.find_element(*self._save_changes_button_selector).click()