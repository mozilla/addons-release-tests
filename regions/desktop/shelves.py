from pypom import Region

from selenium.webdriver.common.by import By


class Shelves(Region):

    _recommended_addons_locator = (By.CLASS_NAME, 'RecommendedAddons')
    _top_rated_locator = (By.CLASS_NAME, 'HighlyRatedAddons')
    _trending_addons_locator = (By.CLASS_NAME, 'TrendingAddons')

    @property
    def recommended_addons(self):
        el = self.find_element(*self._recommended_addons_locator)
        return self.ShelfList(self, el)

    @property
    def top_rated_addons(self):
        el = self.find_element(*self._top_rated_locator)
        return self.ShelfList(self, el)

    @property
    def trending_addons(self):
        el = self.find_element(*self._trending_addons_locator)
        return self.ShelfList(self, el)

    class ShelfList(Region):
        _addon_item_locator = (By.CLASS_NAME, 'SearchResult')
        _promo_card_header_locator = (By.CLASS_NAME, 'Card-header')
        _browse_all_locator = (By.CSS_SELECTOR, '.Card-footer-link > a')

        @property
        def list(self):
            items = self.find_elements(*self._addon_item_locator)
            return [self.ShelfDetail(self.page, el) for el in items]

        @property
        def card_header(self):
            return self.find_element(*self._promo_card_header_locator).text

        def browse_all(self):
            self.find_element(*self._browse_all_locator).click()
            from pages.desktop.search import Search
            search = Search(self.selenium, self.page)
            return search.wait_for_page_to_load()

        class ShelfDetail(Region):
            _addon_name_locator = (By.CLASS_NAME, 'SearchResult-name')
            _addon_icon_locator = (By.CLASS_NAME, 'SearchResult-icon')
            _addon_users_locator = (By.CLASS_NAME, 'SearchResult-users-text')

            @property
            def name(self):
                return self.find_element(*self._addon_name_locator).text

            @property
            def addon_icon_preview(self):
                return self.find_element(*self._addon_icon_locator)

            @property
            def addon_users_preview(self):
                return self.find_element(*self._addon_users_locator)
