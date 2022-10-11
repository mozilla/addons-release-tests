from pypom import Region

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expected

from pages.desktop.base import Base


class Reviews(Base):
    _review_count_title_locator = (By.CLASS_NAME, 'AddonReviewList-reviewCount')
    _filter_by_score_locator = (By.CLASS_NAME, 'AddonReviewList-filterByScoreSelector')
    _user_review_permalink_locator = (By.CSS_SELECTOR, '.FeaturedAddonReview header')
    _addon_summary_card_locator = (By.CLASS_NAME, 'AddonSummaryCard')
    _featured_review_card_locator = (By.CSS_SELECTOR, '.FeaturedAddonReview-card')
    _reviews_list_locator = (By.CSS_SELECTOR, '.AddonReviewList-reviews-listing li')
    _editable_rating_stars_locator = (By.CSS_SELECTOR, '.Rating--editable button')
    _score_star_highlight_locator = (
        By.CSS_SELECTOR,
        '.Rating--editable .Rating-selected-star',
    )
    _rating_score_bars_locator = (By.CSS_SELECTOR, '.RatingsByStar-barContainer')
    _bar_rating_score_locator = (By.CSS_SELECTOR, '.RatingsByStar-star')

    def wait_for_page_to_load(self):
        """Waits for various page components to be loaded"""
        self.wait.until(
            expected.invisibility_of_element_located((By.CLASS_NAME, 'LoadingText')),
            message='All reviews page could not be loaded',
        )
        return self

    @property
    def reviews_page_title(self):
        return self.find_element(*self._review_count_title_locator).text

    @property
    def reviews_title_count(self):
        count = self.reviews_page_title
        review_count = count.split()[0].replace(' reviews', '')
        return int(review_count.replace(',', ''))

    @property
    def filter_by_score(self):
        return self.find_element(*self._filter_by_score_locator)

    @property
    def user_review_permalink(self):
        return self.find_element(*self._user_review_permalink_locator).text

    @property
    def addon_summary_card(self):
        return self.find_element(*self._addon_summary_card_locator)

    @property
    def edit_review_score(self):
        return self.find_elements(*self._editable_rating_stars_locator)

    @property
    def selected_score_highlight(self):
        return self.find_elements(*self._score_star_highlight_locator)

    @property
    def reviews_list(self):
        return self.find_elements(*self._reviews_list_locator)

    @property
    def score_bars(self):
        return self.find_elements(*self._rating_score_bars_locator)

    @property
    def bar_rating_score(self):
        return self.find_elements(*self._bar_rating_score_locator)

    @property
    def featured_review_section(self):
        el = self.find_element(*self._featured_review_card_locator)
        return self.FeaturedReview(self, el)

    class FeaturedReview(Region):
        _author_locator = (By.CSS_SELECTOR, '.AddonReviewCard-authorByLine')
        _body_locator = (By.CSS_SELECTOR, '.ShowMoreCard-contents > div')
        _rating_stars_locator = (By.CSS_SELECTOR, '.Rating--small')

        @property
        def author(self):
            return self.find_element(*self._author_locator)

        @property
        def body(self):
            return self.find_element(*self._body_locator)

        @property
        def rating_stars(self):
            return self.find_element(*self._rating_stars_locator)

    @property
    def review_items(self):
        items = self.find_elements(*self._reviews_list_locator)
        return [self.UserReview(self, el) for el in items]

    class UserReview(Region):
        _rating_stars_locator = (By.CSS_SELECTOR, '.Rating--small')
        _rating_user_locator = (By.CSS_SELECTOR, '.AddonReviewCard-authorByLine')
        _rating_permalink_locator = (By.CSS_SELECTOR, '.AddonReviewCard-authorByLine a')
        _selected_star_locator = (
            By.CSS_SELECTOR,
            '.UserReview-byLine .Rating-selected-star',
        )
        _review_body_locator = (By.CSS_SELECTOR, '.UserReview-body')
        _delete_confirm_locator = (
            By.CSS_SELECTOR,
            '.ConfirmationDialog-confirm-button',
        )
        _flag_review_button_locator = (By.CSS_SELECTOR, '.FlagReviewMenu-menu')
        _flag_review_menu_options = (By.CSS_SELECTOR, '.TooltipMenu-inner button')
        _flag_review_success_text = (By.CSS_SELECTOR, '.TooltipMenu-inner li')
        _flag_review_login_button = (
            By.CSS_SELECTOR,
            '.TooltipMenu-list .Button--micro',
        )
        _reply_to_review_locator = (By.CSS_SELECTOR, '.AddonReviewCard-allControls a')
        _review_reply_textarea_locator = (
            By.CSS_SELECTOR,
            '.DismissibleTextForm-textarea',
        )
        _publish_reply_button_locator = (By.CSS_SELECTOR, '.DismissibleTextForm-submit')
        _reply_text_locator = (
            By.CSS_SELECTOR,
            '.AddonReviewCard-reply .ShowMoreCard-contents > div',
        )
        _dev_reply_header_locator = (By.CSS_SELECTOR, '.UserReview-reply-header')

        @property
        def rating_stars(self):
            return self.find_element(*self._rating_stars_locator)

        @property
        def rating_user(self):
            return self.find_element(*self._rating_user_locator)

        @property
        def posting_date(self):
            return self.find_element(*self._rating_permalink_locator)

        @property
        def selected_star(self):
            return self.find_elements(*self._selected_star_locator)

        @property
        def review_body(self):
            return self.find_element(*self._review_body_locator).text

        def click_confirm_delete_button(self):
            self.find_element(*self._delete_confirm_locator).click()

        def click_flag_review(self):
            self.find_element(*self._flag_review_button_locator).click()
            self.wait.until(
                expected.visibility_of_element_located(
                    (By.CSS_SELECTOR, '.TooltipMenu-list')
                ),
                message='The flag review menu did not open',
            )

        @property
        def flag_review_option(self):
            return self.find_elements(*self._flag_review_menu_options)

        def select_flag_option(self, count):
            self.wait.until(
                expected.element_to_be_clickable(
                    (By.CSS_SELECTOR, '.TooltipMenu-list li:nth-of-type(1)')
                ),
                message='Flag menu options were not loaded',
            )
            # using JavaScriptExecutor to avoid ElementClickInterceptedException
            self.driver.execute_script(
                "arguments[0].click();", self.flag_review_option[count]
            )
            self.wait.until(
                expected.text_to_be_present_in_element(
                    self._flag_review_button_locator, 'Flagged'
                ),
                message='Flag review button state did not change',
            )

        @property
        def flag_review_success_text(self):
            return self.find_elements(*self._flag_review_success_text)

        @property
        def flag_review_login_button(self):
            self.wait.until(
                expected.element_to_be_clickable(self._flag_review_login_button),
                message='Login button in Flag review menu was not loaded',
            )
            return self.find_element(*self._flag_review_login_button)

        def click_reply_to_review(self):
            reply = self.wait.until(
                expected.element_to_be_clickable(self._reply_to_review_locator),
                message='Reply button was not loaded',
            )
            reply.click()
            self.wait.until(
                expected.element_to_be_clickable(self._review_reply_textarea_locator),
                message='Reply text area was not opened',
            )

        def reply_text_input(self, value):
            self.find_element(*self._review_reply_textarea_locator).send_keys(value)

        def clear_developer_reply_text_field(self):
            self.find_element(*self._review_reply_textarea_locator).clear()

        def publish_reply(self):
            self.find_element(*self._publish_reply_button_locator).click()
            self.wait.until(
                expected.visibility_of_element_located(self._dev_reply_header_locator),
                message='Developer reply section header was not displayed',
            )

        @property
        def posted_reply_text(self):
            return self.find_element(*self._reply_text_locator).text

        @property
        def dev_reply_header(self):
            return self.find_element(*self._dev_reply_header_locator)
