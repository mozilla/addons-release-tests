from selenium.webdriver.support import expected_conditions as EC
from pages.desktop.base import Base
from selenium.webdriver.common.by import By


class RatingsAwaitingModeration(Base):
    URL_TEMPLATE = '/reviewers/queue/reviews'

    # Locators -------------------------------------------------
    _page_locator = (By.XPATH, "//li[@class='selected']//a[contains(text(),'Rating Reviews')]")
    _moderation_actions_keep_review_locator = (By.XPATH, "//label[contains(text(),'Keep review; remove flags')]")
    _moderation_actions_skip_for_now_locator = (By.XPATH, "//label[contains(text(),'Skip for now')]")
    _moderation_actions_delete_review_locator = (By.XPATH, "//label[contains(text(),'Delete review')]")
    _review_locator = (By.CSS_SELECTOR, "div.review-flagged")
    _process_reviews_top_locator = (By.XPATH, "//div[@class='review-saved']//button")
    _process_reviews_bottom_locator = (By.XPATH, "//div[@class='review-saved review-flagged']//button")

    # Interaction methods
    @property
    def page(self):
        return self.find_element(*self._page_locator)

    @property
    def moderation_actions_keep_review(self):
        return self.find_element(*self._moderation_actions_keep_review_locator)

    @property
    def moderation_actions_skip_for_now(self):
        return self.find_element(*self._moderation_actions_skip_for_now_locator)

    @property
    def moderation_actions_delete_review(self):
        return self.find_element(*self._moderation_actions_delete_review_locator)

    @property
    def review(self):
        return self.find_element(*self._review_locator)

    @property
    def process_reviews_top(self):
        return self.find_element(*self._process_reviews_top_locator)

    @property
    def process_reviews_bottom(self):
        return self.find_element(*self._process_reviews_bottom_locator)

    # Assert methods --------------------------------------------------------------
    def assert_process_reviews_buttons(self):
        self.wait.until(
            EC.element_to_be_clickable(self._process_reviews_top_locator)
        )
        self.wait.until(
            EC.element_to_be_clickable(self._process_reviews_bottom_locator)
        )
        assert 'Process Reviews' in self.process_reviews_top.text
        assert 'Process Reviews' in self.process_reviews_bottom.text

    def assert_moderation_actions_section_elements(self):
        assert self.moderation_actions_keep_review.is_displayed(), \
            "Moderation action 'Keep review' is not displayed"
        assert 'Keep review' in self.moderation_actions_keep_review.text
        assert self.moderation_actions_skip_for_now.is_displayed(), \
            "Moderation action 'Skip for now' is not displayed"
        assert 'Skip for now' in self.moderation_actions_skip_for_now.text
        assert self.moderation_actions_delete_review.is_displayed(), \
            "Moderation action 'Delete review' is not displayed"
        assert 'Delete review' in self.moderation_actions_delete_review.text

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._page_locator).is_displayed(),
            message="Ratings Awaiting Moderation was not loaded",
        )
        assert "Rating Reviews" in self.page.text
        return self
