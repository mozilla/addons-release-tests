from pypom import Region

from selenium.webdriver.common.by import By


class Categories(Region):

    _root_locator = (By.CLASS_NAME, 'Categories')
    _categories_locator = (By.CLASS_NAME, 'Categories-item')
    _card_header_locator = (By.CLASS_NAME, 'Card-header-text')

    def wait_for_categories_to_load(self):
        self.wait.until(lambda _: self.is_element_displayed(*self._categories_locator))
        return self

    @property
    def card_header(self):
        return self.find_element(*self._card_header_locator).text

    @property
    def category_list(self):
        items = self.find_elements(*self._categories_locator)
        return [self.CategoryList(self, el) for el in items]

    class CategoryList(Region):
        _name_locator = (By.CLASS_NAME, 'Categories-link')

        @property
        def name(self):
            return self.find_element(*self._name_locator).text

        def click(self):
            self.root.click()
            from pages.desktop.frontend.search import Search

            return Search(self.driver, self.page)
