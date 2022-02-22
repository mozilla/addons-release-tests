from pypom import Region
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from pages.desktop.base import Base


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

    @property
    def header_logo(self):
        return self.find_element(*self._header_logo_locator)

    @property
    def title(self):
        return self.find_element(*self._article_title)

    @property
    def nav_bar_links(self):
        return self.find_elements(*self._navigation_bar_locator)

    @property
    def content_paragraphs(self):
        return self.find_elements(*self._content_paragraphs_locator)

    @property
    def last_updated_date(self):
        return self.find_element(*self._last_updated_date_locator)

    @property
    def next_article(self):
        return self.find_element(*self._next_article_link_locator)

    @property
    def previous_article(self):
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
            return self.find_element(*self._name_locator)

        @property
        def picture(self):
            return self.find_element(*self._picture_locator)

        @property
        def twitter_link(self):
            return self.find_element(*self._twitter_link_locator)

        @property
        def pocket_link(self):
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
            return self.find_element(*self._title_locator)

        @property
        def author(self):
            return self.find_element(*self._author_locator)

        @property
        def summary(self):
            return self.find_element(*self._summary_locator).text

        @property
        def rating(self):
            return (
                self.find_element(*self._rating_locator)
                .get_attribute('title')
                .split()[1]
            )

        @property
        def users_number(self):
            return self.find_element(*self._users_number_locator).text.split('Users: ')[
                1
            ]

        @property
        def add_to_firefox_button(self):
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
            return self.find_element(*self._recommended_badge_link_locator)
