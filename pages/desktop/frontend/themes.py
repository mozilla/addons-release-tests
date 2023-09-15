from selenium.webdriver.common.by import By

from pages.desktop.base import Base
from regions.desktop.categories import Categories
from regions.desktop.shelves import Shelves
from selenium.webdriver.support import expected_conditions as EC


class Themes(Base):
    URL_TEMPLATE = 'themes/'

    _title_locator = (By.CLASS_NAME, 'LandingPage-addonType-name')
    _header_summary_locator = (By.CSS_SELECTOR, '.LandingPage-header p')

    def wait_for_page_to_load(self):
        self.wait.until(lambda _: self.is_element_displayed(*self._title_locator))
        return self.find_element(*self._title_locator)

    @property
    def title(self):
        self.wait.until(EC.visibility_of_element_located(self._title_locator))
        return self.find_element(*self._title_locator).text

    @property
    def header_summary(self):
        self.wait.until(EC.visibility_of_element_located(self._header_summary_locator))
        return self.find_element(*self._header_summary_locator).text

    @property
    def categories(self):
        return Categories(self)

    @property
    def shelves(self):
        return Shelves(self)
