from pypom import Page

from selenium.webdriver.common.by import By


class AboutDebug(Page):
    _qa_runtime_name_locator = (By.XPATH, "//label[contains(text(),'Mozilla Firefox')]")

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._qa_runtime_name_locator).is_displayed(),
            message="about:debugging runtime page did not load",
        )
        return self
