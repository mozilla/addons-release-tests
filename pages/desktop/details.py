from pypom import Region

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expected

from pages.desktop.base import Base
from pages.desktop.reviews import Reviews


class Detail(Base):
    _root_locator = (By.CLASS_NAME, 'Addon-extension')
    _addon_name_locator = (By.CLASS_NAME, 'AddonTitle')
    _compatible_locator = (By.CSS_SELECTOR, '.AddonCompatibilityError')
    _install_button_locator = (By.CLASS_NAME, 'AMInstallButton-button')
    _install_button_state_locator = (By.CSS_SELECTOR, '.AMInstallButton a')
    _promoted_badge_locator = (By.CLASS_NAME, 'PromotedBadge-large')
    _promoted_badge_label_locator = (By.CSS_SELECTOR, '.PromotedBadge-large .PromotedBadge-label')
    _experimental_badge_locator = (By.CLASS_NAME, 'Badge-experimental')
    _addon_icon_locator = (By.CLASS_NAME, 'Addon-icon-image')
    _addon_author_locator = (By.CSS_SELECTOR, '.AddonTitle-author a')
    _summary_locator = (By.CLASS_NAME, 'Addon-summary')
    _install_warning_locator = (By.CLASS_NAME, 'InstallWarning')
    _install_warning_text_locator = (By.CSS_SELECTOR, '.InstallWarning p')
    _install_warning_button_locator = (By.CSS_SELECTOR, '.InstallWarning a')

    def wait_for_page_to_load(self):
        """Waits for various page components to be loaded"""
        self.wait.until(
            expected.invisibility_of_element_located(
                (By.CLASS_NAME, 'LoadingText')))
        return self

    @property
    def name(self):
        return self.find_element(*self._addon_name_locator).text

    @property
    def is_compatible(self):
        return not self.is_element_displayed(*self._compatible_locator)

    @property
    def incompatibility_message(self):
        return self.find_element(*self._compatible_locator).text

    def install(self):
        self.find_element(*self._install_button_locator).click()

    @property
    def button_text(self):
        self.wait.until(expected.invisibility_of_element_located(
            (By.CLASS_NAME, 'AMInstallButton-loading-button')))
        return self.find_element(*self._install_button_locator).text

    @property
    def button_state_disabled(self):
        # checking that an inactive install button has a 'disabled' attribute
        return self.find_element(*self._install_button_state_locator).\
            get_attribute('disabled')

    @property
    def promoted_badge(self):
        return self.find_element(*self._promoted_badge_locator)

    @property
    def promoted_badge_category(self):
        return self.find_element(*self._promoted_badge_label_locator).text

    def click_promoted_badge(self):
        # clicks on the promoted badge and waits for the sumo page to load
        self.promoted_badge.click()
        self.wait.until(expected.number_of_windows_to_be(2))
        new_tab = self.selenium.window_handles[1]
        self.selenium.switch_to_window(new_tab)
        self.wait.until(expected.visibility_of_element_located(
            (By.CLASS_NAME, 'sumo-page-heading')))

    @property
    def experimental_badge(self):
        return self.find_element(*self._experimental_badge_locator)

    @property
    def addon_icon(self):
        return self.find_element(*self._addon_icon_locator)

    @property
    def authors(self):
        return self.find_element(*self._addon_author_locator)

    @property
    def summary(self):
        return self.find_element(*self._summary_locator)

    @property
    def install_warning(self):
        return self.find_element(*self._install_warning_locator)

    @property
    def install_warning_message(self):
        return self.find_element(*self._install_warning_text_locator).text

    def click_install_warning_button(self):
        # clicks on the install warning and waits for the sumo page to load
        self.find_element(*self._install_warning_button_locator).click()
        self.wait.until(expected.number_of_windows_to_be(2))
        new_tab = self.selenium.window_handles[1]
        self.selenium.switch_to_window(new_tab)
        self.wait.until(expected.visibility_of_element_located(
            (By.CLASS_NAME, 'sumo-page-heading')))

    @property
    def stats(self):
        return self.Stats(self)

    @property
    def contribute(self):
        return self.Contribute(self)

    @property
    def permissions(self):
        return self.Permissions(self)

    class Stats(Region):
        _root_locator = (By.CLASS_NAME, 'AddonMeta')
        _stats_users_locator = (By.CSS_SELECTOR, '.AddonMeta dl:nth-child(1)')
        _stats_reviews_locator = (By.CSS_SELECTOR, '.AddonMeta dl:nth-child(2)')
        _stats_ratings_locator = (By.CSS_SELECTOR, '.AddonMeta dl:nth-child(3)')
        _grouped_ratings_locator = (By.CSS_SELECTOR, '.RatingsByStar-star a')
        _rating_bar_locator = (By.CSS_SELECTOR, '.RatingsByStar-barContainer')
        _rating_bar_count_locator = (By.CSS_SELECTOR, '.RatingsByStar-count a')

        @property
        def addon_user_stats(self):
            return self.find_element(*self._stats_users_locator)

        @property
        def stats_users_count(self):
            count = self.addon_user_stats.find_element(By.CSS_SELECTOR, 'dd').text
            return int(count.split()[0].replace(',', ''))

        @property
        def no_user_stats(self):
            return self.addon_user_stats.find_element(By.CSS_SELECTOR, 'dt').text

        @property
        def addon_reviews_stats(self):
            return self.find_element(*self._stats_reviews_locator)

        @property
        def stats_reviews_count(self):
            count = self.addon_reviews_stats
            return int(count.find_element(By.CSS_SELECTOR, 'dd').text)

        def stats_reviews_link(self):
            self.addon_reviews_stats.find_element(By.CSS_SELECTOR, 'dt a').click()
            return Reviews(self.selenium, self.page.base_url).wait_for_page_to_load()

        @property
        def no_reviews_stats(self):
            return self.addon_reviews_stats.find_element(By.CSS_SELECTOR, 'dt').text

        @property
        def addon_star_rating_stats(self):
            return self.find_element(*self._stats_ratings_locator)

        @property
        def no_star_ratings(self):
            return self.addon_star_rating_stats.find_element(By.CSS_SELECTOR, 'dt').text

        @property
        def bar_grouped_ratings(self):
            return self.find_elements(*self._grouped_ratings_locator)

        @property
        def rating_bars(self):
            return self.find_elements(*self._rating_bar_locator)

        @property
        def bar_rating_counts(self):
            return self.find_elements(*self._rating_bar_count_locator)

    class Contribute(Region):
        _contribute_header_locator = (By.CSS_SELECTOR, '.ContributeCard header')
        _contribute_content_locator = (By.CLASS_NAME, 'ContributeCard-content')
        _contribute_button_locator = (By.CLASS_NAME, 'ContributeCard-button')

        @property
        def contribute_card_header(self):
            return self.find_element(*self._contribute_header_locator).text

        @property
        def contribute_card_content(self):
            return self.find_element(*self._contribute_content_locator).text

        def click_contribute_button(self):
            self.find_element(*self._contribute_button_locator).click()
            self.wait.until(expected.number_of_windows_to_be(2))
            new_tab = self.selenium.window_handles[1]
            self.selenium.switch_to_window(new_tab)

    class Permissions(Region):
        _permissions_header_locator = (By.CSS_SELECTOR, '.PermissionsCard header')
        _permissions_list_locator = (By.CSS_SELECTOR, '.PermissionsCard-list--required li')
        _permissions_learn_more_locator = (By.CLASS_NAME, 'PermissionsCard-learn-more')

        @property
        def permissions_card_header(self):
            return self.find_element(*self._permissions_header_locator).text

        @property
        def permissions_list(self):
            items = self.find_elements(*self._permissions_list_locator)
            return [self.PermissionDetails(self.page, el) for el in items]

        def click_permissions_button(self):
            self.find_element(*self._permissions_learn_more_locator).click()
            self.wait.until(expected.number_of_windows_to_be(2))
            new_tab = self.selenium.window_handles[1]
            self.selenium.switch_to_window(new_tab)

        class PermissionDetails(Region):
            _permission_icon_locator = (By.CSS_SELECTOR, '.Permission .Icon')
            _permission_description_locator = (By.CLASS_NAME, 'Permission-description')

            @property
            def permission_icon(self):
                return self.find_element(*self._permission_icon_locator)

            @property
            def permission_description(self):
                return self.find_element(*self._permission_description_locator)
