import os
from pathlib import Path

from pypom import Region
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.base import Base
from pages.desktop.frontend.home import Home
from pages.desktop.frontend.reviews import Reviews
from pages.desktop.frontend.search import Search


class User(Base):
    URL_TEMPLATE = '/users/edit'

    _display_name_locator = (By.CLASS_NAME, 'UserProfile-name')

    def wait_for_page_to_load(self):
        """Waits for various page components to be loaded"""
        self.wait.until(
            EC.invisibility_of_element_located((By.CLASS_NAME, 'LoadingText'))
        )
        return self

    def wait_for_user_to_load(self):
        WebDriverWait(
            self.driver, 20, ignored_exceptions=StaleElementReferenceException
        ).until(lambda _: self.is_element_displayed(*self._display_name_locator))
        return self

    @property
    def user_display_name(self):
        self.wait.until(EC.visibility_of_element_located(self._display_name_locator))
        return self.find_element(*self._display_name_locator)

    @property
    def view(self):
        return self.ViewProfile(self)

    @property
    def edit(self):
        return self.EditProfile(self)

    class ViewProfile(Region):
        _user_icon_placeholder_locator = (By.CSS_SELECTOR, '.Icon-anonymous-user')
        _user_profile_image_locator = (By.CSS_SELECTOR, '.UserAvatar-image')
        _user_developer_role_locator = (By.CSS_SELECTOR, '.UserProfile-developer')
        _user_developer_role_icon_locator = (By.CSS_SELECTOR, '.Icon-developer')
        _user_artist_role_locator = (By.CSS_SELECTOR, '.UserProfile-artist')
        _user_artist_role_icon_locator = (By.CSS_SELECTOR, '.Icon-artist')
        _user_homepage_locator = (By.CSS_SELECTOR, '.UserProfile-homepage a')
        _user_location_locator = (By.CSS_SELECTOR, '.UserProfile-location')
        _user_occupation_locator = (By.CSS_SELECTOR, '.UserProfile-occupation')
        _user_creation_date_locator = (By.CSS_SELECTOR, '.UserProfile-user-since')
        _user_addons_count_locator = (By.CSS_SELECTOR, '.UserProfile-number-of-addons')
        _user_addon_average_rating_locator = (
            By.CSS_SELECTOR,
            '.UserProfile-rating-average',
        )
        _user_biography_locator = (By.CSS_SELECTOR, '.UserProfile-biography')
        _user_profile_edit_link_locator = (By.CSS_SELECTOR, '.UserProfile-edit-link')
        _user_extensions_card_locator = (By.CSS_SELECTOR, '.AddonsCard--vertical')
        _user_extensions_card_header_locator = (
            By.CSS_SELECTOR,
            '.AddonsCard--vertical .Card-header-text',
        )
        _user_extensions_results_locator = (
            By.CSS_SELECTOR,
            '.AddonsCard--vertical .SearchResult',
        )
        _user_themes_card_locator = (By.CSS_SELECTOR, '.AddonsByAuthorsCard--theme')
        _user_themes_card_header_locator = (
            By.CSS_SELECTOR,
            '.AddonsByAuthorsCard--theme .Card-header-text',
        )
        _user_themes_results_locator = (By.CLASS_NAME, 'SearchResult--theme')
        _user_reviews_card_locator = (By.CSS_SELECTOR, '.UserProfile-reviews')
        _extensions_pagination_locator = (
            By.CSS_SELECTOR,
            '.AddonsCard--vertical .Paginate',
        )
        _extensions_next_page_locator = (
            By.CSS_SELECTOR,
            '.AddonsCard--vertical .Paginate-item--next',
        )
        _extensions_page_number_locator = (
            By.CSS_SELECTOR,
            '.AddonsCard--vertical .Paginate-page-number',
        )
        _themes_pagination_locator = (
            By.CSS_SELECTOR,
            '.AddonsByAuthorsCard--theme .Paginate',
        )
        _themes_next_page_locator = (
            By.CSS_SELECTOR,
            '.AddonsByAuthorsCard--theme .Paginate-item--next',
        )
        _themes_page_number_locator = (
            By.CSS_SELECTOR,
            '.AddonsByAuthorsCard--theme .Paginate-page-number',
        )
        _user_review_list_locator = (By.CSS_SELECTOR, '.AddonReviewCard-viewOnly')
        _user_abuse_report_button_locator = (
            By.CSS_SELECTOR,
            '.ReportUserAbuse-show-more',
        )
        _abuse_report_form_header_locator = (By.CSS_SELECTOR, '.ReportUserAbuse-header')
        _abuse_report_form_help_text = (
            By.CSS_SELECTOR,
            '.ReportUserAbuse-form p:nth-child(2)',
        )
        _abuse_report_form_additional_help_text = (
            By.CSS_SELECTOR,
            '.ReportUserAbuse-form p:nth-child(3)',
        )
        _abuse_report_textarea_locator = (
            By.CSS_SELECTOR,
            '.DismissibleTextForm-textarea',
        )
        _abuse_report_cancel_button_locator = (
            By.CSS_SELECTOR,
            '.DismissibleTextForm-dismiss',
        )
        _abuse_report_submit_disabled_button_locator = (
            By.CSS_SELECTOR,
            '.DismissibleTextForm-submit.Button--disabled',
        )
        _abuse_report_submit_button_locator = (
            By.CSS_SELECTOR,
            '.DismissibleTextForm-submit',
        )
        _abuse_report_confirm_message_locator = (
            By.CSS_SELECTOR,
            '.ReportUserAbuse--report-sent p:nth-child(2)',
        )

        @property
        def user_profile_icon_placeholder(self):
            self.wait.until(EC.visibility_of_element_located(self._user_icon_placeholder_locator))
            return self.find_element(*self._user_icon_placeholder_locator)

        @property
        def user_profile_icon(self):
            self.wait.until(EC.visibility_of_element_located(self._user_profile_image_locator))
            return self.find_element(*self._user_profile_image_locator)

        @property
        def icon_source(self):
            self.wait.until(
                EC.visibility_of_element_located(self._user_profile_image_locator)
            )
            return self.user_profile_icon.get_attribute('src')

        @property
        def developer_role(self):
            self.wait.until(EC.visibility_of_element_located(self._user_developer_role_locator))
            return self.find_element(*self._user_developer_role_locator)

        @property
        def developer_role_icon(self):
            self.wait.until(EC.visibility_of_element_located(self._user_developer_role_icon_locator))
            return self.find_element(*self._user_developer_role_icon_locator)

        @property
        def artist_role(self):
            self.wait.until(EC.visibility_of_element_located(self._user_artist_role_locator))
            return self.find_element(*self._user_artist_role_locator)

        @property
        def artist_role_icon(self):
            self.wait.until(EC.visibility_of_element_located(self._user_artist_role_icon_locator))
            return self.find_element(*self._user_artist_role_icon_locator)

        @property
        def user_homepage(self):
            self.wait.until(EC.visibility_of_element_located(self._user_homepage_locator))
            return self.find_element(*self._user_homepage_locator).get_attribute('href')

        @property
        def user_location(self):
            self.wait.until(EC.visibility_of_element_located(self._user_location_locator))
            return self.find_element(*self._user_location_locator).text

        @property
        def user_occupation(self):
            self.wait.until(EC.visibility_of_element_located(self._user_occupation_locator))
            return self.find_element(*self._user_occupation_locator).text

        @property
        def user_profile_creation_date(self):
            self.wait.until(EC.visibility_of_element_located(self._user_creation_date_locator))
            return self.find_element(*self._user_creation_date_locator)

        @property
        def user_addons_number(self):
            self.wait.until(EC.visibility_of_element_located(self._user_addons_count_locator))
            return self.find_element(*self._user_addons_count_locator)

        @property
        def user_addons_average_rating(self):
            self.wait.until(EC.visibility_of_element_located(self._user_addon_average_rating_locator))
            return self.find_element(*self._user_addon_average_rating_locator)

        @property
        def user_biography(self):
            self.wait.until(EC.visibility_of_element_located(self._user_biography_locator))
            return self.find_element(*self._user_biography_locator).text

        @property
        def edit_profile_button(self):
            self.wait.until(EC.visibility_of_element_located(self._user_profile_edit_link_locator))
            return self.find_element(*self._user_profile_edit_link_locator)

        def click_edit_profile_button(self):
            self.wait.until(EC.element_to_be_clickable(self._user_profile_edit_link_locator))
            self.find_element(*self._user_profile_edit_link_locator).click()
            return User(self.driver, self.page.base_url).wait_for_page_to_load()

        @property
        def user_extensions(self):
            self.wait.until(EC.visibility_of_element_located(self._user_extensions_card_locator))
            self.find_element(*self._user_extensions_card_locator)
            return Search(self.driver, self.page.base_url).wait_for_page_to_load()

        @property
        def user_extensions_card_header(self):
            self.wait.until(EC.visibility_of_element_located(self._user_extensions_card_header_locator))
            return self.find_element(*self._user_extensions_card_header_locator).text

        @property
        def user_extensions_results(self):
            self.wait.until(EC.visibility_of_element_located(self._user_extensions_results_locator))
            items = self.find_elements(*self._user_extensions_results_locator)
            return [
                Search(
                    self.driver, self.page.base_url
                ).SearchResultList.ResultListItems(self, el)
                for el in items
            ]

        @property
        def user_themes(self):
            self.wait.until(EC.visibility_of_element_located(self._user_themes_card_locator))
            self.find_element(*self._user_themes_card_locator)
            return Search(self.driver, self.page.base_url).wait_for_page_to_load()

        @property
        def user_themes_card_header(self):
            self.wait.until(EC.visibility_of_element_located(self._user_themes_card_header_locator))
            return self.find_element(*self._user_themes_card_header_locator).text

        @property
        def user_themes_results(self):
            self.wait.until(EC.visibility_of_element_located(self._user_themes_results_locator))
            items = self.find_elements(*self._user_themes_results_locator)
            return [
                Search(
                    self.driver, self.page.base_url
                ).SearchResultList.ResultListItems(self, el)
                for el in items
            ]

        @property
        def extensions_pagination(self):
            self.wait.until(EC.visibility_of_element_located(self._extensions_pagination_locator))
            return self.find_element(*self._extensions_pagination_locator)

        def extensions_next_page(self):
            self.wait.until(EC.element_to_be_clickable(self._extensions_next_page_locator))
            self.find_element(*self._extensions_next_page_locator).click()
            return User(self.driver, self.page.base_url).wait_for_page_to_load()

        @property
        def extensions_page_number(self):
            self.wait.until(EC.visibility_of_element_located(self._extensions_page_number_locator))
            return self.find_element(*self._extensions_page_number_locator).text

        @property
        def themes_pagination(self):
            self.wait.until(EC.visibility_of_element_located(self._themes_pagination_locator))
            return self.find_element(*self._themes_pagination_locator)

        def themes_next_page(self):
            self.wait.until(EC.element_to_be_clickable(self._themes_next_page_locator))
            self.find_element(*self._themes_next_page_locator).click()
            return User(self.driver, self.page.base_url).wait_for_page_to_load()

        @property
        def themes_page_number(self):
            self.wait.until(EC.visibility_of_element_located(self._themes_page_number_locator))
            return self.find_element(*self._themes_page_number_locator).text

        def user_reviews_section_loaded(self):
            self.wait.until(
                EC.visibility_of_element_located(self._user_reviews_card_locator)
            )

        @property
        def user_review_items(self):
            self.wait.until(EC.visibility_of_element_located(self._user_review_list_locator))
            items = self.find_elements(*self._user_review_list_locator)
            reviews = Reviews(self.driver, self.page.base_url).wait_for_page_to_load()
            return [reviews.UserReview(self, el) for el in items]

        def click_user_abuse_report(self):
            self.wait.until(EC.element_to_be_clickable(self._user_abuse_report_button_locator))
            self.find_element(*self._user_abuse_report_button_locator).click()
            self.wait.until(
                EC.element_to_be_clickable(self._abuse_report_textarea_locator)
            )

        @property
        def abuse_report_form_header(self):
            self.wait.until(EC.visibility_of_element_located(self._abuse_report_form_header_locator))
            return self.find_element(*self._abuse_report_form_header_locator).text

        @property
        def abuse_report_form_help_text(self):
            self.wait.until(EC.visibility_of_element_located(self._abuse_report_form_help_text))
            return self.find_element(*self._abuse_report_form_help_text).text

        @property
        def abuse_report_form_additional_help_text(self):
            self.wait.until(EC.visibility_of_element_located(self._abuse_report_form_additional_help_text))
            return self.find_element(*self._abuse_report_form_additional_help_text).text

        def user_abuse_report_input_text(self, value):
            self.wait.until(EC.visibility_of_element_located(self._abuse_report_textarea_locator))
            self.find_element(*self._abuse_report_textarea_locator).send_keys(value)

        def cancel_abuse_report_form(self):
            self.wait.until(EC.element_to_be_clickable(self._abuse_report_cancel_button_locator))
            self.find_element(*self._abuse_report_cancel_button_locator).click()
            self.wait.until(
                EC.element_to_be_clickable(self._user_abuse_report_button_locator)
            )

        @property
        def abuse_report_submit_disabled(self):
            self.wait.until(EC.visibility_of_element_located(self._abuse_report_submit_disabled_button_locator))
            return self.find_element(*self._abuse_report_submit_disabled_button_locator)

        def submit_user_abuse_report(self):
            self.wait.until(EC.element_to_be_clickable(self._abuse_report_submit_button_locator))
            self.find_element(*self._abuse_report_submit_button_locator).click()
            self.wait.until(
                EC.invisibility_of_element_located(
                    self._abuse_report_submit_button_locator
                )
            )

        @property
        def user_abuse_confirmation_message(self):
            self.wait.until(EC.visibility_of_element_located(self._abuse_report_confirm_message_locator))
            return self.find_element(*self._abuse_report_confirm_message_locator).text

    class EditProfile(Region):
        _view_profile_link_locator = (By.CSS_SELECTOR, '.UserProfileEdit-user-links a')
        _user_email_locator = (By.CSS_SELECTOR, '.UserProfileEdit-email')
        _user_email_help_text_locator = (
            By.CSS_SELECTOR,
            '.UserProfileEdit-email--help',
        )
        _user_email_help_link_locator = (
            By.CSS_SELECTOR,
            '.UserProfileEdit-email--help a',
        )
        _fxa_account_link_locator = (
            By.CSS_SELECTOR,
            '.UserProfileEdit-manage-account-link',
        )
        _edit_display_name_locator = (By.CSS_SELECTOR, '.UserProfileEdit-displayName')
        _edit_homepage_locator = (By.CSS_SELECTOR, '.UserProfileEdit-homepage')
        _edit_location_locator = (By.CSS_SELECTOR, '.UserProfileEdit-location')
        _edit_occupation_locator = (By.CSS_SELECTOR, '.UserProfileEdit-occupation')
        _profile_picture_placeholder_locator = (By.CSS_SELECTOR, '.Icon-anonymous-user')
        _upload_picture_button_locator = (
            By.CSS_SELECTOR,
            '.UserProfileEditPicture-file-input',
        )
        _uploaded_profile_picture_locator = (By.CSS_SELECTOR, '.UserAvatar-image')
        _delete_picture_button_locator = (
            By.CSS_SELECTOR,
            '.UserProfileEditPicture-delete-button button',
        )
        _cancel_delete_picture_locator = (
            By.CSS_SELECTOR,
            '.ConfirmationDialog-cancel-button',
        )
        _confirm_delete_picture_locator = (
            By.CSS_SELECTOR,
            '.ConfirmationDialog-confirm-button',
        )
        _picture_delete_success_text_locator = (By.CSS_SELECTOR, '.Notice-success p')
        _edit_biography_locator = (By.CSS_SELECTOR, '.UserProfileEdit-biography')
        _notifications_info_text_locator = (
            By.CSS_SELECTOR,
            '.UserProfileEdit-notifications-aside',
        )
        _notification_checkbox_locator = (
            By.CSS_SELECTOR,
            '.UserProfileEditNotification-input',
        )
        _notification_text_locator = (
            By.CSS_SELECTOR,
            '.UserProfileEditNotification label',
        )
        _notifications_help_text_locator = (
            By.CSS_SELECTOR,
            '.UserProfileEdit-notifications--help',
        )
        _edit_profile_submit_disabled_button_locator = (
            By.CSS_SELECTOR,
            '.UserProfileEdit-submit-button.Button--disabled',
        )
        _edit_profile_submit_button_locator = (
            By.CSS_SELECTOR,
            '.UserProfileEdit-submit-button',
        )
        _delete_profile_button_locator = (
            By.CSS_SELECTOR,
            '.UserProfileEdit-delete-button',
        )
        _delete_profile_overlay_locator = (
            By.CSS_SELECTOR,
            '.UserProfileEdit-deletion-modal',
        )
        _cancel_delete_profile_button_locator = (
            By.CSS_SELECTOR,
            '.UserProfileEdit-deletion-modal .UserProfileEdit-cancel-button',
        )
        _confirm_delete_profile_button_locator = (
            By.CSS_SELECTOR,
            '.UserProfileEdit-deletion-modal .UserProfileEdit-confirm-button',
        )
        _invalid_url_error_text_locator = (
            By.CSS_SELECTOR,
            '.Notice-error .Notice-text',
        )

        def click_view_profile_link(self):
            link = WebDriverWait(
                self.driver, 20, ignored_exceptions=StaleElementReferenceException
            ).until(EC.element_to_be_clickable(self._view_profile_link_locator))
            link.click()
            self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.UserProfile-name'))
            )

        @property
        def email_field(self):
            self.wait.until(EC.visibility_of_element_located(self._user_email_locator))
            return self.find_element(*self._user_email_locator).get_attribute('value')

        @property
        def email_field_help_text(self):
            self.wait.until(EC.visibility_of_element_located(self._user_email_help_text_locator))
            return self.find_element(*self._user_email_help_text_locator).text

        def email_field_help_link(self):
            self.wait.until(EC.element_to_be_clickable(self._user_email_help_link_locator))
            self.find_element(*self._user_email_help_link_locator).click()
            # waits for the fxa support page to be opened
            self.wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, '.sumo-page-heading')
                )
            )

        def link_to_fxa_account(self):
            self.wait.until(EC.element_to_be_clickable(self._fxa_account_link_locator))
            self.find_element(*self._fxa_account_link_locator).click()
            # waits for the fxa account page to be opened - check logo visibility
            self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.flex h1 span'))
            )

        def display_name(self, value):
            self.wait.until(EC.visibility_of_element_located(self._edit_display_name_locator))
            self.find_element(*self._edit_display_name_locator).send_keys(value)

        @property
        def display_name_field(self):
            self.wait.until(EC.visibility_of_element_located(self._edit_display_name_locator))
            return self.find_element(*self._edit_display_name_locator)

        def homepage_link(self, value):
            self.wait.until(EC.visibility_of_element_located(self._edit_homepage_locator))
            self.find_element(*self._edit_homepage_locator).send_keys(value)

        @property
        def homepage_link_field(self):
            self.wait.until(EC.visibility_of_element_located(self._edit_homepage_locator))
            return self.find_element(*self._edit_homepage_locator)

        def location(self, value):
            self.wait.until(EC.visibility_of_element_located(self._edit_location_locator))
            self.find_element(*self._edit_location_locator).send_keys(value)

        @property
        def location_field(self):
            self.wait.until(EC.visibility_of_element_located(self._edit_location_locator))
            return self.find_element(*self._edit_location_locator)

        def occupation(self, value):
            self.wait.until(EC.visibility_of_element_located(self._edit_occupation_locator))
            self.find_element(*self._edit_occupation_locator).send_keys(value)

        @property
        def profile_avatar_placeholder(self):
            self.wait.until(EC.visibility_of_element_located(self._profile_picture_placeholder_locator))
            return self.find_element(*self._profile_picture_placeholder_locator)

        def upload_picture(self, image):
            self.wait.until(EC.visibility_of_element_located(self._upload_picture_button_locator))
            button = self.find_element(*self._upload_picture_button_locator)
            path = Path(os.getcwd())
            img = str(path / "img" / image)
            button.send_keys(img)

        def profile_picture_is_displayed(self):
            self.wait.until(
                lambda _: self.is_element_displayed(
                    *self._uploaded_profile_picture_locator
                )
            )
            return self

        @property
        def picture_source(self):
            self.wait.until(EC.visibility_of_element_located(self._uploaded_profile_picture_locator))
            return self.find_element(
                *self._uploaded_profile_picture_locator
            ).get_attribute('src')

        def delete_profile_picture(self):
            self.wait.until(EC.element_to_be_clickable(self._delete_picture_button_locator))
            self.find_element(*self._delete_picture_button_locator).click()
            self.wait.until(
                EC.element_to_be_clickable(self._confirm_delete_picture_locator)
            )

        def cancel_delete_picture(self):
            self.wait.until(EC.element_to_be_clickable(self._cancel_delete_picture_locator))
            self.find_element(*self._cancel_delete_picture_locator).click()
            self.wait.until(
                EC.element_to_be_clickable(self._delete_picture_button_locator)
            )

        def confirm_delete_picture(self):
            self.wait.until(EC.element_to_be_clickable(self._confirm_delete_picture_locator))
            self.find_element(*self._confirm_delete_picture_locator).click()
            self.wait.until(
                EC.visibility_of_element_located(
                    self._picture_delete_success_text_locator
                )
            )

        @property
        def picture_delete_success_message(self):
            self.wait.until(EC.visibility_of_element_located(self._picture_delete_success_text_locator))
            return self.find_element(*self._picture_delete_success_text_locator).text

        def biography(self, value):
            self.wait.until(EC.visibility_of_element_located(self._edit_biography_locator))
            self.find_element(*self._edit_biography_locator).send_keys(value)

        @property
        def notifications_info_text(self):
            self.wait.until(EC.visibility_of_element_located(self._notifications_info_text_locator))
            return self.find_element(*self._notifications_info_text_locator).text

        @property
        def notifications_checkbox(self):
            """function used for developer notifications"""
            self.wait.until(
                lambda _: len(self.notification_text) == 8,
                message=f'There were {len(self.notification_text)} notifications displayed, expected 8',
            )
            return self.find_elements(*self._notification_checkbox_locator)

        @property
        def notification_text(self):
            self.wait.until(EC.visibility_of_element_located(self._notification_text_locator))
            items = self.find_elements(*self._notification_text_locator)
            # the notifications endpoint takes a bit longer to respond, so a wait is helpful here
            self.wait.until(
                lambda _: len(items) > 0,
                message=f'Expected notifications list to be loaded but the list contains {len(items)} items',
            )
            return items

        @property
        def notifications_help_text(self):
            self.wait.until(EC.visibility_of_element_located(self._notifications_help_text_locator))
            return self.find_element(*self._notifications_help_text_locator).text

        @property
        def submit_changes_button_disabled(self):
            self.wait.until(EC.visibility_of_element_located(self._edit_profile_submit_disabled_button_locator))
            return self.find_element(*self._edit_profile_submit_disabled_button_locator)

        def update_profile(self):
            """Updates a user profile and expects to remain on the Edit Profile page (likely due to an error)"""
            self.wait.until(EC.element_to_be_clickable(self._edit_profile_submit_button_locator))
            self.find_element(*self._edit_profile_submit_button_locator).click()

        def submit_changes(self):
            """Updates a user profile and expects to navigate to the View Profile page"""
            self.wait.until(EC.element_to_be_clickable(self._edit_profile_submit_button_locator))
            self.find_element(*self._edit_profile_submit_button_locator).click()
            self.wait.until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'UserProfile-name'))
            )

        def delete_account(self):
            self.wait.until(EC.element_to_be_clickable(self._delete_profile_button_locator))
            self.find_element(*self._delete_profile_button_locator).click()
            self.wait.until(
                EC.visibility_of_element_located(self._delete_profile_overlay_locator)
            )

        def cancel_delete_account(self):
            self.wait.until(EC.element_to_be_clickable(self._cancel_delete_profile_button_locator))
            self.find_element(*self._cancel_delete_profile_button_locator).click()
            self.wait.until(
                EC.invisibility_of_element_located(
                    self._cancel_delete_profile_button_locator
                )
            )

        def confirm_delete_account(self):
            self.wait.until(EC.element_to_be_clickable(self._confirm_delete_profile_button_locator))
            self.find_element(*self._confirm_delete_profile_button_locator).click()
            return Home(self.driver, self.page.base_url).wait_for_page_to_load()

        @property
        def invalid_url_error_text(self):
            self.wait.until(EC.visibility_of_element_located(self._invalid_url_error_text_locator))
            return self.find_element(*self._invalid_url_error_text_locator).text
