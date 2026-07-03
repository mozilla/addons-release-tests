from pypom import Region

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


from pages.desktop.base import Base


class BlogHomepage(Base):
    URL_TEMPLATE = "blog/"

    _articles_locator = (By.CSS_SELECTOR, ".blog-entry")

    @property
    def articles(self):
        items = self.find_elements(*self._articles_locator)
        return [self.ArticlesList(self, el) for el in items]

    class ArticlesList(Region):
        _image_locator = (By.CSS_SELECTOR, ".blog-entry-featured-image > img")
        _image_link_locator = (By.CSS_SELECTOR, ".blog-entry-featured-image")
        _title_locator = (By.CLASS_NAME, "blog-entry-title")
        _date_locator = (By.CLASS_NAME, "blog-entry-date")
        _intro_text_locator = (By.CSS_SELECTOR, ".blog-entry-excerpt > p:nth-child(1)")
        _read_more_link_locator = (By.CSS_SELECTOR, ".blog-entry-read-more > a")

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
    _header_logo_locator = (By.CLASS_NAME, "header-logo")
    _article_title = (By.CLASS_NAME, "header-title")
    _navigation_bar_locator = (By.CSS_SELECTOR, ".blogpost-breadcrumb ol li")
    _content_paragraphs_locator = (By.CSS_SELECTOR, ".blogpost-content-wrapper > p")
    _last_updated_date_locator = (By.CSS_SELECTOR, "dd.updated")
    _previous_article_link_locator = (By.CSS_SELECTOR, ".blogpost-nav-prev a p")
    _next_article_link_locator = (By.CSS_SELECTOR, ".blogpost-nav-next a p")
    _author_info_section_locator = (By.CLASS_NAME, "blogpost-meta")
    _static_addon_card_locator = (By.CLASS_NAME, "StaticAddonCard")

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
        _name_locator = (By.CSS_SELECTOR, "dd.author")
        _picture_locator = (By.CSS_SELECTOR, ".author-avatar > img")
        _twitter_link_locator = (By.CLASS_NAME, "share-twitter-link")
        _pocket_link_locator = (By.CLASS_NAME, "share-pocket-link")

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
            self.wait.until(
                EC.visibility_of_element_located(self._twitter_link_locator)
            )
            return self.find_element(*self._twitter_link_locator)

        @property
        def pocket_link(self):
            self.wait.until(EC.visibility_of_element_located(self._pocket_link_locator))
            return self.find_element(*self._pocket_link_locator)

    @property
    def addon_cards(self):
        # blog articles are shared content across environments, so some of the
        # add-ons referenced by an article may not exist in a given environment
        # (e.g. on -dev). Those render as "StaticAddonCard--is-unavailable" with
        # no title/author/button, so we exclude them and only return the cards
        # that actually resolved to an available add-on.
        self.wait.until(
            EC.presence_of_all_elements_located(self._static_addon_card_locator)
        )

        def _cards_hydrated(_):
            # the "is-unavailable" state is applied during client-side
            # hydration, so wait until every card has settled into either an
            # unavailable state or a resolved one with a visible title before
            # deciding which cards to keep
            cards = self.find_elements(*self._static_addon_card_locator)
            for el in cards:
                if "StaticAddonCard--is-unavailable" in el.get_attribute("class"):
                    continue
                titles = el.find_elements(By.CSS_SELECTOR, ".AddonTitle > a")
                if not titles or not titles[0].is_displayed():
                    return False
            return bool(cards)

        self.wait.until(_cards_hydrated)
        return [
            self.AddonCard(self, el)
            for el in self.find_elements(*self._static_addon_card_locator)
            if "StaticAddonCard--is-unavailable" not in el.get_attribute("class")
        ]

    class AddonCard(Region):
        _title_locator = (By.CSS_SELECTOR, ".AddonTitle > a")
        _author_locator = (By.CSS_SELECTOR, ".AddonTitle-author > a")
        _summary_locator = (By.CLASS_NAME, "StaticAddonCard-summary")
        _rating_locator = (By.CSS_SELECTOR, '[data-testid="badge-star-full"] .Badge-content')
        _users_number_locator = (
            By.CSS_SELECTOR,
            '[data-testid="badge-user-fill"] .Badge-content',
        )
        _add_to_firefox_button_locator = (By.CLASS_NAME, "GetFirefoxButton-button")
        _recommended_badge_link_locator = (
            By.CSS_SELECTOR,
            '[data-testid="badge-recommended"] a.Badge-link',
        )

        # Note: these waits use the region-scoped `find_element` rather than
        # `EC.visibility_of_element_located`, which searches the whole document
        # via the driver and would lock onto the first matching element on the
        # page. On articles that contain unavailable (hidden) add-on cards, that
        # first match belongs to a hidden card, so the driver-scoped wait would
        # never see it become visible even for an available card region.
        def _wait_displayed(self, locator):
            self.wait.until(lambda _: self.find_element(*locator).is_displayed())
            return self.find_element(*locator)

        @property
        def title(self):
            return self._wait_displayed(self._title_locator)

        @property
        def author(self):
            return self._wait_displayed(self._author_locator)

        @property
        def summary(self):
            return self._wait_displayed(self._summary_locator).text

        @property
        def rating(self):
            # the star badge is only rendered when the add-on has at least one rating
            if not self.find_elements(*self._rating_locator):
                return 0
            # badge content looks like "4.9 (96 reviews)"
            return float(self._wait_displayed(self._rating_locator).text.split()[0])

        @property
        def users_number(self):
            # badge content looks like "10,148 Users", or "No Users" when the
            # add-on has no users yet
            count = (
                self._wait_displayed(self._users_number_locator)
                .text.split()[0]
                .replace(",", "")
            )
            return int(count) if count.isdigit() else 0

        @property
        def add_to_firefox_button(self):
            return self._wait_displayed(self._add_to_firefox_button_locator)

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
            self.wait.until(
                EC.visibility_of_element_located(self._recommended_badge_link_locator)
            )
            return self.find_element(*self._recommended_badge_link_locator)
