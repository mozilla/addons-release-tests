from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from pages.desktop.base import Base


class DevHub(Base):
    """AMO Developer Hub homepage"""

    URL_TEMPLATE = 'developers/'

    _logo_locator = (By.CLASS_NAME, 'DevHub-Navigation-Logo')
    _footer_language_picker_locator = (By.ID, 'language')
    _footer_products_section_locator = (By.CSS_SELECTOR, '.Footer-products-links')
    _footer_links_locator = (By.CSS_SELECTOR, '.Footer-links li a')

    def wait_for_page_to_load(self):
        self.wait.until(lambda _: self.find_element(*self._logo_locator).is_displayed())
        return self

    @property
    def page_logo(self):
        return self.find_element(*self._logo_locator)

    def footer_language_picker(self, value):
        select = Select(self.find_element(*self._footer_language_picker_locator))
        select.select_by_visible_text(value)

    @property
    def products_links(self):
        element = self.find_element(*self._footer_products_section_locator)
        return element.find_elements(*self._footer_links_locator)
