from pypom import Page, Region

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC


class ViewRecentUpdates(Page):
    _header_name_locator = (By.XPATH, "//h1[contains(text(), 'Manage Your Updates')]")
    _list_section_name_locator = (By.XPATH, "//h2[contains(text(), 'Recent Updates')]")

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._header_name_locator).is_displayed(),
            message="View Recent Updates was not loaded",
        )
        return self

    @property
    def list_section_name(self):
        self.wait.until(
            EC.visibility_of_element_located(self._list_section_name_locator)
        )
        return self.find_element(*self._list_section_name_locator)

