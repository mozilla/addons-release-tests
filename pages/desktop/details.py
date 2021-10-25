from pypom import Region

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as expected

from pages.desktop.base import Base
from pages.desktop.reviews import Reviews
from pages.desktop.versions import Versions


class Detail(Base):
    _root_locator = (By.CLASS_NAME, 'Addon-extension')
    _addon_name_locator = (By.CLASS_NAME, 'AddonTitle')
    _compatible_locator = (By.CSS_SELECTOR, '.AddonCompatibilityError')
    _new_compatibility_banner_locator = (By.CLASS_NAME, 'GetFirefoxButton-callout-text')
    _get_firefox_button_locator = (By.CLASS_NAME, 'GetFirefoxButton-button')
    _install_button_locator = (By.CLASS_NAME, 'AMInstallButton-button')
    _install_button_state_locator = (By.CSS_SELECTOR, '.AMInstallButton a')
    _promoted_badge_locator = (By.CLASS_NAME, 'PromotedBadge-large')
    _promoted_badge_label_locator = (
        By.CSS_SELECTOR,
        '.PromotedBadge-large .PromotedBadge-label',
    )
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
            expected.invisibility_of_element_located((By.CLASS_NAME, 'LoadingText'))
        )
        return self

    @property
    def name(self):
        """The only valid locator for the addon name on AMO will return the name
        as 'Addon name by author(s) name'. This format makes it difficult to determine
        the exact addon name, especially when we want to use it in comparisons.
        The following method makes sure that we only return the addon name without authors"""
        el = self.find_element(*self._addon_name_locator).text
        name_value = el.split()
        # we want to remove all elements from the list starting from 'by', but its index varies
        get_index = name_value.index('by')
        # finally recreating the addon name without the authors
        final_name = name_value[0:get_index]
        return ' '.join(final_name)

    @property
    def is_compatible(self):
        return not self.is_element_displayed(*self._compatible_locator)

    @property
    def incompatibility_message(self):
        return self.find_element(*self._compatible_locator).text

    @property
    def compatibility_banner(self):
        return self.find_element(*self._new_compatibility_banner_locator)

    @property
    def get_firefox_button(self):
        return self.find_element(*self._get_firefox_button_locator)

    def install(self):
        self.find_element(*self._install_button_locator).click()

    @property
    def button_text(self):
        self.wait.until(
            expected.invisibility_of_element_located(
                (By.CLASS_NAME, 'AMInstallButton-loading-button')
            )
        )
        return self.find_element(*self._install_button_locator).text

    @property
    def button_state_disabled(self):
        # checking that an inactive install button has a 'disabled' attribute
        return self.find_element(*self._install_button_state_locator).get_attribute(
            'disabled'
        )

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
        self.wait.until(
            expected.visibility_of_element_located((By.CLASS_NAME, 'sumo-page-heading'))
        )

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
        self.wait.until(
            expected.visibility_of_element_located((By.CLASS_NAME, 'sumo-page-heading'))
        )

    @property
    def stats(self):
        return self.Stats(self)

    @property
    def contribute(self):
        return self.Contribute(self)

    @property
    def permissions(self):
        return self.Permissions(self)

    @property
    def more_info(self):
        return self.MoreInfo(self)

    @property
    def screenshots(self):
        return self.Screenshots(self)

    @property
    def release_notes(self):
        return self.ReleaseNotes(self)

    @property
    def same_author_addons(self):
        return self.AddonsByAuthor(self)

    @property
    def add_to_collection(self):
        return self.AddToCollection(self)

    @property
    def description(self):
        return self.AddonDescription(self)

    @property
    def recommendations(self):
        return self.AddonRecommendations(self)

    @property
    def ratings(self):
        return self.Ratings(self)

    @property
    def themes(self):
        return self.Theme(self)

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
        _permissions_list_locator = (
            By.CSS_SELECTOR,
            '.PermissionsCard-list--required li',
        )
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

    class MoreInfo(Region):
        _more_info_header_locator = (By.CSS_SELECTOR, '.AddonMoreInfo header')
        _support_links_locator = (By.CSS_SELECTOR, '.AddonMoreInfo-links a')
        _version_number_locator = (By.CLASS_NAME, 'AddonMoreInfo-version')
        _addon_size_locator = (By.CLASS_NAME, 'AddonMoreInfo-filesize')
        _last_updated_locator = (By.CLASS_NAME, 'AddonMoreInfo-last-updated')
        _addon_categories_locator = (
            By.CSS_SELECTOR,
            '.AddonMoreInfo-related-categories-list a',
        )
        _addon_license_locator = (By.CLASS_NAME, 'AddonMoreInfo-license-link')
        _privacy_policy_locator = (By.CLASS_NAME, 'AddonMoreInfo-privacy-policy-link')
        _eula_locator = (By.CLASS_NAME, 'AddonMoreInfo-eula')
        _all_versions_locator = (By.CLASS_NAME, 'AddonMoreInfo-version-history-link')
        _addon_tags_locator = (By.CSS_SELECTOR, '.AddonMoreInfo-tag-links-list a')

        @property
        def more_info_card_header(self):
            return self.find_element(*self._more_info_header_locator).text

        @property
        def addon_support_links(self):
            return self.find_elements(*self._support_links_locator)

        @property
        def addon_version_number(self):
            return self.find_element(*self._version_number_locator)

        @property
        def addon_size(self):
            return self.find_element(*self._addon_size_locator)

        @property
        def addon_last_update_date(self):
            return self.find_element(*self._last_updated_locator)

        @property
        def addon_categories(self):
            return self.find_elements(*self._addon_categories_locator)

        def addon_external_license(self):
            self.find_element(*self._addon_license_locator).click()
            # clicking on license should open a link outside of AMO
            self.wait.until(
                expected.invisibility_of_element_located(self._more_info_header_locator)
            )

        def addon_custom_license(self):
            self.find_element(*self._addon_license_locator).click()
            return self.License(self).wait_for_region_to_load()

        def addon_privacy_policy(self):
            self.find_element(*self._privacy_policy_locator).click()
            return self.License(self).wait_for_region_to_load()

        def addon_eula(self):
            self.find_element(*self._eula_locator).click()
            return self.License(self).wait_for_region_to_load()

        def addon_versions(self):
            self.find_element(*self._all_versions_locator).click()
            return Versions(self.selenium, self.page.base_url).wait_for_page_to_load()

        @property
        def addon_tags(self):
            return self.find_elements(*self._addon_tags_locator)

        class License(Region):
            _license_and_privacy_header_locator = (
                By.CSS_SELECTOR,
                '.AddonInfo-info header',
            )
            _license_and_privacy_text_locator = (By.CSS_SELECTOR, '.AddonInfo-info p')
            _addon_summary_card_locator = (By.CSS_SELECTOR, '.AddonSummaryCard')

            def wait_for_region_to_load(self):
                """Waits for various page components to be loaded"""
                self.wait.until(
                    expected.invisibility_of_element_located(
                        (By.CLASS_NAME, 'LoadingText')
                    )
                )
                return self

            @property
            def custom_licence_and_privacy_header(self):
                return self.find_element(*self._license_and_privacy_header_locator).text

            @property
            def custom_licence_and_privacy_text(self):
                return self.find_element(*self._license_and_privacy_text_locator)

            @property
            def custom_licence_and_privacy_summary_card(self):
                return self.find_element(*self._addon_summary_card_locator)

    class Screenshots(Region):
        _screenshot_thumbnail_locator = (By.CSS_SELECTOR, '.ScreenShots-list img')
        _screenshot_viewer_locator = (By.CSS_SELECTOR, '.pswp--open')
        _next_preview_locator = (By.CSS_SELECTOR, '.pswp__button--arrow--right')
        _previous_preview_locator = (By.CSS_SELECTOR, '.pswp__button--arrow--left')
        _image_view_close_button_locator = (
            By.CSS_SELECTOR,
            '.pswp--open .pswp__button--close',
        )
        _screenshot_counter_location = (By.CSS_SELECTOR, '.pswp__counter')

        @property
        def screenshot_preview(self):
            return self.find_elements(*self._screenshot_thumbnail_locator)

        @property
        def screenshot_viewer(self):
            return self.find_element(*self._screenshot_viewer_locator)

        def screenshot_full_view_displayed(self):
            self.wait.until(
                lambda _: self.is_element_displayed(*self._screenshot_viewer_locator)
            )
            return self

        def go_to_next_screenshot(self):
            self.find_element(*self._next_preview_locator).click()

        def go_to_previous_screenshot(self):
            self.find_element(*self._previous_preview_locator).click()

        def right_key_for_next_screenshot(self):
            self.find_element(*self._screenshot_viewer_locator).send_keys(
                Keys.ARROW_RIGHT
            )

        def left_key_for_previous_screenshot(self):
            self.find_element(*self._screenshot_viewer_locator).send_keys(
                Keys.ARROW_LEFT
            )

        @property
        def screenshot_counter(self):
            return self.find_element(*self._screenshot_counter_location).text

        def close_screenshot_view(self):
            self.find_element(*self._image_view_close_button_locator).click()
            self.wait.until(
                expected.invisibility_of_element_located(self.screenshot_viewer)
            )

        def esc_to_close_screenshot_viewer(self):
            self.find_element(*self._screenshot_viewer_locator).send_keys(Keys.ESCAPE)
            self.wait.until(
                expected.invisibility_of_element_located(self.screenshot_viewer)
            )

    class ReleaseNotes(Region):
        _release_notes_card_header_locator = (
            By.CSS_SELECTOR,
            '.AddonDescription-version-notes header',
        )
        _release_notes_content_locator = (
            By.CSS_SELECTOR,
            '.AddonDescription-version-notes .ShowMoreCard-contents',
        )

        @property
        def release_notes_header(self):
            return self.find_element(*self._release_notes_card_header_locator).text

        @property
        def release_notes_text(self):
            return self.find_element(*self._release_notes_content_locator)

    class AddonsByAuthor(Region):
        _addons_by_author_header_locator = (
            By.CSS_SELECTOR,
            '.AddonsByAuthorsCard header',
        )
        _addons_by_author_results_locator = (
            By.CSS_SELECTOR,
            '.AddonsByAuthorsCard .SearchResult',
        )
        _addons_by_author_results_item_locator = (
            By.CSS_SELECTOR,
            '.AddonsByAuthorsCard a',
        )

        @property
        def addons_by_author_header(self):
            return self.find_element(*self._addons_by_author_header_locator).text

        @property
        def addons_by_author_results_list(self):
            return self.find_elements(*self._addons_by_author_results_locator)

        @property
        def addons_by_author_results_items(self):
            return self.find_elements(*self._addons_by_author_results_item_locator)

    class AddToCollection(Region):
        _collection_card_header_locator = (
            By.CSS_SELECTOR,
            '.AddAddonToCollection header',
        )
        _collection_select_locator = (By.CLASS_NAME, 'AddAddonToCollection-select')
        _select_collections_list_locator = (
            By.CSS_SELECTOR,
            '.AddAddonToCollection optgroup option',
        )
        _add_to_collection_success_notice_locator = (
            By.CSS_SELECTOR,
            '.AddAddonToCollection-added .Notice-text',
        )
        _add_to_collection_error_notice_locator = (
            By.CSS_SELECTOR,
            '.Notice-error .Notice-text',
        )

        @property
        def collections_card_header(self):
            return self.find_element(*self._collection_card_header_locator).text

        @property
        def collections_select_field(self):
            return self.find_element(*self._collection_select_locator)

        @property
        def add_to_collections_list(self):
            return self.find_elements(*self._select_collections_list_locator)

        @property
        def add_to_collection_success_notice(self):
            self.wait.until(
                expected.visibility_of_element_located(
                    self._add_to_collection_success_notice_locator
                ),
                message='The Add to collection success message was not displayed',
            )
            return self.find_element(
                *self._add_to_collection_success_notice_locator
            ).text

        @property
        def add_to_collection_error_notice(self):
            self.wait.until(
                expected.visibility_of_element_located(
                    self._add_to_collection_error_notice_locator
                ),
                message='The Add to collection error message was not displayed',
            )
            return self.find_element(*self._add_to_collection_error_notice_locator).text

    class AddonDescription(Region):
        _description_header_locator = (By.CSS_SELECTOR, '.AddonDescription header')
        _description_text_locator = (By.CLASS_NAME, 'AddonDescription-contents')

        @property
        def addon_description_header(self):
            return self.find_element(*self._description_header_locator).text

        @property
        def addon_description_text(self):
            return self.find_element(*self._description_text_locator)

    class AddonRecommendations(Region):
        _addon_recommendations_root_locator = (By.CSS_SELECTOR, '.AddonRecommendations')
        _recommendations_card_header_locator = (
            By.CSS_SELECTOR,
            '.AddonRecommendations header',
        )
        _recommendations_card_results_locator = (
            By.CSS_SELECTOR,
            '.AddonRecommendations .SearchResult',
        )
        _recommendations_name_locator = (
            By.CSS_SELECTOR,
            '.AddonRecommendations .SearchResult-link',
        )

        @property
        def addon_recommendations_header(self):
            return self.find_element(*self._recommendations_card_header_locator).text

        @property
        def addons_recommendations_results_list(self):
            return self.find_elements(*self._recommendations_card_results_locator)

        @property
        def recommendations_results_item(self):
            return self.find_elements(*self._recommendations_name_locator)

    class Theme(Region):
        _theme_preview_locator = (By.CSS_SELECTOR, '.ThemeImage-image')
        _same_author_theme_previews_locator = (By.CSS_SELECTOR, '.SearchResult-icon')

        @property
        def theme_preview(self):
            return self.find_element(*self._theme_preview_locator)

        @property
        def more_themes_by_author_previews(self):
            # waiting for the element to be clickable to avoid 'element could not be scrolled into view' exception
            self.wait.until(
                expected.element_to_be_clickable(
                    self._same_author_theme_previews_locator
                )
            )
            return self.find_elements(*self._same_author_theme_previews_locator)

        @property
        def preview_source(self):
            return [
                item.get_attribute('src')
                for item in self.more_themes_by_author_previews
            ]

    class Ratings(Region):
        _ratings_card_header_locator = (By.CSS_SELECTOR, '.Addon-overall-rating header')
        _ratings_card_summary_locator = (By.CLASS_NAME, 'RatingManager-legend')
        _login_to_rate_button_locator = (
            By.CLASS_NAME,
            'RatingManager-log-in-to-rate-button',
        )
        _rating_stars_locator = (By.CSS_SELECTOR, '.RatingManager-UserRating button')
        _loaded_rating_stars_locator = (By.CSS_SELECTOR, '.Rating--loading')
        _highlighted_star_locator = (
            By.CSS_SELECTOR,
            '.RatingManager-UserRating .Rating-selected-star',
        )
        _delete_rating_link_locator = (By.CSS_SELECTOR, '.AddonReviewCard-delete')
        _delete_confirm_button_locator = (
            By.CSS_SELECTOR,
            '.ConfirmationDialog-confirm-button',
        )
        _write_review_button_locator = (
            By.CSS_SELECTOR,
            '.AddonReviewCard-writeReviewButton',
        )
        _review_textarea_locator = (By.CSS_SELECTOR, '.AddonReviewManager textarea')
        _cancel_review_write_locator = (
            By.CSS_SELECTOR,
            '.AddonReviewManager .DismissibleTextForm-dismiss',
        )
        _submit_review_button_locator = (
            By.CSS_SELECTOR,
            '.AddonReviewManager .DismissibleTextForm-submit',
        )
        _review_text_locator = (By.CSS_SELECTOR, '.UserReview-body')
        _edit_review_link_locator = (By.CSS_SELECTOR, '.AddonReviewCard-allControls a')
        _delete_review_link_locator = (By.CLASS_NAME, 'AddonReviewCard-delete')
        _keep_review_button_locator = (
            By.CSS_SELECTOR,
            '.ConfirmationDialog-cancel-button',
        )
        _review_permalink_locator = (By.CSS_SELECTOR, '.UserReview-byLine a')
        _report_abuse_button_locator = (By.CLASS_NAME, 'ReportAbuseButton-show-more')
        _all_reviews_link_locator = (By.CLASS_NAME, 'Addon-all-reviews-link')

        @property
        def ratings_card_header(self):
            return self.find_element(*self._ratings_card_header_locator).text

        @property
        def ratings_card_summary(self):
            return self.find_element(*self._ratings_card_summary_locator).text

        @property
        def rating_login_button(self):
            return self.find_element(*self._login_to_rate_button_locator)

        @property
        def rating_stars(self):
            # waits for the ratings stars to be fully loaded and editable
            self.wait.until(
                expected.invisibility_of_element_located(
                    self._loaded_rating_stars_locator
                )
            )
            return self.find_elements(*self._rating_stars_locator)

        @property
        def selected_star_highlight(self):
            # waits for the ratings stars to be fully loaded and editable
            self.wait.until(
                expected.invisibility_of_element_located(
                    self._loaded_rating_stars_locator
                )
            )
            return self.find_elements(*self._highlighted_star_locator)

        @property
        def delete_rating_link(self):
            # waits for the ratings stars to be fully loaded and editable
            self.wait.until(
                expected.invisibility_of_element_located(
                    self._loaded_rating_stars_locator
                )
            )
            return self.find_element(*self._delete_rating_link_locator)

        def click_delete_confirm_button(self):
            self.find_element(*self._delete_confirm_button_locator).click()
            self.wait.until(
                expected.invisibility_of_element_located(self._review_text_locator)
            )

        @property
        def write_a_review(self):
            return self.find_element(*self._write_review_button_locator)

        def wait_for_rating_form(self):
            self.wait.until(
                expected.element_to_be_clickable(self._write_review_button_locator)
            )

        def review_text_input(self, value):
            self.find_element(*self._review_textarea_locator).send_keys(value)

        @property
        def submit_review_button(self):
            return self.find_element(*self._submit_review_button_locator)

        def submit_review(self):
            self.find_element(*self._submit_review_button_locator).click()
            self.wait.until(
                expected.visibility_of_element_located(self._edit_review_link_locator)
            )

        @property
        def written_review(self):
            return self.find_element(*self._review_text_locator)

        @property
        def cancel_review(self):
            return self.find_element(*self._cancel_review_write_locator)

        @property
        def edit_review(self):
            # waits for the ratings stars to be fully loaded and editable
            self.wait.until(
                expected.invisibility_of_element_located(
                    self._loaded_rating_stars_locator
                )
            )
            return self.find_element(*self._edit_review_link_locator)

        @property
        def delete_review(self):
            # waits for the ratings stars to be fully loaded and editable
            self.wait.until(
                expected.invisibility_of_element_located(
                    self._loaded_rating_stars_locator
                )
            )
            return self.find_element(*self._delete_review_link_locator)

        @property
        def keep_review(self):
            return self.find_element(*self._keep_review_button_locator)

        @property
        def review_permalink(self):
            # waits for the ratings stars to be fully loaded and editable
            self.wait.until(
                expected.invisibility_of_element_located(
                    self._loaded_rating_stars_locator
                )
            )
            return self.find_element(*self._review_permalink_locator)

        def click_all_reviews_link(self):
            self.find_element(*self._all_reviews_link_locator).click()
            return Reviews(self.selenium, self.page.base_url).wait_for_page_to_load()

        @property
        def all_reviews_link_rating_count(self):
            count = self.find_element(*self._all_reviews_link_locator).text
            return int(count.split()[2])

        def click_report_abuse(self):
            self.find_element(*self._report_abuse_button_locator).click()
