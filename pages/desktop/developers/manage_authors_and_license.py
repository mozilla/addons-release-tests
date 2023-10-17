import time

import pytest
from pypom import Region, Page

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class ManageAuthorsAndLicenses(Page):
    _radio_button_mozilla_public_license_selector = (By.XPATH, '//*[@data-name="Mozilla Public License 2.0"]')
    _radio_button_gnu_general_public_license_selector = (By.ID, 'authors_pending_confirmation')
    _save_changes_button_selector = (By.CSS_SELECTOR, 'div.listing-footer button')
    _notification_box_success_selector = (By.CSS_SELECTOR, '.notification-box')

    @property
    def radio_button_mozilla_public_license(self):
        return self.find_element(*self._radio_button_mozilla_public_license_selector)

    @property
    def radio_button_general_public_license(self):
        return self.find_element(*self._radio_button_gnu_general_public_license_selector)

    @property
    def notification_box_success(self):
        return self.find_element(*self._notification_box_success_selector)

    @staticmethod
    def open_manage_authors_and_licenses_page(selenium, base_url, addon):
        return selenium.get(f"{base_url}/developers/addon/{addon}/ownership")

    def wait_for_page_to_load(self):
        self.wait.until(
            EC.visibility_of_element_located(*self._radio_button_gnu_general_public_license_selector)
        )
        return

    def wait_for_notification_box_success(self):
        self.wait.until(
            EC.visibility_of_element_located(*self._notification_box_success_selector)
        )
        return

    def click_mozilla_public_license(self):
        return self.find_element(*self._radio_button_mozilla_public_license_selector).click()

    def click_general_public_license(self):
        return self.find_element(*self._radio_button_gnu_general_public_license_selector).click()

    def click_save_changes_button(self):
        return self.find_element(*self._save_changes_button_selector).click()