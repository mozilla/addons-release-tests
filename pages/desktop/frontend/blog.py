from pypom import Region

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


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
            self.wait.until(EC.visibility_of_element_located(self._image_locator))
            return self.find_element(*self._image_locator)

        @property
        def title(self):
            self.wait.until(EC.visibility_of_element_located(self._image_locator))
            return self.find_element(*self._title_locator)

        @property
        def date(self):
            self.wait.until(EC.visibility_of_element_located(self._image_locator))
            return self.find_element(*self._date_locator)

        @property
        def intro_text(self):
            self.wait.until(EC.visibility_of_element_located(self._image_locator))
            return self.find_element(*self._intro_text_locator)

        @property
        def read_more_link(self):
            self.wait.until(EC.visibility_of_element_located(self._image_locator))
            return self.find_element(*self._read_more_link_locator)

        def click_read_more_link(self):
            self.wait.until(EC.element_to_be_clickable(self._image_locator))
            self.read_more_link.click()
            return ArticlePage(self.driver, self.page.base_url).wait_for_page_to_load()


class ArticlePage(Base):
    _header_logo_locator = (By.CLASS_NAME, 'header-logo')
    _article_title = (By.CLASS_NAME, 'header-title')
    _navigation_bar_locator = (By.CSS_SELECTOR, '.blogpost-breadcrumb ol li')
    _content_paragraphs_locator = (By.CSS_SELECTOR, '.blogpost-content-wrapper > p')
    _last_updated_date_locator = (By.CSS_SELECTOR, 'dd.updated')
    _previous_article_link_locator = (By.CSS_SELECTOR, '.blogpost-nav-prev a p')
    _next_article_link_locator = (By.CSS_SELECTOR, '.blogpost-nav-next a p')
    _author_info_section_locator = (By.CLASS_NAME, 'blogpost-meta')
    _static_addon_card_locator = (By.CLASS_NAME, 'StaticAddonCard')

    def wait_for_page_to_load(self):
        self.wait.until(
            EC.visibility_of_element_located(self._author_info_section_locator)
        )
        return self

    @property
    def header_logo(self):
        self.wait_for_element_to_be_displayed(self._header_logo_locator)
        return self.find_element(*self._header_logo_locator)

    @property
    def title(self):
        self.wait_for_element_to_be_displayed(self._article_title)
        return self.find_element(*self._article_title)

    @property
    def nav_bar_links(self):
        self.wait_for_element_to_be_displayed(self._navigation_bar_locator)
        return self.find_elements(*self._navigation_bar_locator)

    @property
    def content_paragraphs(self):
        self.wait_for_element_to_be_displayed(self._content_paragraphs_locator)
        return self.find_elements(*self._content_paragraphs_locator)

    @property
    def last_updated_date(self):
        self.wait_for_element_to_be_displayed(self._last_updated_date_locator)
        return self.find_element(*self._last_updated_date_locator)

    @property
    def next_article(self):
        self.wait_for_element_to_be_displayed(self._next_article_link_locator)
        return self.find_element(*self._next_article_link_locator)

    @property
    def previous_article(self):
        self.wait_for_element_to_be_displayed(self._previous_article_link_locator)
        return self.find_element(*self._previous_article_link_locator)

    @property
    def author(self):
        return self.Author(self, self.find_element(*self._author_info_section_locator))

    class Author(Region):
        _name_locator = (By.CSS_SELECTOR, 'dd.author')
        _picture_locator = (By.CSS_SELECTOR, '.author-avatar > img')
        _twitter_link_locator = (By.CLASS_NAME, 'share-twitter-link')
        _pocket_link_locator = (By.CLASS_NAME, 'share-pocket-link')

        @property
        def name(self):
            self.wait.until(EC.visibility_of_element_located(self._name_locator))
            return self.find_element(*self._name_locator)

        @property
        def picture(self):
            self.wait.until(EC.visibility_of_element_located(self._picture_locator))
            return self.find_element(*self._picture_locator)

        @property
        def twitter_link(self):
            self.wait.until(EC.visibility_of_element_located(self._twitter_link_locator))
            return self.find_element(*self._twitter_link_locator)

        @property
        def pocket_link(self):
            self.wait.until(EC.visibility_of_element_located(self._pocket_link_locator))
            return self.find_element(*self._pocket_link_locator)

    @property
    def addon_cards(self):
        return [
            self.AddonCard(self, el)
            for el in self.find_elements(*self._static_addon_card_locator)
        ]

    class AddonCard(Region):
        _title_locator = (By.CSS_SELECTOR, '.AddonTitle > a')
        _author_locator = (By.CSS_SELECTOR, '.AddonTitle-author > a')
        _summary_locator = (By.CLASS_NAME, 'StaticAddonCard-summary')
        _rating_locator = (By.CLASS_NAME, 'Rating')
        _users_number_locator = (By.CLASS_NAME, 'StaticAddonCard-metadata-adu')
        _add_to_firefox_button_locator = (By.CLASS_NAME, 'GetFirefoxButton-button')
        _recommended_badge_link_locator = (
            By.CLASS_NAME,
            'PromotedBadge-link--recommended',
        )

        @property
        def title(self):
            self.wait.until(EC.visibility_of_element_located(self._title_locator))
            return self.find_element(*self._title_locator)

        @property
        def author(self):
            self.wait.until(EC.visibility_of_element_located(self._author_locator))
            return self.find_element(*self._author_locator)

        @property
        def summary(self):
            self.wait.until(EC.visibility_of_element_located(self._summary_locator))
            return self.find_element(*self._summary_locator).text

        @property
        def rating(self):
            self.wait.until(EC.visibility_of_element_located(self._rating_locator))
            rating = self.find_element(*self._rating_locator).get_attribute('title')
            if 'There are no ratings yet' in rating:
                return 0
            return float(rating.split()[1])

        @property
        def users_number(self):
            self.wait.until(EC.visibility_of_element_located(self._users_number_locator))
            return int(
                self.find_element(*self._users_number_locator)
                .text.split('Users: ')[1]
                .replace(",", "")
            )

        @property
        def add_to_firefox_button(self):
            self.wait.until(EC.visibility_of_element_located(self._add_to_firefox_button_locator))
            return self.find_element(*self._add_to_firefox_button_locator)

        @property
        def is_recommended(self):
            try:
                assert self.find_element(
                    *self._recommended_badge_link_locator
                ).is_displayed()
                return True
            except NoSuchElementException:
                return False

        @property
        def recommended_link(self):
            self.wait.until(EC.visibility_of_element_located(self._recommended_badge_link_locator))
            return self.find_element(*self._recommended_badge_link_locator)
