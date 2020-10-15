from pypom import Page, Region
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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
            expected.invisibility_of_element_located(
                (By.CLASS_NAME, 'LoadingText')))
        return self

    def wait_for_contextcard_update(self, value):
        try:
            self.wait.until(
                expected.text_to_be_present_in_element(
                    (By.CLASS_NAME, 'SearchContextCard-header'), value))
        except NoSuchElementException:
            print('Search context card header was not loaded')

    @property
    def result_list(self):
        return self.SearchResultList(self)

    @property
    def filter_by_sort(self):
        return self.find_element(*self._search_filters_sort_locator)

    @property
    def filter_by_type(self):
        return self.find_element(*self._search_filters_type_locator)

    @property
    def filter_by_os(self):
        return self.find_element(*self._search_filters_os_locator)

    @property
    def filter_by_badging(self):
        return self.find_element(*self._search_filters_badging_locator)

    @property
    def recommended_filter(self) -> object:
        return self.find_element(*self._recommended_checkbox_locator)

    def next_page(self):
        self.find_element(*self._pagination_next_locator).click()

    def previous_page(self):
        self.find_element(*self._pagination_previous_locator).click()

    @property
    def page_number(self):
        self.wait.until(
            lambda _: self.is_element_displayed(*self._selected_page_locator)
        )
        return self.find_element(*self._selected_page_locator).text

    class SearchResultList(Region):
        _result_locator = (By.CLASS_NAME, 'SearchResult')
        _theme_locator = (By.CLASS_NAME, 'SearchResult--theme')
        _extension_locator = (By.CLASS_NAME, 'SearchResult-name')

        @property
        def extensions(self):
            items = self.find_elements(*self._result_locator)
            return [self.ResultListItems(self, el) for el in items]

        @property
        def themes(self):
            items = self.find_elements(*self._theme_locator)
            return [self.ResultListItems(self, el) for el in items]

        @property
        def extension(self):
            items = self.find_elements(*self._extension_locator)
            return [self.ResultListItems(self, el) for el in items]

        class ResultListItems(Region):
            _rating_locator = (By.CSS_SELECTOR, '.Rating--small')
            _search_item_name_locator = (By.CSS_SELECTOR,
                                         '.SearchResult-contents > h2')
            _promoted_badge_locator = (By.CSS_SELECTOR, '.PromotedBadge')
            _promoted_badge_label_locator = (By.CSS_SELECTOR, '.PromotedBadge-label')
            _users_locator = (By.CLASS_NAME, 'SearchResult-users-text')

            @property
            def name(self):
                return self.find_element(*self._search_item_name_locator).text

            def link(self):
                self.find_element(*self._search_item_name_locator).click()
                from pages.desktop.details import Detail
                detail_page = Detail(self.selenium, self.page.base_url)
                return detail_page.wait_for_page_to_load()

            @property
            def users(self):
                users = self.find_element(*self._users_locator).text
                return int(
                    users.split()[0].replace(',', '').replace('users', ''))

            @property
            def rating(self):
                """Returns the rating"""
                rating = self.find_element(
                    *self._rating_locator).get_property('title')
                return float(rating.split()[1])

            @property
            def promoted_badge(self):
                WebDriverWait(self.selenium, 10).until(
                    EC.visibility_of_element_located(
                        self._promoted_badge_locator),
                    message='Promoted badge was not found for these search results'
                    )
                return self

            @property
            def promoted_badge_label(self):
                return self.find_element(*self._promoted_badge_label_locator).text


