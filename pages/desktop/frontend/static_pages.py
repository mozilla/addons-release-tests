from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.base import Base


class StaticPages(Base):
    """This class will store informative pages, such as 404 pages, server error pages
    and other pages that have only an informative scope"""

    _not_found_page_header_locator = (By.CLASS_NAME, 'Card-header-text')

    def wait_for_page_to_load(self):
        """Waits for various page components to be loaded"""
        self.wait.until(
            EC.invisibility_of_element_located((By.CLASS_NAME, 'LoadingText')),
            message="The requested page could not be loaded",
        )
        return self

    @property
    def not_found_page_header(self):
        return self.find_element(*self._not_found_page_header_locator).text
