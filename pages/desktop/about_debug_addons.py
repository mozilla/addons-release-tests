from pypom import Page, Region

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC


class AboutDebug(Page):
    _qa_runtime_name_locator = (By.XPATH, "//label[contains(text(),'Mozilla Firefox')]")

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._qa_runtime_name_locator).is_displayed(),
            message="About Debug Page was not loaded",
        )
        return self
