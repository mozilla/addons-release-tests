from pypom import Region
from selenium.webdriver.common.by import By

from pages.desktop.base import Base


class BlogHomepage(Base):
    URL_TEMPLATE = 'blog/'

    _articles_locator = (By.CSS_SELECTOR, '.blog-entry')

    @property
    def articles(self):
        items = self.find_elements(*self._articles_locator)
        return [self.ArticlesList(self, el) for el in items]

    class ArticlesList(Region):

        _image_locator = (By.CSS_SELECTOR, '.blog-entry-featured-image > img')
        _image_link_locator = (By.CSS_SELECTOR, '.blog-entry-featured-image')
        _title_locator = (By.CLASS_NAME, 'blog-entry-title')
        _date_locator = (By.CLASS_NAME, 'blog-entry-date')
        _intro_text_locator = (By.CSS_SELECTOR, '.blog-entry-excerpt > p:nth-child(1)')
        _read_more_link_locator = (By.CSS_SELECTOR, '.blog-entry-read-more > a')

        @property
        def image(self):
            return self.find_element(*self._image_locator)

        @property
        def title(self):
            return self.find_element(*self._title_locator)

        @property
        def date(self):
            return self.find_element(*self._date_locator)

        @property
        def intro_text(self):
            return self.find_element(*self._intro_text_locator)

        @property
        def read_more_link(self):
            return self.find_element(*self._read_more_link_locator)
