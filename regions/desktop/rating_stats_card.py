from pypom import Region
from selenium.webdriver.common.by import By


class RatingStats(Region):

    _addon_title_locator = (By.CSS_SELECTOR, '.AddonTitle > a')
    _addon_image_locator = (By.CSS_SELECTOR, '.AddonSummaryCard-header-icon-image')
    _addon_author_locator = (By.CSS_SELECTOR, '.AddonTitle-author > a')
    _addon_rating_locator = (By.CSS_SELECTOR, '.AddonSummaryCard-addonAverage')
    _number_of_reviews_locator = (By.CLASS_NAME, 'RatingsByStar-count')
    _rating_stars_locator = (By.CSS_SELECTOR, '.Rating-star')
    _rating_by_star_locator = (By.CSS_SELECTOR, '.RatingsByStar-graph > a')

    @property
    def addon_title(self):
        return self.find_element(*self._addon_title_locator)

    def click_addon_title(self):
        self.find_element(*self._addon_title_locator).click()
        from pages.desktop.frontend.details import Detail

        return Detail(self.selenium, self.page)

    @property
    def addon_image(self):
        return self.find_element(*self._addon_image_locator)

    def click_addon_image(self):
        self.find_element(*self._addon_image_locator).click()
        from pages.desktop.frontend.details import Detail

        return Detail(self.selenium, self.page)

    @property
    def addon_author_names(self):
        return [i.text for i in self.find_elements(*self._addon_author_locator)]

    def click_author_name(self, index=0):
        self.find_elements(*self._addon_image_locator)[index].click()
        from pages.desktop.frontend.users import User

        return User(self.selenium, self.page).view

    @property
    def rating_stars(self):
        return self.find_element(*self._rating_stars_locator)

    @property
    def rating(self):
        rating = self.find_element(*self._addon_rating_locator).text.split()[0]
        return float(rating)

    def click_see_all_reviews_with_x_stars(self, x):
        self.find_elements(*self._rating_by_star_locator)[5 - x].click()
        from pages.desktop.frontend.reviews import Reviews

        return Reviews(self.selenium, self.page)

    def number_of_reviews_with_x_stars(self, x):
        return int(self.find_elements(*self._number_of_reviews_locator)[5 - x].text)

    @property
    def reviews_number(self):
        total = 0
        for i in range(1, 6):
            total += self.number_of_reviews_with_x_stars(i)
        return total
