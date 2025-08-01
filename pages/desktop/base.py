import requests

from pypom import Page, Region

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Base(Page):
    _url = "{base_url}"
    _amo_header = (By.CLASS_NAME, "Header")

    def __init__(self, selenium, base_url, **kwargs):
        super(Base, self).__init__(selenium, base_url, timeout=30, **kwargs)

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._amo_header).is_displayed(),
            message="AMO header was not loaded",
        )
        return self

    def wait_for_title_update(self, term):
        self.wait.until(
            EC.title_contains(term),
            message=f"Page title was {self.driver.title}, expected {term}",
        )
        return self

    def wait_for_current_url(self, term):
        self.wait.until(
            EC.url_contains(term), message=f"The url was {self.driver.current_url}"
        )
        return self

    def wait_for_element_to_be_displayed(self, element):
        self.wait.until(EC.visibility_of_element_located(element))
        return self

    def wait_for_element_to_be_clickable(self, element):
        self.wait.until(EC.element_to_be_clickable(element))
        return self

    @property
    def header(self):
        return Header(self)

    @property
    def footer(self):
        return Footer(self)

    @property
    def logged_in(self):
        """Returns True if a user is logged in. Since the user element can become
        stale sometimes and causes the login test to fail, a StaleElementReferenceException
        was added to catch this error and wait for the element to be located again"""
        count = 0
        while count < 5:
            try:
                self.wait.until(
                    EC.visibility_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            ".Header-user-and-external-links .DropdownMenu-button-text",
                        )
                    ),
                    message="LOGIN FAILED: The user name was not displayed in the header after login.",
                )
                break
            except StaleElementReferenceException as exception:
                print(f"{exception}: Try to find the element again")
            count += 1
        return self

    @property
    def search(self):
        return self.header.SearchBox(self)

    def login(self, user):
        fxa = self.header.click_login()
        # wait for the FxA login page to load
        self.wait.until(
            EC.visibility_of_element_located((By.NAME, "email")),
            message=f"FxA email input field was not displayed in {self.driver.current_url}",
        )
        fxa.account(user)
        # verifies that the AMO page was fully loaded after login
        WebDriverWait(self.driver, 30).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "LoadingText")),
            message="AMO was not loaded properly after login.",
        )
        # assess that the user has been logged in
        self.wait.until(
            lambda _: self.logged_in,
            message=f"Log in flow was not successful. URL at fail time was {self.driver.current_url}",
        )

    def register(self):
        fxa_register_page = self.header.click_login()
        self.wait.until(EC.visibility_of_element_located((By.NAME, "email")))
        fxa_register_page.fxa_register()
        # wait for transition between FxA page and AMO
        self.wait.until(EC.url_contains("addons"))
        self.wait.until(lambda _: self.logged_in)

    def logout(self):
        self.header.click_logout()


class Header(Region):
    _root_locator = (By.CLASS_NAME, "Header")
    _header_title_locator = (By.CLASS_NAME, "Header-title")
    _firefox_logo_locator = (By.CLASS_NAME, "Header-title")
    _extensions_locator = (
        By.CSS_SELECTOR,
        ".SectionLinks \
                           > li:nth-child(1) > a:nth-child(1)",
    )
    _extensions_active_button_locator = (
        By.CLASS_NAME,
        "SectionLinks-link-extension.SectionLinks-link--active",
    )
    _login_locator = (By.CLASS_NAME, "Header-authenticate-button")
    _user_locator = (
        By.CSS_SELECTOR,
        ".Header-user-and-external-links .DropdownMenu-button-text",
    )
    _account_dropdown_locator = (
        By.CSS_SELECTOR,
        ".DropdownMenu.Header-authenticate-button .DropdownMenu-items",
    )
    _user_menu_links_locator = (
        By.CSS_SELECTOR,
        ".Header-user-and-external-links .DropdownMenuItem-link a",
    )
    _logout_locator = (
        By.CSS_SELECTOR,
        ".DropdownMenu-items .Header-logout-button button",
    )
    _more_menu_locator = (
        By.CSS_SELECTOR,
        ".Header-SectionLinks .SectionLinks-dropdown",
    )
    _more_dropdown_locator = (
        By.CSS_SELECTOR,
        ".SectionLinks-dropdown .DropdownMenu-items",
    )
    _more_dropdown_sections_locator = (By.CSS_SELECTOR, ".DropdownMenuItem-section")
    _more_dropdown_links_locator = (By.CSS_SELECTOR, ".DropdownMenuItem a")
    _themes_locator = (
        By.CSS_SELECTOR,
        ".SectionLinks > li:nth-child(2) > \
                       a:nth-child(1)",
    )
    _themes_active_button_locator = (
        By.CLASS_NAME,
        "SectionLinks-link-theme.SectionLinks-link--active",
    )
    _devhub_locator = (By.CLASS_NAME, "Header-developer-hub-link")
    _extension_workshop_locator = (By.CLASS_NAME, "Header-extension-workshop-link")
    _blog_link_locator = (By.CLASS_NAME, "Header-blog-link")
    _active_link_locator = (By.CLASS_NAME, "SectionLinks-link--active")

    def click_extensions(self):
        self.wait.until(EC.element_to_be_clickable(self._extensions_locator))
        self.find_element(*self._extensions_locator).click()
        from pages.desktop.frontend.extensions import Extensions

        return Extensions(self.driver, self.page.base_url).wait_for_page_to_load()

    @property
    def extensions_text(self):
        self.wait.until(EC.visibility_of_element_located(self._extensions_locator))
        return self.find_element(*self._extensions_locator).text

    @property
    def extensions_button_active(self):
        """Checks that the 'Extensions' menu button is highlighted when selected"""
        self.wait.until(
            EC.visibility_of_element_located(self._extensions_active_button_locator)
        )
        return self.find_element(*self._extensions_active_button_locator)

    @property
    def themes_link(self):
        self.wait.until(EC.visibility_of_element_located(self._themes_locator))
        return self.find_element(*self._themes_locator)

    def click_themes(self):
        self.wait.until(EC.element_to_be_clickable(self._themes_locator))
        self.find_element(*self._themes_locator).click()
        from pages.desktop.frontend.themes import Themes

        return Themes(self.driver, self.page.base_url).wait_for_page_to_load()

    @property
    def themes_button_active(self):
        """Checks that the 'Themes' menu button is highlighted when selected"""
        self.wait.until(
            EC.visibility_of_element_located(self._themes_active_button_locator)
        )
        return self.find_element(*self._themes_active_button_locator)

    def click_title(self):
        self.find_element(*self._header_title_locator).click()
        from pages.desktop.frontend.home import Home

        return Home(self.driver, self.page.base_url).wait_for_page_to_load()

    @property
    def login_button(self):
        return self.find_element(*self._login_locator)

    def click_login(self):
        self.find_element(*self._login_locator).click()
        from pages.desktop.frontend.login import Login

        return Login(self.driver, self.page.base_url)

    def user_header_display_name(self, value):
        WebDriverWait(
            self.driver, 30, ignored_exceptions=StaleElementReferenceException
        ).until(
            EC.text_to_be_present_in_element(self._user_locator, value),
            message="The expected displayed name was not visible",
        )

    def click_logout(self):
        user = WebDriverWait(
            self.driver, 30, ignored_exceptions=StaleElementReferenceException
        ).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    ".Header-authenticate-button",
                )
            )
        )
        action = ActionChains(self.driver)
        action.move_to_element(user)
        action.pause(3)
        action.perform()
        # assigning the webelement to a variable before initializing the action chains can lead
        # to stale element errors since the dropdown state changes when we hover over it
        logout = WebDriverWait(
            self.driver, 20, ignored_exceptions=StaleElementReferenceException
        ).until(EC.element_to_be_clickable(self._logout_locator))
        action.move_to_element(logout)
        action.pause(3)
        action.click()
        action.pause(3)
        action.perform()
        self.wait.until(
            lambda s: self.is_element_displayed(*self._login_locator),
            message="The login button was not displayed after logout",
        )

    def user_menu_link(self, count):
        self.wait.until(EC.visibility_of_element_located(self._user_menu_links_locator))
        return self.find_elements(*self._user_menu_links_locator)[count]

    def click_user_menu_links(self, count, landing_page):
        user = WebDriverWait(
            self.driver, 30, ignored_exceptions=StaleElementReferenceException
        ).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    ".Header-authenticate-button",
                )
            )
        )
        action = ActionChains(self.driver)
        action.move_to_element(user)
        action.pause(2)
        action.perform()
        link = WebDriverWait(
            self.driver, 20, ignored_exceptions=StaleElementReferenceException
        ).until(EC.element_to_be_clickable(self.user_menu_link(count)))
        action.move_to_element(link)
        action.pause(2)
        action.click()
        action.perform()
        # waits for the landing page to open
        self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, landing_page)),
            message=f"Expected page not loaded; page was {self.driver.current_url}",
        )

    @property
    def more_menu_link(self):
        self.wait.until(EC.visibility_of_element_located(self._more_menu_locator))
        return self.find_element(*self._more_menu_locator)

    @property
    def more_menu_dropdown_sections(self):
        return self.find_elements(*self._more_dropdown_sections_locator)

    @property
    def more_menu_dropdown_links(self):
        return self.find_elements(*self._more_dropdown_links_locator)

    def more_menu(self, item=None):
        menu = self.find_element(*self._more_menu_locator)
        dropdown = self.find_element(*self._more_dropdown_locator)
        link = menu.find_elements(*self._more_dropdown_links_locator)
        # Create an action chain clicking on the elements of the dropdown more menu
        action = ActionChains(self.driver)
        action.move_to_element(menu)
        action.pause(2)
        action.move_to_element(dropdown)
        action.move_to_element(link[item])
        action.click(link[item])
        action.pause(2)
        action.perform()

    @property
    def developer_hub_link(self):
        self.wait.until(EC.visibility_of_element_located(self._devhub_locator))
        return self.find_element(*self._devhub_locator)

    def click_developer_hub(self):
        self.wait.until(EC.element_to_be_clickable(self._devhub_locator))
        self.find_element(*self._devhub_locator).click()
        self.wait.until(
            EC.number_of_windows_to_be(2),
            message=f"Number of windows was {len(self.driver.window_handles)}, expected 2",
        )
        new_tab = self.driver.window_handles[1]
        self.driver.switch_to.window(new_tab)
        self.wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "DevHub-Navigation-Logo")),
            message=f"DevHub homepage not loaded; page was {self.driver.current_url}",
        )

    @property
    def extension_workshop_link(self):
        self.wait.until(
            EC.visibility_of_element_located(self._extension_workshop_locator)
        )
        return self.find_element(*self._extension_workshop_locator)

    def click_extension_workshop(self):
        self.wait.until(EC.element_to_be_clickable(self._extension_workshop_locator))
        self.find_element(*self._extension_workshop_locator).click()
        self.wait.until(
            EC.number_of_windows_to_be(2),
            message=f"Number of windows was {len(self.driver.window_handles)}, expected 2",
        )
        new_tab = self.driver.window_handles[1]
        self.driver.switch_to.window(new_tab)
        self.wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "logo")),
            message=f"Extension Workshop not loaded; page was {self.driver.current_url}",
        )

    @property
    def firefox_addons_blog_link(self):
        self.wait.until(EC.visibility_of_element_located(self._blog_link_locator))
        return self.find_element(*self._blog_link_locator)

    def click_firefox_addons_blog(self):
        self.wait.until(EC.element_to_be_clickable(self._blog_link_locator))
        self.find_element(*self._blog_link_locator).click()

    @property
    def is_active_link(self):
        return self.find_element(*self._active_link_locator).text

    class SearchBox(Region):
        _root_locator = (By.CLASS_NAME, "AutoSearchInput")
        _query_field_locator = (By.ID, "AutoSearchInput-q")
        _search_suggestions_list_locator = (
            By.CLASS_NAME,
            "AutoSearchInput-suggestions-list",
        )
        _search_suggestions_item_locator = (
            By.CLASS_NAME,
            "AutoSearchInput-suggestions-item",
        )
        _search_textbox_locator = (By.CLASS_NAME, "AutoSearchInput-query")
        _search_item_name = (By.CSS_SELECTOR, ".SearchSuggestion-name")
        _highlighted_selected_locator = (
            By.CSS_SELECTOR,
            ".AutoSearchInput-suggestions-item--highlighted",
        )

        @property
        def search_field(self):
            self.wait.until(EC.visibility_of_element_located(self._query_field_locator))
            return self.find_element(*self._query_field_locator)

        def search_for(self, term, execute=True):
            self.wait.until(
                EC.visibility_of_element_located(self._search_textbox_locator)
            )
            textbox = self.find_element(*self._search_textbox_locator)
            textbox.click()
            textbox.send_keys(term)
            # Send 'enter' since the mobile page does not have a submit button
            if execute:
                textbox.send_keys(Keys.ENTER)
                from pages.desktop.frontend.search import Search

                return Search(self.driver, self.page).wait_for_page_to_load()
            WebDriverWait(self.driver, 30).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "LoadingText"))
            )
            return self.search_suggestions

        @property
        def search_suggestions(self):
            self.wait.until(
                lambda _: self.is_element_displayed(
                    *self._search_suggestions_list_locator
                ),
                message="Search suggestions list did not open",
            )
            WebDriverWait(self.driver, 30).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "LoadingText"))
            )
            el_list = self.find_element(*self._search_suggestions_list_locator)
            items = el_list.find_elements(*self._search_suggestions_item_locator)
            return [self.SearchSuggestionItem(self.page, el) for el in items]

        @property
        def highlighted_suggestion(self):
            self.wait.until(
                EC.visibility_of_element_located(self._highlighted_selected_locator)
            )
            return self.find_element(*self._highlighted_selected_locator)

        class SearchSuggestionItem(Region):
            _item_name_locator = (By.CLASS_NAME, "SearchSuggestion-name")
            _item_icon_locator = (By.CLASS_NAME, "SearchSuggestion-icon")
            _promoted_icon_locator = (By.CSS_SELECTOR, ".Icon-recommended")

            @property
            def name(self):
                self.wait.until(
                    EC.visibility_of_element_located(self._item_name_locator)
                )
                return self.find_element(*self._item_name_locator).text

            @property
            def addon_icon(self):
                self.wait.until(
                    EC.visibility_of_element_located(self._item_icon_locator)
                )
                return self.find_element(*self._item_icon_locator)

            @property
            def promoted_icon(self):
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(self._promoted_icon_locator),
                    message="Promoted icon was not found for these search suggestions",
                )
                return self.find_element(*self._promoted_icon_locator).text

            @property
            def select(self):
                self.root.click()
                from pages.desktop.frontend.details import Detail

                return Detail(self.driver, self.page).wait_for_page_to_load()


class Footer(Region):
    _root_locator = (By.CSS_SELECTOR, ".Footer-wrapper")
    _footer_amo_links_locator = (By.CSS_SELECTOR, ".Footer-amo-links")
    _footer_browsers_links_locator = (By.CSS_SELECTOR, ".Footer-browsers-links")
    _footer_products_links_locator = (By.CSS_SELECTOR, ".Footer-product-links")
    _footer_mozilla_link_locator = (By.CSS_SELECTOR, ".Footer-mozilla-link")
    _footer_social_locator = (By.CSS_SELECTOR, ".Footer-links-social")
    _footer_links_locator = (By.CSS_SELECTOR, ".Footer-links li a")
    _footer_legal_locator = (By.CSS_SELECTOR, ".Footer-legal-links ")
    _footer_copyright_links_locator = (By.CSS_SELECTOR, ".Footer-copyright a")
    _copyright_message_locator = (By.CSS_SELECTOR, ".Footer-copyright")
    _language_picker_locator = (By.ID, "lang-picker")

    @property
    def addon_links(self):
        self.wait.until(
            EC.visibility_of_element_located(self._footer_amo_links_locator)
        )
        element = self.find_element(*self._footer_amo_links_locator)
        return element.find_elements(*self._footer_links_locator)

    @property
    def browsers_links(self):
        self.wait.until(
            EC.visibility_of_element_located(self._footer_browsers_links_locator)
        )
        element = self.find_element(*self._footer_browsers_links_locator)
        return element.find_elements(*self._footer_links_locator)

    @property
    def products_links(self):
        self.wait.until(
            EC.visibility_of_element_located(self._footer_products_links_locator)
        )
        element = self.find_element(*self._footer_products_links_locator)
        return element.find_elements(*self._footer_links_locator)

    @property
    def mozilla_link(self):
        self.wait.until(
            EC.visibility_of_element_located(self._footer_mozilla_link_locator)
        )
        return self.find_element(*self._footer_mozilla_link_locator)

    @property
    def social_links(self):
        self.wait.until(EC.visibility_of_element_located(self._footer_social_locator))
        element = self.find_element(*self._footer_social_locator)
        return element.find_elements(By.CSS_SELECTOR, "li a")

    @property
    def legal_links(self):
        self.wait.until(EC.visibility_of_element_located(self._footer_legal_locator))
        element = self.find_element(*self._footer_legal_locator)
        return element.find_elements(By.CSS_SELECTOR, "li a")

    @property
    def copyright_links(self):
        self.wait.until(
            EC.visibility_of_element_located(self._footer_copyright_links_locator)
        )
        return self.find_elements(*self._footer_copyright_links_locator)

    @property
    def copyright_message(self):
        self.wait.until(
            EC.visibility_of_element_located(self._copyright_message_locator)
        )
        return self.find_element(*self._copyright_message_locator)

    def language_picker(self, value):
        self.wait.until(EC.visibility_of_element_located(self._language_picker_locator))
        select = Select(self.find_element(*self._language_picker_locator))
        select.select_by_visible_text(value)
