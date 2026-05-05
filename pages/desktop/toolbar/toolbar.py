from pypom import Page

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class Toolbar(Page):
    _unified_extensions_button_locator = (By.ID, "unified-extensions-button")
    _extension_item_menu_button_locator = (
        By.CSS_SELECTOR,
        ".unified-extensions-item-menu-button",
    )
    _menu_manage_extension_locator = (
        By.ID,
        "unified-extensions-context-menu-manage-extension",
    )
    _menu_remove_extension_locator = (
        By.ID,
        "unified-extensions-context-menu-remove-extension",
    )
    _menu_report_extension_locator = (
        By.ID,
        "unified-extensions-context-menu-report-extension",
    )

    def open_unified_extensions_panel(self):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.wait.until(
                EC.visibility_of_element_located(
                    self._unified_extensions_button_locator
                )
            )
            self.find_element(*self._unified_extensions_button_locator).click()
            self.wait.until(
                EC.visibility_of_element_located(
                    self._extension_item_menu_button_locator
                )
            )

    def open_extension_item_menu(self, index=0):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.wait.until(
                EC.visibility_of_element_located(
                    self._extension_item_menu_button_locator
                )
            )
            self.find_elements(*self._extension_item_menu_button_locator)[index].click()
            self.wait.until(
                EC.visibility_of_element_located(self._menu_manage_extension_locator)
            )

    @property
    def menu_options_present(self):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            ids = []
            for locator in (
                self._menu_manage_extension_locator,
                self._menu_remove_extension_locator,
                self._menu_report_extension_locator,
            ):
                try:
                    el = self.find_element(*locator)
                    if el.is_displayed():
                        ids.append(el.get_attribute("id"))
                except NoSuchElementException:
                    continue
            return ids

    def click_manage_extension(self):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.find_element(*self._menu_manage_extension_locator).click()

    def click_remove_extension(self):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.find_element(*self._menu_remove_extension_locator).click()

    def click_report_extension(self):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.find_element(*self._menu_report_extension_locator).click()
