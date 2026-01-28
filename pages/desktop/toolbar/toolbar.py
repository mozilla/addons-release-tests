from time import sleep
from pypom import Page, Region

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from pages.desktop.about_addons import AboutAddons


class Toolbar(Page):
    _manage_extension_button_locator = (By.ID, "unified-extensions-button")
    _extensions_menu_addon_locator = (By.CSS_SELECTOR, ".unified-extensions-item-action-button")
    _extensions_menu_wheel_button_locator = (By.CSS_SELECTOR, ".unified-extensions-item-menu-button")
    _wheel_option_manage_extension_locator = (By.ID, "unified-extensions-context-menu-manage-extension")
    _wheel_option_remove_extension_locator = (By.ID, "unified-extensions-context-menu-remove-extension")
    _wheel_option_report_extension_locator = (By.ID, "unified-extensions-context-menu-report-extension")

    def click_manage_extension_button_no_addon(self):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.wait.until(
                EC.visibility_of_element_located(self._manage_extension_button_locator)
            )
            self.find_element(*self._manage_extension_button_locator).click()
        self.wait.until(
            EC.number_of_windows_to_be(2),
            message=f"Number of windows was {len(self.driver.window_handles)}, expected 2",
        )
        self.driver.switch_to.window(self.driver.window_handles[1])
        return AboutAddons(self.driver, self.base_url).wait_for_page_to_load()

    def click_toolbar_extension_button(self):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.wait.until(
                EC.visibility_of_element_located(self._manage_extension_button_locator)
            )
            self.find_element(*self._manage_extension_button_locator).click()

    def click_toolbar_extension_wheel_options_buttons(self, value="MANAGE_EXTENSION"):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.wait.until(
                EC.visibility_of_element_located(self._extensions_menu_wheel_button_locator)
            )
            self.find_element(*self._extensions_menu_wheel_button_locator).click()
            if value == "MANAGE_EXTENSION":
                self.wait.until(
                    EC.visibility_of_element_located(self._wheel_option_manage_extension_locator)
                )
                self.find_element(*self._wheel_option_manage_extension_locator).click()
