from selenium.webdriver.common.by import By
from pages.desktop.base import Base


class ContentReviewAddonPage(Base):
    URL_TEMPLATE = 'review/review-content'

    _addon_name_locator = (By.CSS_SELECTOR, '#addon-name > span:nth-child(2) > em')

    @property
    def addon_name(self):
        return self.find_element(*self._addon_name_locator)

    @staticmethod
    def open_content_review_addon_page(selenium, addon_string):
        return selenium.get(f"https://reviewers.addons.allizom.org/en-US/reviewers/review-content/{addon_string}")

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._addon_name_locator).is_displayed(),
            message="Content Review Page was not loaded",
        )
        return self
