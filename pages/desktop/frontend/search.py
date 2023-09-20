from pypom import Page, Region

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Search(Page):
    _context_card_locator = (By.CLASS_NAME, 'SearchContextCard-header')
    _search_box_locator = (By.CLASS_NAME, 'AutoSearchInput-query')
    _submit_button_locator = (By.CLASS_NAME, 'AutoSearchInput-submit-button')
    _search_filters_sort_locator = (By.ID, 'SearchFilters-Sort')
    _search_filters_type_locator = (By.ID, 'SearchFilters-AddonType')
    _search_filters_os_locator = (By.ID, 'SearchFilters-OperatingSystem')
    _search_filters_badging_locator = (By.ID, 'SearchFilters-Badging')
    _recommended_checkbox_locator = (By.ID, 'SearchFilters-Recommended')
    _pagination_next_locator = (By.CSS_SELECTOR, '.Paginate-item--next')
    _pagination_previous_locator = (By.CLASS_NAME, 'Paginate-item--previous')
    _selected_page_locator = (By.CLASS_NAME, 'Paginate-page-number')

    def wait_for_page_to_load(self):
        self.wait.until(
            expected.invisibility_of_element_located((By.CLASS_NAME, 'LoadingText')),
            message='Search page could not be loaded',
        )
        return self

    def wait_for_contextcard_update(self, value):
        self.wait.until(
            expected.text_to_be_present_in_element(
                (By.CLASS_NAME, 'SearchContextCard-header'), value
            ),
            message=f'Expected search term "{value}" not found in "{self.find_element(*self._context_card_locator).text}"',
        )

    def search_results_list_loaded(self, count):
        """method used when we need to check that the search results list
        contains a certain number of items"""
        self.wait.until(
            lambda _: len(self.result_list.search_results) >= count,
            message=f'Expected search results to be {count} but the list returned {len(self.result_list.search_results)}',
        )

    @property
    def results_info(self):
        self.wait.until(EC.visibility_of_element_located(self._context_card_locator))
        return self.find_element(*self._context_card_locator)

    @property
    def result_list(self):
        return self.SearchResultList(self)

    @property
    def filter_by_sort(self):
        self.wait.until(EC.visibility_of_element_located(self._search_filters_sort_locator))
        return self.find_element(*self._search_filters_sort_locator)

    @property
    def filter_by_type(self):
        self.wait.until(EC.visibility_of_element_located(self._search_filters_type_locator))
        return self.find_element(*self._search_filters_type_locator)

    @property
    def filter_by_os(self):
        self.wait.until(EC.visibility_of_element_located(self._search_filters_os_locator))
        return self.find_element(*self._search_filters_os_locator)

    @property
    def filter_by_badging(self):
        self.wait.until(EC.visibility_of_element_located(self._search_filters_badging_locator))
        return self.find_element(*self._search_filters_badging_locator)

    @property
    def recommended_filter(self) -> object:
        self.wait.until(EC.visibility_of_element_located(self._recommended_checkbox_locator))
        return self.find_element(*self._recommended_checkbox_locator)

    def next_page(self):
        self.wait.until(EC.visibility_of_element_located(self._pagination_next_locator))
        self.find_element(*self._pagination_next_locator).click()

    def previous_page(self):
        self.wait.until(EC.element_to_be_clickable(self._pagination_previous_locator))
        self.find_element(*self._pagination_previous_locator).click()

    @property
    def page_number(self):
        self.wait.until(
            lambda _: self.is_element_displayed(*self._selected_page_locator),
            message='Pagination items were not loaded',
        )
        return self.find_element(*self._selected_page_locator).text

    class SearchResultList(Region):
        _result_locator = (By.CLASS_NAME, 'SearchResult')
        _result_link_locator = (By.CLASS_NAME, 'SearchResult-link')
        _theme_locator = (By.CLASS_NAME, 'SearchResult--theme')
        _extension_locator = (By.CLASS_NAME, 'SearchResult-name')

        @property
        def search_results(self):
            self.wait.until(EC.visibility_of_element_located(self._result_locator))
            items = self.find_elements(*self._result_locator)
            return [self.ResultListItems(self, el) for el in items]

        @property
        def themes(self):
            items = self.find_elements(*self._theme_locator)
            return [self.ResultListItems(self, el) for el in items]

        @property
        def extension(self):
            self.wait.until(EC.visibility_of_element_located(self._extension_locator))
            items = self.find_elements(*self._extension_locator)
            return [self.ResultListItems(self, el) for el in items]

        def click_search_result(self, count):
            self.wait.until(EC.element_to_be_clickable(self._result_link_locator))
            self.find_elements(*self._result_link_locator)[count].click()
            from pages.desktop.frontend.details import Detail

            return Detail(self.driver, self.page.base_url).wait_for_page_to_load()

        class ResultListItems(Region):
            _rating_locator = (By.CSS_SELECTOR, '.Rating--small')
            _search_item_name_locator = (By.CSS_SELECTOR, '.SearchResult-link')
            _promoted_badge_locator = (By.CSS_SELECTOR, '.PromotedBadge')
            _promoted_badge_label_locator = (By.CSS_SELECTOR, '.PromotedBadge-label')
            _users_locator = (By.CLASS_NAME, 'SearchResult-users')
            _users_number_locator = (By.CLASS_NAME, 'SearchResult-users-text')
            _icon_locator = (By.CLASS_NAME, 'SearchResult-icon')
            _rating_stars_locator = (By.CLASS_NAME, 'SearchResult-rating')
            _author_locator = (By.CLASS_NAME, 'SearchResult-author')
            _summary_locator = (By.CLASS_NAME, 'SearchResult-summary')

            @property
            def search_name(self):
                self.wait.until(EC.visibility_of_element_located(self._search_item_name_locator))
                return self.find_element(*self._search_item_name_locator)

            @property
            def name(self):
                self.wait.until(EC.visibility_of_element_located(self._search_item_name_locator))
                return self.find_element(*self._search_item_name_locator).text

            def link(self):
                self.wait.until(
                    EC.element_to_be_clickable(self._search_item_name_locator)
                )
                self.find_element(*self._search_item_name_locator).click()
                from pages.desktop.frontend.details import Detail

                detail_page = Detail(self.driver, self.page.page.base_url)
                return detail_page.wait_for_page_to_load()

            @property
            def users(self):
                self.wait.until(EC.visibility_of_element_located(self._users_number_locator))
                users = self.find_element(*self._users_number_locator).text
                return int(users.split()[0].replace(',', '').replace('users', ''))

            @property
            def rating(self):
                """Returns the rating"""
                self.wait.until(EC.visibility_of_element_located(self._rating_locator))
                rating = self.find_element(*self._rating_locator).get_property('title')
                return float(rating.split()[1])

            @property
            def search_result_icon(self):
                self.wait.until(EC.visibility_of_element_located(self._icon_locator))
                return self.find_element(*self._icon_locator)

            @property
            def search_result_rating_stars(self):
                self.wait.until(EC.visibility_of_element_located(self._rating_stars_locator))
                return self.find_element(*self._rating_stars_locator)

            @property
            def search_result_author(self):
                self.wait.until(EC.visibility_of_element_located(self._author_locator))
                return self.find_element(*self._author_locator)

            @property
            def search_result_users(self):
                self.wait.until(EC.visibility_of_element_located(self._users_locator))
                return self.find_element(*self._users_locator)

            @property
            def search_result_summary(self):
                self.wait.until(EC.visibility_of_element_located(self._summary_locator))
                return self.find_element(*self._summary_locator)

            @property
            def promoted_badge(self):
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(self._promoted_badge_locator),
                    message='Promoted badge was not found for these search results',
                )
                return self

            @property
            def promoted_badge_label(self):
                self.wait.until(EC.visibility_of_element_located(self._promoted_badge_label_locator))
                return self.find_element(*self._promoted_badge_label_locator).text
