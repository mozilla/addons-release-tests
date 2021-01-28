from selenium.webdriver.common.by import By
from pages.desktop.base import Base
from regions.desktop.categories import Categories
from regions.desktop.shelves import Shelves


class Extensions(Base):
    URL_TEMPLATE = 'extensions/'

    _title_locator = (By.CLASS_NAME, 'LandingPage-addonType-name')
    _header_summary_locator = (By.CSS_SELECTOR, '.LandingPage-header p')

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.is_element_displayed(*self._title_locator))
        return self

    @property
    def title(self):
        return self.find_element(*self._title_locator).text

    @property
    def header_summary(self):
        return self.find_element(*self._header_summary_locator).text

    @property
    def categories(self):
        return Categories(self)

    @property
    def shelves(self):
        return Shelves(self)
