from selenium.webdriver.common.by import By

from pages.desktop.base import Base


class SubmitAddon(Base):

    _my_addons_page_logo_locator = (By.CSS_SELECTOR, '.site-titles')
    _submission_form_header_locator = (By.CSS_SELECTOR, '.is_addon')

    @property
    def my_addons_page_logo(self):
        return self.find_element(*self._my_addons_page_logo_locator)

    @property
    def submission_form_header(self):
        return self.find_element(*self._submission_form_header_locator)
