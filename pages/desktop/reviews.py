from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expected

from pages.desktop.base import Base


class Reviews(Base):
    _review_count_title_locator = (By.CLASS_NAME, 'AddonReviewList-reviewCount')
    _filter_by_score_locator = (By.CLASS_NAME, 'AddonReviewList-filterByScoreSelector')

    def wait_for_page_to_load(self):
        """Waits for various page components to be loaded"""
        self.wait.until(
            expected.invisibility_of_element_located(
                (By.CLASS_NAME, 'LoadingText')))
        return self

    @property
    def reviews_page_title(self):
        return self.find_element(*self._review_count_title_locator).text

    @property
    def reviews_title_count(self):
        count = self.reviews_page_title
        return int(count.split()[0].replace(' reviews', ''))

    @property
    def filter_by_score(self):
        return self.find_element(*self._filter_by_score_locator)