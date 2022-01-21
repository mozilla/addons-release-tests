from selenium.webdriver.common.by import By

from pages.desktop.base import Base


class ManageAddons(Base):

    _my_addons_page_logo = (By.CSS_SELECTOR, '.site-titles')
    _page_title_locator = (By.CSS_SELECTOR, '.hero > h1')

    @property
    def my_addons_page_logo(self):
        return self.find_element(*self._my_addons_page_logo)

    @property
    def my_addons_page_title(self):
        return self.find_element(*self._page_title_locator)
