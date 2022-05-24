import time
import pytest
import requests

from pypom import Region

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.base import Base
from pages.desktop.developers.addons_manage import ManageAddons
from pages.desktop.developers.edit_addon import EditAddon
from pages.desktop.developers.submit_addon import SubmitAddon


class DevHubHome(Base):
    """AMO Developer Hub homepage"""

    URL_TEMPLATE = 'developers/'

    _logo_locator = (By.CLASS_NAME, 'DevHub-Navigation-Logo')
    _ext_workshop_link_locator = (By.LINK_TEXT, 'Extension Workshop')
    _documentation_link_locator = (By.LINK_TEXT, 'Documentation')
    _support_link_locator = (By.LINK_TEXT, 'Support')
    _blog_link_locator = (By.LINK_TEXT, 'Blog')
    _fxa_login_button_locator = (By.CLASS_NAME, 'DevHub-Navigation-Register')
    _page_overview_title_locator = (By.CSS_SELECTOR, '.DevHub-Overview h1')
    _page_overview_summary_locator = (By.CSS_SELECTOR, '.DevHub-Overview p')
    _learn_how_button_locator = (By.CSS_SELECTOR, '.DevHub-Overview a')
    _page_content_title_locator = (
        By.CSS_SELECTOR,
        '.DevHub-content-header--submit-or-manage',
    )
    _page_content_summary_locator = (
        By.CSS_SELECTOR,
        '.DevHub-content-copy p:nth-child(3)',
    )
    _page_content_login_link_locator = (
        By.CSS_SELECTOR,
        '.DevHub-content-copy:nth-child(1) > a',
    )
    _page_content_featured_image_locator = (
        By.CSS_SELECTOR,
        '.DevHub-content-image--submit-or-manage',
    )
    _get_involved_title_locator = (
        By.CSS_SELECTOR,
        '.DevHub-content-container--get-involved h3',
    )
    _get_involved_summary_locator = (
        By.CSS_SELECTOR,
        '.DevHub-content-container--get-involved p',
    )
    _dev_community_link_locator = (
        By.CSS_SELECTOR,
        '.DevHub-content-container--get-involved a',
    )
    _get_involved_image_locator = (By.CLASS_NAME, 'DevHub-content-image--get-involved')
    _footer_language_picker_locator = (By.ID, 'language')
    _footer_products_section_locator = (By.CSS_SELECTOR, '.Footer-products-links')
    _footer_links_locator = (By.CSS_SELECTOR, '.Footer-links li a')

    # elements visible only to logged in users
    _sign_out_link_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Navigation-SignOut a:nth-child(1)',
    )
    _user_logged_in_avatar_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Navigation-SignOut a:nth-child(2)',
    )
    _my_addons_header_link_locator = (By.LINK_TEXT, 'My Add-ons')
    _user_profile_picture_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Navigation-SignOut a img',
    )
    _logged_in_hero_banner_header_locator = (
        By.CSS_SELECTOR,
        '.DevHub-callout-box--banner h2',
    )
    _logged_in_hero_banner_text_locator = (
        By.CSS_SELECTOR,
        '.DevHub-callout-box--banner p',
    )
    _logged_in_hero_banner_link_locator = (
        By.CSS_SELECTOR,
        '.DevHub-callout-box--banner a',
    )
    _my_addons_section_header_locator = (By.CSS_SELECTOR, '.DevHub-MyAddons h2')
    _my_addons_section_paragraph_locator = (By.CSS_SELECTOR, '.DevHub-MyAddons-copy')
    _my_addons_section_list_locator = (By.CSS_SELECTOR, '.DevHub-MyAddons-item')
    _see_all_addons_link_locator = (
        By.CSS_SELECTOR,
        '.DevHub-MyAddons-item-buttons-all',
    )
    _submit_addon_button_locator = (
        By.CSS_SELECTOR,
        '.DevHub-MyAddons .Button:nth-of-type(1)',
    )
    _submit_theme_button_locator = (
        By.CSS_SELECTOR,
        '.DevHub-MyAddons .Button:nth-of-type(2)',
    )

    def wait_for_page_to_load(self):
        self.wait.until(lambda _: self.find_element(*self._logo_locator).is_displayed())
        return self

    @property
    def page_logo(self):
        return self.find_element(*self._logo_locator)

    def extension_workshop_is_loaded(self):
        # There are a few Devhub links that redirect to the Extension Workshop(EW) page.
        # The following method can be used by tests which verify that EW has loaded.
        self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.banner.intro h1'))
        )

    @property
    def extension_workshop(self):
        return self.find_element(*self._ext_workshop_link_locator)

    def click_documentation(self):
        self.find_element(*self._documentation_link_locator).click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, '.main-content h1'), 'Browser Extensions'
            ),
            message=f'Expected "Browser Extensions" in the page title but got'
            f' "{self.find_element(By.CSS_SELECTOR, ".main-content h1").text}".',
        )

    def click_support(self):
        self.find_element(*self._support_link_locator).click()

    def click_blog(self):
        self.find_element(*self._blog_link_locator).click()
        self.wait.until(EC.visibility_of_element_located((By.ID, 'site-title')))

    @property
    def header_login_button(self):
        return self.find_element(*self._fxa_login_button_locator)

    def click_header_login_button(self):
        self.find_element(*self._fxa_login_button_locator).click()
        from pages.desktop.frontend.login import Login

        return Login(self.selenium, self.base_url)

    @property
    def sign_out_link(self):
        return self.find_element(*self._sign_out_link_locator)

    def click_sign_out(self):
        self.sign_out_link.click()

    @property
    def user_avatar(self):
        return self.find_element(*self._user_logged_in_avatar_locator)

    def devhub_login(self, user):
        fxa = self.click_header_login_button()
        # wait for the FxA login page to load
        self.wait.until(
            EC.visibility_of_element_located((By.NAME, 'email')),
            message=f'FxA email input field was not displayed in {self.selenium.current_url}',
        )
        fxa.account(user)
        # wait for transition between FxA page and Devhub
        self.wait.until(
            EC.url_contains('developers'),
            message=f'Devhub could not be loaded in {self.selenium.current_url}'
            f'Response status code was {requests.head(self.selenium.current_url).status_code}',
        )
        # assess that the user has been logged in
        self.wait.until(
            lambda _: self.sign_out_link.is_displayed(),
            message=f'Log in flow was not successful. URL at fail time was {self.selenium.current_url}',
        )

    @property
    def devhub_overview_title(self):
        return self.find_element(*self._page_overview_title_locator).text

    @property
    def devhub_overview_summary(self):
        return self.find_element(*self._page_overview_summary_locator).text

    def click_overview_learn_how_button(self):
        self.find_element(*self._learn_how_button_locator).click()

    @property
    def devhub_content_title(self):
        return self.find_element(*self._page_content_title_locator).text

    @property
    def devhub_content_summary(self):
        return self.find_element(*self._page_content_summary_locator).text

    @property
    def devhub_content_image(self):
        return self.find_element(*self._page_content_featured_image_locator)

    @property
    def devhub_get_involved_title(self):
        return self.find_element(*self._get_involved_title_locator).text

    @property
    def devhub_get_involved_summary(self):
        return self.find_element(*self._get_involved_summary_locator).text

    @property
    def devhub_get_involved_link(self):
        return self.find_element(*self._dev_community_link_locator)

    @property
    def devhub_get_involved_image(self):
        return self.find_element(*self._get_involved_image_locator)

    def click_content_login_link(self):
        self.find_element(*self._page_content_login_link_locator).click()

    @property
    def user_profile_icon(self):
        # get the 'alt' attribute to determine if img is uploaded by the user and is not the default avatar
        return self.find_element(*self._user_profile_picture_locator).get_attribute(
            'alt'
        )

    def click_user_profile_picture(self):
        icon = self.wait.until(
            EC.element_to_be_clickable(self._user_profile_picture_locator)
        )
        icon.click()
        from pages.desktop.frontend.users import User

        return User(self.selenium, self.base_url)

    def click_my_addons_header_link(self):
        self.find_element(*self._my_addons_header_link_locator).click()
        return ManageAddons(self.selenium, self.base_url)

    @property
    def logged_in_hero_banner_header(self):
        return self.find_element(*self._logged_in_hero_banner_header_locator).text

    @property
    def my_addons_section_header(self):
        return self.find_element(*self._my_addons_section_header_locator)

    @property
    def my_addons_section_paragraph(self):
        return self.find_element(*self._my_addons_section_paragraph_locator)

    @property
    def logged_in_hero_banner_text(self):
        return self.find_element(*self._logged_in_hero_banner_text_locator).text

    def click_logged_in_hero_banner_extension_workshop_link(self):
        self.find_element(*self._logged_in_hero_banner_link_locator).click()

    def click_see_all_addons_link(self):
        self.find_element(*self._see_all_addons_link_locator).click()
        return ManageAddons(self.selenium, self.base_url)

    def click_submit_addon_button(self):
        self.find_element(*self._submit_addon_button_locator).click()
        return SubmitAddon(self.selenium, self.base_url)

    def click_submit_theme_button(self):
        self.find_element(*self._submit_theme_button_locator).click()
        return SubmitAddon(self.selenium, self.base_url)

    @property
    def my_addons_list(self):
        items = self.find_elements(*self._my_addons_section_list_locator)
        return [self.MyAddonsList(self, el) for el in items]

    @property
    def connect(self):
        return ConnectFooter(self)

    @property
    def resources(self):
        return ResourcesFooter(self)

    def footer_language_picker(self, value):
        select = Select(self.find_element(*self._footer_language_picker_locator))
        select.select_by_visible_text(value)

    @property
    def products_links(self):
        element = self.find_element(*self._footer_products_section_locator)
        return element.find_elements(*self._footer_links_locator)

    class MyAddonsList(Region):
        _my_addon_icon_locator = (By.CSS_SELECTOR, '.DevHub-MyAddons-item-icon')
        _my_addon_name_locator = (By.CSS_SELECTOR, '.DevHub-MyAddons-item-name')
        _my_addon_edit_link_locator = (By.CSS_SELECTOR, '.DevHub-MyAddons-item-edit')
        _my_addon_version_number_locator = (
            By.CSS_SELECTOR,
            '.DevHub-MyAddons-item-versions',
        )
        _my_addon_version_status_locator = (
            By.CSS_SELECTOR,
            '.DevHub-MyAddons-VersionStatus',
        )
        _my_addon_rating_text_locator = (By.CSS_SELECTOR, '.addon-rating strong')
        _my_addon_rating_stars_locator = (By.CSS_SELECTOR, '.stars')
        _my_addon_last_modified_date_locator = (
            By.CSS_SELECTOR,
            '.DevHub-MyAddons-item-modified span:nth-of-type(2)',
        )

        @property
        def my_addon_icon(self):
            return self.find_element(*self._my_addon_icon_locator)

        @property
        def my_addon_name(self):
            return self.find_element(*self._my_addon_name_locator)

        def click_my_addon_edit_link(self):
            self.find_element(*self._my_addon_edit_link_locator).click()
            return EditAddon(self.selenium, self.page.base_url)

        @property
        def my_addon_version_number(self):
            return self.find_element(*self._my_addon_version_number_locator)

        @property
        def my_addon_version_status(self):
            return self.find_element(*self._my_addon_version_status_locator)

        @property
        def my_addon_rating_text(self):
            return self.find_element(*self._my_addon_rating_text_locator)

        @property
        def my_addon_rating_stars(self):
            return self.find_element(*self._my_addon_rating_stars_locator)

        @property
        def my_addon_last_modified_date(self):
            return self.find_element(*self._my_addon_last_modified_date_locator)

        @property
        def my_addon_modified_date_text(self):
            """Get the date string from the Last Update date section and format it"""
            return self.my_addon_last_modified_date.text.replace('.', '')

        def is_listed_addon(self):
            """Checks the add-on listing visibility in DevHub homepage
            by looking at its status in the Edit add-on page"""
            status = self.click_my_addon_edit_link()
            try:
                # DevHub homepage will display only the Approved or Awaiting Review statuses, so we check these first
                if (
                    'Approved' in status.listed_addon_status
                    or 'Awaiting Review' in status.listed_addon_status
                ):
                    return True
                else:
                    # addon is either in Incomplete or Disabled status,
                    # so we won't see the status in DevHub homepage for such cases
                    return False
            except NoSuchElementException:
                # if the add-on is unlisted, there is no status displayed, so the 'listed_addon_status'
                # element is not present in the Edit Addon page, resulting in a 'NoSuchElementException'
                return False
            finally:
                # we execute this regardless of the status in order to go back and select
                # the next available addon in the Devhub Homepage, My Addons list
                self.selenium.back()


class ConnectFooter(Region):
    _connect_footer_title_locator = (
        By.CSS_SELECTOR,
        '.DevHub-content-header--Connect h2',
    )
    _twitter_column_title_locator = (
        By.CSS_SELECTOR,
        '.Devhub-content-copy--Connect div:nth-child(1) h4:nth-child(1)',
    )
    _twitter_links_locator = (
        By.CSS_SELECTOR,
        '.DevHub-content-copy--Connect-twitter-list a',
    )
    _more_column_title_locator = (
        By.CSS_SELECTOR,
        '.Devhub-content-copy--Connect div:nth-child(2) h4:nth-child(1)',
    )
    _more_contact_links_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Connect-section:nth-child(2) > ul a',
    )
    _newsletter_header_locator = (
        By.CSS_SELECTOR,
        '.Devhub-content-copy--Connect div:nth-child(3) h4',
    )
    _newsletter_info_text_locator = (
        By.CSS_SELECTOR,
        '.Devhub-content-copy--Connect div:nth-child(3) p',
    )
    _newsletter_email_input_field_locator = (By.ID, 'email')
    _newsletter_sign_up_button_locator = (By.CSS_SELECTOR, '.btn-success')
    _newsletter_privacy_checkbox_locator = (By.ID, 'privacy')
    _newsletter_privacy_notice_link_locator = (By.CSS_SELECTOR, '.form_group-agree a')
    _newsletter_sign_up_confirmation_header_locator = (
        By.CSS_SELECTOR,
        '.newsletter_thanks h2',
    )
    _newsletter_sign_up_confirmation_message_locator = (
        By.CSS_SELECTOR,
        '.newsletter_thanks p',
    )

    @property
    def connect_footer_title(self):
        return self.find_element(*self._connect_footer_title_locator).text

    @property
    def connect_twitter_title(self):
        return self.find_element(*self._twitter_column_title_locator).text

    @property
    def twitter_links(self):
        return self.find_elements(*self._twitter_links_locator)

    @property
    def connect_more_title(self):
        return self.find_element(*self._more_column_title_locator).text

    @property
    def more_connect_links(self):
        return self.find_elements(*self._more_contact_links_locator)

    @property
    def newsletter_section_header(self):
        return self.find_element(*self._newsletter_header_locator).text

    @property
    def newsletter_info_text(self):
        return self.find_element(*self._newsletter_info_text_locator).text

    def newsletter_email_input_field(self, email):
        self.find_element(*self._newsletter_email_input_field_locator).send_keys(email)

    @property
    def newsletter_sign_up(self):
        return self.find_element(*self._newsletter_sign_up_button_locator)

    def click_privacy_checkbox(self):
        self.find_element(*self._newsletter_privacy_checkbox_locator).click()

    def click_newsletter_privacy_notice_link(self):
        self.find_element(*self._newsletter_privacy_notice_link_locator).click()
        self.wait.until(
            EC.number_of_windows_to_be(2),
            message=f'Number of windows was {len(self.selenium.window_handles)}, expected 2',
        )
        new_tab = self.selenium.window_handles[1]
        self.selenium.switch_to.window(new_tab)

    @property
    def newsletter_signup_confirmation_header(self):
        return self.find_element(
            *self._newsletter_sign_up_confirmation_header_locator
        ).text

    @property
    def newsletter_signup_confirmation_message(self):
        return self.find_element(
            *self._newsletter_sign_up_confirmation_message_locator
        ).text

    def check_newsletter_signup_email(self, email):
        retry = 0
        while retry < 10:
            # verify that a response is available and get the email subject
            request = requests.get(f'https://restmail.net/mail/{email}', timeout=10)
            response = request.json()
            if response:
                confirmation = [key['subject'] for key in response]
                return confirmation
            elif not response:
                print('Confirmation email not received yet')
                # fail if we retired 10 times and there was no email received
                if retry == 9:
                    pytest.fail('Newsletter confirmation email was not sent')
                # pause between subsequent requests to give more time to the email to be sent
                time.sleep(2)
                retry += 1
        return self


class ResourcesFooter(Region):
    _documentation_section_header_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Footer-sections:nth-of-type(1) .DevHub-Footer-section:nth-of-type(1) h4',
    )
    _documentation_section_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Footer-sections:nth-of-type(1) .DevHub-Footer-section:nth-of-type(1)',
    )
    _tools_section_header_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Footer-sections:nth-of-type(1) .DevHub-Footer-section:nth-of-type(2) h4',
    )
    _tools_section_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Footer-sections:nth-of-type(1) .DevHub-Footer-section:nth-of-type(2)',
    )
    _promote_section_header_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Footer-sections:nth-of-type(1) .DevHub-Footer-section:nth-of-type(3) h4',
    )
    _promote_section_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Footer-sections:nth-of-type(1) .DevHub-Footer-section:nth-of-type(3)',
    )
    _resources_footer_section_links = (By.CSS_SELECTOR, '.DevHub-Footer-sections li a')
    _addon_review_section_header_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Footer-sections:nth-of-type(2) .DevHub-Footer-section:nth-of-type(1) h4',
    )
    _addon_review_info_text_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Footer-sections:nth-of-type(2) .DevHub-Footer-section:nth-of-type(1) p',
    )
    _addon_review_link_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Footer-sections:nth-of-type(2) .DevHub-Footer-section:nth-of-type(1) a',
    )
    _write_code_section_header_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Footer-sections:nth-of-type(2) .DevHub-Footer-section:nth-of-type(2) h4',
    )
    _write_code_info_text_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Footer-sections:nth-of-type(2) .DevHub-Footer-section:nth-of-type(2) p',
    )
    _write_code_link_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Footer-sections:nth-of-type(2) .DevHub-Footer-section:nth-of-type(2) a',
    )
    _participate_section_header_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Footer-sections:nth-of-type(2) .DevHub-Footer-section:nth-of-type(3) h4',
    )
    _participate_info_text_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Footer-sections:nth-of-type(2) .DevHub-Footer-section:nth-of-type(3) p',
    )
    _participate_link_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Footer-sections:nth-of-type(2) .DevHub-Footer-section:nth-of-type(3) a',
    )

    @property
    def documentation_section_header(self):
        return self.find_element(*self._documentation_section_header_locator).text

    @property
    def documentation_section_links(self):
        el = self.find_element(*self._documentation_section_locator)
        return el.find_elements(*self._resources_footer_section_links)

    @property
    def tools_section_header(self):
        return self.find_element(*self._tools_section_header_locator).text

    @property
    def tools_section_links(self):
        el = self.find_element(*self._tools_section_locator)
        return el.find_elements(*self._resources_footer_section_links)

    @property
    def promote_section_header(self):
        return self.find_element(*self._promote_section_header_locator).text

    @property
    def promote_section_links(self):
        el = self.find_element(*self._promote_section_locator)
        return el.find_elements(*self._resources_footer_section_links)

    @property
    def review_addons_section_header(self):
        return self.find_element(*self._addon_review_section_header_locator).text

    @property
    def review_addons_section_info_text(self):
        return self.find_element(*self._addon_review_info_text_locator).text

    def click_join_addon_review_link(self):
        self.find_element(*self._addon_review_link_locator).click()

    @property
    def write_code_section_header(self):
        return self.find_element(*self._write_code_section_header_locator).text

    @property
    def write_code_section_info_text(self):
        return self.find_element(*self._write_code_info_text_locator).text

    def click_write_code_section_link(self):
        self.find_element(*self._write_code_link_locator).click()

    @property
    def participate_section_header(self):
        return self.find_element(*self._participate_section_header_locator).text

    @property
    def participate_section_info_text(self):
        return self.find_element(*self._participate_info_text_locator).text

    def click_participate_section_link(self):
        self.find_element(*self._participate_link_locator).click()
