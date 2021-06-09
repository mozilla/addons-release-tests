from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expected

from pages.desktop.base import Base


class Versions(Base):
    _versions_page_header_locator = (By.CSS_SELECTOR, '.AddonVersions-versions header')
    _latest_version_locator = (By.CSS_SELECTOR, '.Card-contents li:nth-child(2) h2')

    def wait_for_page_to_load(self):
        """Waits for various page components to be loaded"""
        self.wait.until(
            expected.invisibility_of_element_located((By.CLASS_NAME, 'LoadingText'))
        )
        return self

    @property
    def versions_page_header(self):
        return self.find_element(*self._versions_page_header_locator)

    @property
    def latest_version_number(self):
        el = self.find_element(*self._latest_version_locator).text
        return el.split()[1].replace('Version ', '')
