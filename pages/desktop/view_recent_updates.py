from pypom import Page

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class ViewRecentUpdates(Page):
    _header_name_locator = (By.XPATH, "//h1[contains(text(), 'Manage Your Updates')]")
    _list_section_name_locator = (By.XPATH, "//h2[contains(text(), 'Recent Updates')]")
    _addon_card_locator = (By.CSS_SELECTOR, ".card.addon")
    _addon_name_locator = (By.CSS_SELECTOR, ".addon-name a")

    def wait_for_page_to_load(self):
        self.wait.until(
            EC.visibility_of_element_located(self._header_name_locator),
            message="View Recent Updates page did not load",
        )
        return self

    @property
    def list_section_name(self):
        self.wait.until(
            EC.visibility_of_element_located(self._list_section_name_locator)
        )
        return self.find_element(*self._list_section_name_locator)

    @property
    def addon_names(self):
        self.wait.until(EC.visibility_of_element_located(self._addon_card_locator))
        return [el.text for el in self.find_elements(*self._addon_name_locator)]
