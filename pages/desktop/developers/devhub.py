import time
import pytest
import requests

from pypom import Region

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.base import Base


class DevHub(Base):
    """AMO Developer Hub homepage"""

    URL_TEMPLATE = 'developers/'

    _logo_locator = (By.CLASS_NAME, 'DevHub-Navigation-Logo')
    _ext_workshop_link_locator = (By.LINK_TEXT, 'Extension Workshop')
    _documentation_link_locator = (By.LINK_TEXT, 'Documentation')
    _support_link_locator = (By.LINK_TEXT, 'Support')
    _blog_link_locator = (By.LINK_TEXT, 'Blog')
    _fxa_login_button_locator = (By.CLASS_NAME, 'DevHub-Navigation-Register')
    _sign_out_link_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Navigation-SignOut a:nth-child(1)',
    )
    _user_logged_in_avatar_locator = (
        By.CSS_SELECTOR,
        '.DevHub-Navigation-SignOut a:nth-child(2)',
    )
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
    def connect(self):
        return ConnectFooter(self)

    def footer_language_picker(self, value):
        select = Select(self.find_element(*self._footer_language_picker_locator))
        select.select_by_visible_text(value)

    @property
    def products_links(self):
        element = self.find_element(*self._footer_products_section_locator)
        return element.find_elements(*self._footer_links_locator)


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
