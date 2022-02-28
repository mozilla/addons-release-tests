from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.base import Base


class LanguageTools(Base):
    URL_TEMPLATE = '/language-tools/'

    _language_tools_header_locator = (By.CLASS_NAME, 'Card-header-text')
    _langpacks_info_text_locator = (By.CSS_SELECTOR, '.Card-contents p:nth-child(2)')
    _dictionaries_info_text_locator = (By.CSS_SELECTOR, '.Card-contents p:nth-child(1)')
    _language_list_column_locator = (By.CSS_SELECTOR, '.pivoted:nth-child(1) strong')
    _langpacks_list_column_locator = (By.CSS_SELECTOR, '.pivoted:nth-child(2) a')
    _dictionaries_list_column_locator = (By.CSS_SELECTOR, '.pivoted:nth-child(3) a')

    def loaded(self):
        """Waits for various page components to be loaded"""
        self.wait.until(
            EC.invisibility_of_element_located((By.CLASS_NAME, 'LoadingText'))
        )
        return self

    @property
    def language_tools_header(self):
        return self.find_element(*self._language_tools_header_locator).text

    @property
    def language_packs_info_text(self):
        return self.find_element(*self._langpacks_info_text_locator).text

    @property
    def dictionaries_info_text(self):
        return self.find_element(*self._dictionaries_info_text_locator).text

    @property
    def supported_languages_list(self):
        return self.find_elements(*self._language_list_column_locator)

    @property
    def available_language_packs(self):
        return self.find_elements(*self._langpacks_list_column_locator)

    @property
    def available_dictionaries(self):
        return self.find_elements(*self._dictionaries_list_column_locator)
