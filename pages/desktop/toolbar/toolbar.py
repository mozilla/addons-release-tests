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
    _extensions_menu_label_name_locator = (By.CSS_SELECTOR, "label[class='unified-extensions-item-name']")
    _extensions_menu_wheel_button_locator = (By.CSS_SELECTOR, ".unified-extensions-item-menu-button")
    _unified_extensions_discover_extensions_locator = (By.ID, ".unified-extensions-discover-extensions")
    _wheel_option_manage_extension_locator = (By.ID, "unified-extensions-context-menu-manage-extension")
    _wheel_option_remove_extension_locator = (By.ID, "unified-extensions-context-menu-remove-extension")
    _wheel_option_report_extension_locator = (By.ID, "unified-extensions-context-menu-report-extension")
    _panel_ui_menu_button_locator = (By.ID, "PanelUI-menu-button")
    _panel_ui_menu_extensions_and_themes_locator = (By.ID, "appMenu-extensions-themes-button")
    _panel_ui_menu_new_private_window_locator = (By.ID, "appMenu-new-private-window-button2")
    _panel_ui_container_locator = (By.ID, "appMenu-mainView")

    @property
    def manage_extension_toolbar(self):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.wait.until(
                EC.visibility_of_element_located(self._manage_extension_button_locator)
            )
            return self.find_element(*self._manage_extension_button_locator)

    @property
    def extensions_menu_addon(self):
        self.wait.until(
            EC.visibility_of_element_located(self._extensions_menu_addon_locator)
        )
        return self.find_element(*self._extensions_menu_addon_locator)

    @property
    def panel_ui_container(self):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.wait.until(
                EC.visibility_of_element_located(self._panel_ui_container_locator)
            )
            return self.find_element(*self._panel_ui_container_locator)

    @property
    def extensions_menu_label_name(self):
        # with self.driver.context(self.driver.CONTEXT_CHROME):
        self.wait.until(
            EC.visibility_of_element_located(self._extensions_menu_label_name_locator)
        )
        return self.find_element(*self._extensions_menu_label_name_locator)

    def click_panel_ui_menu(self):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.wait.until(
                EC.visibility_of_element_located(self._panel_ui_menu_button_locator)
            )
            self.find_element(*self._panel_ui_menu_button_locator).click()

    def open_new_private_window(self):
        """Click the hamburger menu's "New Private Window" entry and return
        the window handle of the new private window."""
        existing = set(self.driver.window_handles)
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.wait.until(
                EC.visibility_of_element_located(self._panel_ui_menu_button_locator)
            )
            self.find_element(*self._panel_ui_menu_button_locator).click()
            # The button id changed between Firefox versions; try the current
            # id first and fall back to the legacy one.
            try:
                btn = self.find_element(*self._panel_ui_menu_new_private_window_locator)
            except NoSuchElementException:
                btn = self.driver.execute_script(
                    "return document.getElementById('appMenu-new-private-window-button');"
                )
            btn.click()
        self.wait.until(
            lambda d: len(d.window_handles) == len(existing) + 1,
            message="Private window did not open",
        )
        new_handle = (set(self.driver.window_handles) - existing).pop()
        return new_handle

    def click_panel_ui_extensions_and_themes(self):
        existing_handles = list(self.driver.window_handles)
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.wait.until(
                EC.visibility_of_element_located(self._panel_ui_menu_extensions_and_themes_locator)
            )
            self.find_element(*self._panel_ui_menu_extensions_and_themes_locator).click()
        # Recent Firefox versions navigate the current tab to about:addons; older
        # builds open it in a new tab. Wait for either condition and switch into
        # the tab that is now on about:addons.
        self.wait.until(
            lambda d: (
                len(d.window_handles) > len(existing_handles)
                or "about:addons" in d.current_url
            ),
            message="Add-ons Manager did not open via the hamburger menu",
        )
        new_handles = [h for h in self.driver.window_handles if h not in existing_handles]
        if new_handles:
            self.driver.switch_to.window(new_handles[0])
        return AboutAddons(self.driver, self.base_url).wait_for_page_to_load()

    def click_manage_extension_button_no_addon(self):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.wait.until(
                EC.visibility_of_element_located(self._manage_extension_button_locator)
            )
            self.find_element(*self._manage_extension_button_locator).click()
            host = self.driver.execute_script("""
                    return document.querySelector("button[id='main-button']");
                """)
            host.click()
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
