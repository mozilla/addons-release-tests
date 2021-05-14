from selenium.webdriver.common.by import By

from pages.desktop.base import Base


class User(Base):
    _display_name_locator = (By.CLASS_NAME, 'UserProfile-name')

    def wait_for_user_to_load(self):
        self.wait.until(
            lambda _: self.is_element_displayed(*self._display_name_locator))
        return self

    @property
    def user_display_name(self):
        return self.find_element(*self._display_name_locator).text
