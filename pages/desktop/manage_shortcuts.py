from pypom import Page

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class ManageShortcuts(Page):
    _header_locator = (
        By.XPATH,
        "//h1[contains(text(), 'Manage Extension Shortcuts')]",
    )
    _back_button_locator = (By.CSS_SELECTOR, "button.back-button")
    _shortcut_card_locator = (By.CSS_SELECTOR, ".card.shortcut")
    _shortcut_input_locator = (By.CSS_SELECTOR, ".shortcut-input")
    _no_shortcuts_section_locator = (
        By.XPATH,
        "//*[contains(text(), 'do not have shortcuts')]",
    )
    _no_shortcuts_addon_name_locator = (
        By.CSS_SELECTOR,
        ".shortcuts-no-commands-list .addon-name",
    )

    def wait_for_page_to_load(self):
        self.wait.until(
            EC.visibility_of_element_located(self._header_locator),
            message="Manage Extension Shortcuts header did not appear",
        )
        return self

    @property
    def header(self):
        return self.find_element(*self._header_locator)

    @property
    def shortcut_cards(self):
        return self.find_elements(*self._shortcut_card_locator)

    @property
    def shortcut_inputs(self):
        return self.find_elements(*self._shortcut_input_locator)

    @property
    def no_shortcuts_section_visible(self):
        try:
            return self.find_element(
                *self._no_shortcuts_section_locator
            ).is_displayed()
        except NoSuchElementException:
            return False

    @property
    def no_shortcuts_addons(self):
        return [el.text for el in self.find_elements(*self._no_shortcuts_addon_name_locator)]

    def click_back(self):
        self.wait.until(EC.element_to_be_clickable(self._back_button_locator))
        self.find_element(*self._back_button_locator).click()
