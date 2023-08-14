import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.base import Base
from pages.desktop.developers.submit_addon import SubmitAddon
from pathlib import Path


class EditAddon(Base):
    """Edit page for a specific addon."""

    _root_locator = (By.CLASS_NAME, "section")
    _edit_addon_navbar_locator = (By.CLASS_NAME, "edit-addon-nav")
    _addon_name_locator = (By.CSS_SELECTOR, ".section header h2")
    _listed_addon_status_locator = (By.CSS_SELECTOR, ".addon-listed-status a")
    _last_modified_date_locator = (By.CLASS_NAME, "date-updated")
    _unlisted_version_tooltip_locator = (
        By.CLASS_NAME,
        "distribution-tag-unlisted.tooltip",
    )
    _submit_new_version_link_locator = (By.CLASS_NAME, "version-upload")
    _manage_versions_link_locator = (
        By.CSS_SELECTOR,
        "#edit-addon-nav ul:nth-child(1) li:nth-child(3)",
    )
    _edit_addon_images_button_locator = (By.CSS_SELECTOR, "#edit-addon-media a")
    _edit_addon_images_save_changes_button = (
        By.CSS_SELECTOR,
        ".edit-media-button button",
    )
    _images_icon_label_locator = (
        By.CSS_SELECTOR,
        "table > tbody:nth-child(2) > tr:nth-child(1) > th:nth-child(1) > span",
    )
    _images_screenshot_locator = (
        By.CSS_SELECTOR,
        "table > tbody:nth-child(2) > tr:nth-child(2) > th:nth-child(1) > label",
    )
    _upload_icon_button = (By.ID, "id_icon_upload")
    _upload_screenshot_button = (By.ID, "screenshot_upload")
    _text_error_uploading_screenshot_locator = (
        By.CSS_SELECTOR,
        "div.edit-previews-text.error strong",
    )
    _text_error_details_screenshot_locator = (
        By.CSS_SELECTOR,
        "div.edit-previews-text.error > ul:nth-child(2) > li",
    )

    def wait_for_page_to_load(self):
        self.wait.until(lambda _: self.is_element_displayed(*self._addon_name_locator))
        return self

    @property
    def name(self):
        return self.find_element(*self._addon_name_locator).text

    @property
    def listed_addon_status(self):
        return self.find_element(*self._listed_addon_status_locator).text

    def click_upload_version_link(self):
        self.wait.until(
            EC.element_to_be_clickable(self._submit_new_version_link_locator)
        ).click()
        return SubmitAddon(self.selenium, self.base_url).wait_for_page_to_load()

    @property
    def unlisted_version_tooltip(self):
        return self.find_element(*self._unlisted_version_tooltip_locator)

    @property
    def last_modified_date(self):
        """Get the date string from the Last Update date section and format it"""
        site_date = (
            self.find_element(*self._last_modified_date_locator)
            .text.split("Last Updated: ")[1]
            .replace(".", "")
        )
        month = site_date.split()[0]
        # get only the first three letters in the month to have a uniform date structure
        final_date = site_date.replace(month, month[0:3])
        return final_date

    @property
    def edit_addon_images(self):
        return self.find_element(*self._edit_addon_images_button_locator)

    @property
    def images_icon_label_locator(self):
        return self.find_element(*self._images_icon_label_locator)

    @property
    def images_screenshot_locator(self):
        return self.find_element(*self._images_screenshot_locator)

    @property
    def upload_icon_button_locator(self):
        return self.find_element(*self._upload_icon_button)

    @property
    def upload_screenshot_button_locator(self):
        return self.find_element(*self._upload_screenshot_button)

    @property
    def edit_addon_images_save_changes_button_locator(self):
        return self.find_element(*self._edit_addon_images_save_changes_button)

    @property
    def text_error_uploading_screenshot(self):
        return self.find_element(*self._text_error_uploading_screenshot_locator)

    @property
    def text_error_details_screenshot(self):
        return self.find_element(*self._text_error_details_screenshot_locator)

    # Click methods

    def click_edit_addon_images_button_locator(self):
        return self.find_element(*self._edit_addon_images_button_locator).click()

    def click_upload_icon_button(self):
        return self.find_element(*self._upload_icon_button).click()

    def click_upload_screenshot_button(self):
        return self.find_element(*self._upload_screenshot_button)[1].click()

    def click_edit_addon_images_save_changes_button_locator(self):
        return self.find_element(*self._edit_addon_images_save_changes_button)

    def click_manage_versions_link(self):
        self.find_element(*self._manage_versions_link_locator).click()
        from pages.desktop.developers.manage_versions import ManageVersions

        return ManageVersions(self.driver, self.base_url).wait_for_page_to_load()

    @staticmethod
    def open_edit_page_for_addon(selenium, base_url, addon):
        return selenium.get(f"{base_url}/developers/addon/{addon}/edit")

    # Wait Methods
    def wait_for_images_section_to_load(self):
        self.wait.until(
            EC.visibility_of_element_located(
                self._edit_addon_images_save_changes_button
            )
        )

    def wait_for_screenshot_errors(self):
        self.wait.until(
            EC.visibility_of_element_located(
                self._text_error_uploading_screenshot_locator
            )
        )

    def upload_screenshot(self, img):
        """General method for uploading a file"""
        button = self.find_element(*self._upload_screenshot_button)
        archive = Path(f"{os.getcwd()}/img/{img}")
        button.send_keys(str(archive))
