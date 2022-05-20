from selenium.webdriver.common.by import By

from pages.desktop.base import Base


class EditAddon(Base):
    """Edit page for a specific addon."""

    _root_locator = (By.CLASS_NAME, 'section')
    _edit_addon_navbar_locator = (By.CLASS_NAME, 'edit-addon-nav')
    _addon_name_locator = (By.CSS_SELECTOR, '.section header h2')
    _listed_addon_status_locator = (By.CSS_SELECTOR, '.addon-listed-status a')
    _last_modified_date_locator = (By.CLASS_NAME, 'date-updated')
    _manage_versions_link_locator = (
        By.CSS_SELECTOR,
        '#edit-addon-nav ul:nth-child(1) li:nth-child(3)',
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

    @property
    def last_modified_date(self):
        """Get the date string from the Last Update date section and format it"""
        return (
            self.find_element(*self._last_modified_date_locator)
            .text.split('Last Updated: ')[1]
            .replace('.', '')
        )

    def click_manage_versions_link(self):
        self.find_element(*self._manage_versions_link_locator).click()
        from pages.desktop.developers.manage_versions import ManageVersions

        return ManageVersions(self.selenium, self.base_url).wait_for_page_to_load()
