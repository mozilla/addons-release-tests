from pypom import Region

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class Shelves(Region):

    _recommended_addons_locator = (By.CLASS_NAME, 'RecommendedAddons')
    _top_rated_locator = (By.CLASS_NAME, 'HighlyRatedAddons')
    _trending_addons_locator = (By.CLASS_NAME, 'TrendingAddons')

    @property
    def recommended_addons(self):
        self.wait.until(EC.visibility_of_element_located(self._recommended_addons_locator))
        el = self.find_element(*self._recommended_addons_locator)
        return self.ShelfList(self, el)

    @property
    def top_rated_addons(self):
        self.wait.until(EC.visibility_of_element_located(self._top_rated_locator))
        el = self.find_element(*self._top_rated_locator)
        return self.ShelfList(self, el)

    @property
    def trending_addons(self):
        self.wait.until(EC.visibility_of_element_located(self._trending_addons_locator))
        el = self.find_element(*self._trending_addons_locator)
        return self.ShelfList(self, el)

    class ShelfList(Region):
        _addon_item_locator = (By.CLASS_NAME, 'SearchResult')
        _promo_card_header_locator = (By.CLASS_NAME, 'Card-header')
        _browse_all_locator = (By.CSS_SELECTOR, '.Card-footer-link > a')

        @property
        def list(self):
            self.wait.until(EC.visibility_of_element_located(self._addon_item_locator))
            items = self.find_elements(*self._addon_item_locator)
            return [self.ShelfDetail(self.page, el) for el in items]

        @property
        def card_header(self):
            self.wait.until(EC.visibility_of_element_located(self._promo_card_header_locator))
            return self.find_element(*self._promo_card_header_locator).text

        def browse_all(self):
            self.wait.until(EC.element_to_be_clickable(self._browse_all_locator))
            self.find_element(*self._browse_all_locator).click()
            from pages.desktop.frontend.search import Search

            search = Search(self.driver, self.page)
            return search.wait_for_page_to_load()

        class ShelfDetail(Region):
            _addon_name_locator = (By.CLASS_NAME, 'SearchResult-name')
            _addon_icon_locator = (By.CLASS_NAME, 'SearchResult-icon')
            _addon_users_locator = (By.CSS_SELECTOR, 'span[class="SearchResult-users-text"]')

            # Note: these wait on the region-scoped element being displayed
            # rather than EC.visibility_of_element_located, which is driver
            # scoped and waits for the first matching element anywhere on the
            # page. With several shelf items sharing the same classes, that
            # global wait can return while a later item's element is not yet
            # visible, making is_displayed() flakily return False.
            def _wait_displayed(self, locator):
                self.wait.until(lambda _: self.find_element(*locator).is_displayed())
                return self.find_element(*locator)

            @property
            def name(self):
                return self._wait_displayed(self._addon_name_locator).text

            @property
            def addon_icon_preview(self):
                return self._wait_displayed(self._addon_icon_locator)

            @property
            def addon_users_preview(self):
                return self._wait_displayed(self._addon_users_locator)
