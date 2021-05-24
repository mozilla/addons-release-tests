from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expected

from pages.desktop.base import Base


class User(Base):
    _display_name_locator = (By.CLASS_NAME, 'UserProfile-name')

    def wait_for_page_to_load(self):
        """Waits for various page components to be loaded"""
        self.wait.until(
            expected.invisibility_of_element_located(
                (By.CLASS_NAME, 'LoadingText')))
        return self

    @property
    def user_display_name(self):
        return self.find_element(*self._display_name_locator).text
