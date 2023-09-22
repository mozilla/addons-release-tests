import os

from pages.desktop.base import Base
from selenium.webdriver.common.by import By
from pathlib import Path

from selenium.webdriver.support import expected_conditions as EC


class DevhubAddonValidate(Base):
    """AMO Developer Hub Validate Add-on Page"""

    URL_TEMPLATE = "developers/addon/validate"

    # Locators
    _create_addon_form = (By.ID, "create-addon")
    _addon_on_your_site = (
        By.CSS_SELECTOR,
        "#id_channel > div:nth-child(1) > label:nth-child(1)",
    )
    _addon_on_your_own = (
        By.CSS_SELECTOR,
        "#id_channel > div:nth-child(2) > label:nth-child(1)",
    )
    _upload_addon_button = (By.ID, "upload-addon")
    _firefox_app = (By.CSS_SELECTOR,)
    _create_addon_paragraph = (By.CSS_SELECTOR, ".create-addon p")
    _list_addon_label = (By.CSS_SELECTOR, ".list-addon label")
    _on_this_site_checkbox = (By.CSS_SELECTOR, "#id_channel_0")
    _on_your_own_text_checkbox = (By.CSS_SELECTOR, "#id_channel_1")
    _upload_details_text = (By.CSS_SELECTOR, ".upload-details")
    _upload_status_results_succes = (By.ID, "upload-status-results")
    _upload_status_results_failed = (
        By.CSS_SELECTOR,
        "div.upload-status div.status-fail strong",
    )
    _upload_status_bar_results_approved = (By.CSS_SELECTOR, "div.bar-success")
    _upload_status_bar_results_failed = (By.CSS_SELECTOR, "div.bar-fail")
    _upload_status = (By.ID, "uploadstatus")
    _upload_errors = (By.ID, "upload_errors")

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._create_addon_form).is_displayed()
        )
        return self

    def is_validation_approved(self):
        """Wait for addon validation to complete; if not successful, the test will fail"""
        self.wait.until(
            EC.visibility_of_element_located(self._upload_status_bar_results_approved)
        )

    def is_not_validated(self):
        """Wait for addon validation to complete; if successful, the test will fail"""
        self.wait.until(
            EC.visibility_of_element_located(self._upload_status_bar_results_failed)
        )

    @property
    def addon_on_your_site(self):
        self.wait_for_element_to_be_displayed(self._addon_on_your_site)
        return self.find_element(*self._addon_on_your_site)

    @property
    def addon_on_your_own(self):
        self.wait_for_element_to_be_displayed(self._addon_on_your_own)
        return self.find_element(*self._addon_on_your_own)

    @property
    def create_addon_paragraph(self):
        self.wait_for_element_to_be_displayed(self._create_addon_paragraph)
        return self.find_element(*self._create_addon_paragraph)

    @property
    def list_addon_label(self):
        self.wait_for_element_to_be_displayed(self._list_addon_label)
        return self.find_element(*self._list_addon_label)

    @property
    def on_this_site_checkbox(self):
        self.wait_for_element_to_be_displayed(self._on_this_site_checkbox)
        return self.find_element(*self._on_this_site_checkbox)

    @property
    def on_your_own_text_checkbox(self):
        self.wait_for_element_to_be_displayed(self._on_your_own_text_checkbox)
        return self.find_element(*self._on_your_own_text_checkbox)

    @property
    def upload_details_text(self):
        self.wait_for_element_to_be_displayed(self._upload_details_text)
        return self.find_element(*self._upload_details_text)

    @property
    def upload_details_results_succes(self):
        self.wait_for_element_to_be_displayed(self._upload_status_results_succes)
        return self.find_element(*self._upload_status_results_succes)

    @property
    def upload_details_results_failed(self):
        self.wait_for_element_to_be_displayed(self._upload_status_results_failed)
        return self.find_element(*self._upload_status_results_failed)

    @property
    def upload_status(self):
        self.wait_for_element_to_be_displayed(self._upload_status)
        return self.find_element(*self._upload_status)

    @property
    def upload_errors(self):
        self.wait_for_element_to_be_displayed(self._upload_errors)
        return self.find_element(*self._upload_errors)

    def click_on_this_site_checkbox(self):
        self.wait_for_element_to_be_clickable(self._on_this_site_checkbox)
        return self.find_element(*self._on_this_site_checkbox).click()

    def click_on_your_own_text_checkbox(self):
        self.wait_for_element_to_be_clickable(self._on_your_own_text_checkbox)
        return self.find_element(*self._on_your_own_text_checkbox).click()

    def click_upload_addon_button(self):
        self.wait_for_element_to_be_clickable(self._upload_addon_button)
        self.find_element(*self._upload_addon_button).click()

    def upload_file(self, addon):
        # Upload given file on the AMO DevHub Validate Page
        button = self.find_element(*self._upload_addon_button)
        archive = Path(f"{os.getcwd()}/sample-addons/{addon}")
        button.send_keys(str(archive))
