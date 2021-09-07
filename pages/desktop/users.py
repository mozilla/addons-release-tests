import os

from pypom import Region
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.base import Base
from pages.desktop.home import Home


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
        self.wait.until(
            lambda _: self.is_element_displayed(*self._display_name_locator)
        )
        return self

    @property
    def user_display_name(self):
        return self.find_element(*self._display_name_locator).text

    @property
    def view(self):
        return self.ViewProfile(self)

    @property
    def edit(self):
        return self.EditProfile(self)

    class ViewProfile(Region):
        _user_icon_placeholder_locator = (By.CSS_SELECTOR, '.Icon-anonymous-user')
        _user_profile_image_locator = (By.CSS_SELECTOR, '.UserAvatar-image')
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

        @property
        def user_profile_icon_placeholder(self):
            return self.find_element(*self._user_icon_placeholder_locator)

        @property
        def user_profile_icon(self):
            return self.find_element(*self._user_profile_image_locator)

        @property
        def icon_source(self):
            return self.user_profile_icon.get_attribute('src')

        @property
        def user_homepage(self):
            return self.find_element(*self._user_homepage_locator).get_attribute('href')

        @property
        def user_location(self):
            return self.find_element(*self._user_location_locator).text

        @property
        def user_occupation(self):
            return self.find_element(*self._user_occupation_locator).text

        @property
        def user_profile_creation_date(self):
            return self.find_element(*self._user_creation_date_locator)

        @property
        def user_addons_number(self):
            return self.find_element(*self._user_addons_count_locator)

        @property
        def user_addons_average_rating(self):
            return self.find_element(*self._user_addon_average_rating_locator)

        @property
        def user_biography(self):
            return self.find_element(*self._user_biography_locator).text

        def click_edit_profile_button(self):
            self.find_element(*self._user_profile_edit_link_locator).click()

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
            '.UserProfileEditNotification-checkbox',
        )
        _notification_text_locator = (
            By.CSS_SELECTOR,
            '.UserProfileEditNotification label',
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

        def click_view_profile_link(self):
            self.find_element(*self._view_profile_link_locator).click()
            return User(self.selenium, self.page.base_url).wait_for_user_to_load()

        @property
        def email_field(self):
            return self.find_element(*self._user_email_locator).get_attribute('value')

        @property
        def email_field_help_text(self):
            return self.find_element(*self._user_email_help_text_locator).text

        def email_field_help_link(self):
            self.find_element(*self._user_email_help_link_locator).click()
            # waits for the fxa support page to be opened
            self.wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, '.sumo-page-heading')
                )
            )

        def link_to_fxa_account(self):
            self.find_element(*self._fxa_account_link_locator).click()
            # waits for the fxa account page to be opened - check logo visibility
            self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.flex h1 span'))
            )

        def display_name(self, value):
            self.find_element(*self._edit_display_name_locator).send_keys(value)

        def homepage_link(self, value):
            self.find_element(*self._edit_homepage_locator).send_keys(value)

        def location(self, value):
            self.find_element(*self._edit_location_locator).send_keys(value)

        def occupation(self, value):
            self.find_element(*self._edit_occupation_locator).send_keys(value)

        @property
        def profile_avatar_placeholder(self):
            return self.find_element(*self._profile_picture_placeholder_locator)

        def upload_picture(self, image):
            button = self.find_element(*self._upload_picture_button_locator)
            path = os.getcwd()
            img = f'{path}\img\{image}'
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
            return self.find_element(
                *self._uploaded_profile_picture_locator
            ).get_attribute('src')

        def delete_profile_picture(self):
            self.find_element(*self._delete_picture_button_locator).click()
            self.wait.until(
                EC.element_to_be_clickable(self._confirm_delete_picture_locator)
            )

        def cancel_delete_picture(self):
            self.find_element(*self._cancel_delete_picture_locator).click()
            self.wait.until(
                EC.element_to_be_clickable(self._delete_picture_button_locator)
            )

        def confirm_delete_picture(self):
            self.find_element(*self._confirm_delete_picture_locator).click()
            self.wait.until(
                EC.visibility_of_element_located(
                    self._picture_delete_success_text_locator
                )
            )

        @property
        def picture_delete_success_message(self):
            return self.find_element(*self._picture_delete_success_text_locator).text

        def biography(self, value):
            self.find_element(*self._edit_biography_locator).send_keys(value)

        @property
        def notifications_help_text(self):
            return self.find_element(*self._notifications_info_text_locator)

        @property
        def notifications_checkbox(self):
            return self.find_elements(*self._notification_checkbox_locator)

        @property
        def notification_text(self):
            return self.find_elements(*self._notification_text_locator)

        def submit_changes(self):
            self.find_element(*self._edit_profile_submit_button_locator).click()

        def delete_account(self):
            self.find_element(*self._delete_profile_button_locator).click()
            self.wait.until(
                EC.visibility_of_element_located(self._delete_profile_overlay_locator)
            )

        def cancel_delete_account(self):
            self.find_element(*self._cancel_delete_profile_button_locator).click()
            self.wait.until(
                EC.invisibility_of_element_located(
                    self._cancel_delete_profile_button_locator
                )
            )

        def confirm_delete_account(self):
            self.find_element(*self._confirm_delete_profile_button_locator).click()
            return Home(self.selenium, self.page.base_url).wait_for_page_to_load()
