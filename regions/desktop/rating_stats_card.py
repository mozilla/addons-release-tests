from pypom import Region
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class RatingStats(Region):

    _addon_title_locator = (By.CSS_SELECTOR, '.AddonTitle > a')
    _addon_image_locator = (By.CSS_SELECTOR, '.AddonSummaryCard-header-icon-image')
    _addon_author_locator = (By.CSS_SELECTOR, '.AddonTitle-author > a')
    _addon_rating_locator = (By.CSS_SELECTOR, '.AddonSummaryCard-addonAverage')
    _number_of_reviews_locator = (By.CLASS_NAME, 'RatingsByStar-count')
    _rating_stars_locator = (By.CSS_SELECTOR, '.AddonSummaryCard .Rating-star')
    _filled_stars_locator = (By.CSS_SELECTOR, '.AddonSummaryCard .Rating-selected-star')
    _half_filled_stars_locator = (
        By.CSS_SELECTOR,
        '.AddonSummaryCard .Rating-half-star',
    )
    _rating_by_star_locator = (By.CSS_SELECTOR, '.RatingsByStar-graph > a')
    _rating_bars_locator = (By.CSS_SELECTOR, '.RatingsByStar-barFrame')

    @property
    def addon_title(self):
        self.wait.until(EC.visibility_of_element_located(self._addon_title_locator))
        return self.find_element(*self._addon_title_locator)

    def click_addon_title(self):
        self.wait.until(EC.element_to_be_clickable(self._addon_title_locator))
        self.find_element(*self._addon_title_locator).click()
        from pages.desktop.frontend.details import Detail

        return Detail(self.driver, self.page)

    @property
    def addon_image(self):
        self.wait.until(EC.visibility_of_element_located(self._addon_image_locator))
        return self.find_element(*self._addon_image_locator)

    def click_addon_image(self):
        self.wait.until(EC.element_to_be_clickable(self._addon_image_locator))
        self.find_element(*self._addon_image_locator).click()
        from pages.desktop.frontend.details import Detail

        return Detail(self.driver, self.page)

    @property
    def addon_author_names(self):
        return [i.text for i in self.find_elements(*self._addon_author_locator)]

    def click_author_name(self, index=0):
        self.wait.until(EC.element_to_be_clickable(self._addon_author_locator))
        self.find_elements(*self._addon_author_locator)[index].click()
        from pages.desktop.frontend.users import User

        return User(self.driver, self.page).view

    @property
    def rating_stars(self):
        self.wait.until(EC.visibility_of_element_located(self._rating_stars_locator))
        return self.find_elements(*self._rating_stars_locator)

    @property
    def rating(self):
        self.wait.until(EC.visibility_of_element_located(self._addon_rating_locator))
        rating = self.find_element(*self._addon_rating_locator).text.split()[0]
        return float(rating)

    @property
    def rating_bars(self):
        self.wait.until(EC.visibility_of_element_located(self._rating_bars_locator))
        return self.find_elements(*self._rating_bars_locator)

    def click_see_all_reviews_with_specific_stars(self, count):
        self.wait.until(EC.element_to_be_clickable(self._rating_by_star_locator))
        self.find_elements(*self._rating_by_star_locator)[count].click()
        from pages.desktop.frontend.reviews import Reviews

        return Reviews(self.driver, self.page)

    def number_of_reviews_with_specific_stars(self, count):
        self.wait.until(EC.visibility_of_element_located(self._number_of_reviews_locator))
        return int(self.find_elements(*self._number_of_reviews_locator)[count].text)

    @property
    def number_of_filled_stars(self):
        self.wait.until(EC.visibility_of_element_located(self._filled_stars_locator))
        return len(self.find_elements(*self._filled_stars_locator))

    @property
    def number_of_half_filled_stars(self):
        return len(self.find_elements(*self._half_filled_stars_locator))

    @property
    def number_of_unfilled_stars(self):
        return 5 - (self.number_of_filled_stars + self.number_of_half_filled_stars)
