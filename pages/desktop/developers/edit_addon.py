from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.base import Base
from pages.desktop.developers.submit_addon import SubmitAddon


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

    def wait_for_page_to_load(self):
        self.wait.until(lambda _: self.is_element_displayed(*self._addon_name_locator))
        return self

    @property
    def name(self):
        self.wait_for_element_to_be_displayed(self._addon_name_locator)
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
        self.wait_for_element_to_be_displayed(self._unlisted_version_tooltip_locator)
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

    def click_manage_versions_link(self):
        self.wait_for_element_to_be_clickable(self._manage_versions_link_locator)
        self.find_element(*self._manage_versions_link_locator).click()
        from pages.desktop.developers.manage_versions import ManageVersions

        return ManageVersions(self.driver, self.base_url).wait_for_page_to_load()
