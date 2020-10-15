import time
from pypom import Page, Region
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Base(Page):
    _url = '{base_url}/{locale}'
    _amo_header = (By.CLASS_NAME, 'Header')

    def __init__(self, selenium, base_url, locale='en-US', **kwargs):
        super(Base, self).__init__(
            selenium, base_url, locale=locale, timeout=30, **kwargs)

    def wait_for_page_to_load(self):
        self.wait.until(
            lambda _: self.find_element(*self._amo_header).is_displayed())
        return self

    def wait_for_title_update(self, term):
        self.wait.until(EC.title_contains(term))
        return self

    def wait_for_current_url(self, term):
        self.wait.until(EC.url_contains(term))
        return self

    @property
    def header(self):
        return Header(self)

    @property
    def footer(self):
        return Footer(self)

    @property
    def logged_in(self):
        """Returns True if a user is logged in"""
        return self.is_element_displayed(*self.header._user_locator)

    @property
    def search(self):
        return self.header.SearchBox(self)

    # this is WIP
    def login(self, variables):
        login_page = self.header.click_login()
        time.sleep(1)
        login_page.login_regular_user(variables)
        self.selenium.get(self.base_url)
        self.wait.until(lambda _: self.logged_in)

    def logout(self):
        self.header.click_logout()


class Header(Region):
    _root_locator = (By.CLASS_NAME, 'Header')
    _header_title_locator = (By.CLASS_NAME, 'Header-title')
    _explore_locator = (By.CSS_SELECTOR, '.SectionLinks > li:nth-child(1) \
                        > a:nth-child(1)')
    _firefox_logo_locator = (By.CLASS_NAME, 'Header-title')
    _extensions_locator = (By.CSS_SELECTOR, '.SectionLinks \
                           > li:nth-child(2) > a:nth-child(1)')
    _login_locator = (By.CLASS_NAME, 'Header-authenticate-button')
    _logout_locator = (
        By.CSS_SELECTOR, '.DropdownMenu-items .Header-logout-button')
    _more_dropdown_locator = (
        By.CSS_SELECTOR,
        '.Header-SectionLinks .SectionLinks-dropdown')
    _more_dropdown_link_locator = (By.CSS_SELECTOR, '.DropdownMenuItem a')
    _themes_locator = (By.CSS_SELECTOR, '.SectionLinks > li:nth-child(3) > \
                       a:nth-child(1)')
    _user_locator = (
        By.CSS_SELECTOR,
        '.Header-user-and-external-links .DropdownMenu-button-text')
    _devhub_locator = (By.CLASS_NAME, 'Header-developer-hub-link')
    _extension_workshop_locator = (By.CLASS_NAME, 'Header-extension-workshop-link')
    _active_link_locator = (By.CLASS_NAME, 'SectionLinks-link--active')

    def click_explore(self):
        self.find_element(*self._firefox_logo_locator).click()

    def click_extensions(self):
        self.find_element(*self._extensions_locator).click()
        from pages.desktop.extensions import Extensions
        return Extensions(
            self.selenium, self.page.base_url).wait_for_page_to_load()

    @property
    def extensions_text(self):
        return self.find_element(*self._extensions_locator).text

    def click_themes(self):
        self.find_element(*self._themes_locator).click()
        from pages.desktop.themes import Themes
        return Themes(
            self.selenium, self.page.base_url).wait_for_page_to_load()

    def click_title(self):
        self.find_element(*self._header_title_locator).click()

        from pages.desktop.home import Home
        return Home(self.selenium, self.page.base_url).wait_for_page_to_load()

    def click_login(self):
        self.find_element(*self._login_locator).click()
        from pages.desktop.login import Login
        return Login(self.selenium, self.page.base_url)

    def click_logout(self):
        user = self.find_element(*self._user_locator)
        logout = self.find_element(*self._logout_locator)
        action = ActionChains(self.selenium)
        action.move_to_element(user)
        action.click()
        action.pause(2)
        action.move_to_element(logout)
        action.pause(2)
        action.click(logout)
        action.perform()
        self.wait.until(lambda s: self.is_element_displayed(
            *self._login_locator))

    def more_menu(self, item=None):
        menu = self.find_element(*self._more_dropdown_locator)
        links = menu.find_elements(*self._more_dropdown_link_locator)
        # Create an action chain clicking on the elements of the dropdown more
        # menu. It pauses between each action to account for lag.
        menu.click()
        action = ActionChains(self.selenium)
        action.move_to_element(menu)
        action.click_and_hold()
        action.pause(2)
        action.move_to_element(links[item])
        action.pause(2)
        action.click(links[item])
        action.pause(2)
        action.perform()

    def click_developer_hub(self):
        self.find_element(*self._devhub_locator).click()
        self.wait.until(EC.number_of_windows_to_be(2))
        new_tab = self.selenium.window_handles[1]
        self.selenium.switch_to_window(new_tab)

    def click_extension_workshop(self):
        self.find_element(*self._extension_workshop_locator).click()
        self.wait.until(EC.number_of_windows_to_be(2))
        new_tab = self.selenium.window_handles[1]
        self.selenium.switch_to_window(new_tab)
        self.wait.until(EC.visibility_of_element_located((
            By.CLASS_NAME, 'logo')))

    @property
    def is_active_link(self):
        return self.find_element(*self._active_link_locator).text

    class SearchBox(Region):
        _root_locator = (By.CLASS_NAME, 'AutoSearchInput')
        _query_field_locator = (By.ID, 'AutoSearchInput-q')
        _search_suggestions_list_locator = (
            By.CLASS_NAME, 'AutoSearchInput-suggestions-list')
        _search_suggestions_item_locator = (
            By.CLASS_NAME, 'AutoSearchInput-suggestions-item')
        _search_textbox_locator = (By.CLASS_NAME, 'AutoSearchInput-query')
        _search_item_name = (By.CSS_SELECTOR, '.SearchSuggestion-name')
        _highlighted_selected_locator = (By.CSS_SELECTOR, '.AutoSearchInput-suggestions-item--highlighted')

        @property
        def search_field(self):
            return self.find_element(*self._query_field_locator)

        def search_for(self, term, execute=True):
            textbox = self.find_element(*self._search_textbox_locator)
            textbox.click()
            textbox.send_keys(term)
            # Send 'enter' since the mobile page does not have a submit button
            if execute:
                textbox.send_keys(Keys.ENTER)
                from pages.desktop.search import Search
                return Search(self.selenium, self.page).wait_for_page_to_load()
            WebDriverWait(self.selenium, 30).until(
                EC.invisibility_of_element_located(
                    (By.CLASS_NAME, 'LoadingText')))
            return self.search_suggestions

        @property
        def search_suggestions(self):
            self.wait.until(
                lambda _: self.is_element_displayed(
                    *self._search_suggestions_list_locator)
            )
            WebDriverWait(self.selenium, 30).until(
                EC.invisibility_of_element_located(
                    (By.CLASS_NAME, 'LoadingText')))
            el_list = self.find_element(*self._search_suggestions_list_locator)
            items = el_list.find_elements(
                *self._search_suggestions_item_locator)
            return [self.SearchSuggestionItem(self.page, el) for el in items]

        @property
        def highlighted_suggestion(self):
            return self.find_element(*self._highlighted_selected_locator)

        class SearchSuggestionItem(Region):
            _item_name_locator = (By.CLASS_NAME, 'SearchSuggestion-name')
            _item_icon_locator = (By.CLASS_NAME, 'SearchSuggestion-icon')
            _promoted_icon_locator = (By.CSS_SELECTOR, '.IconPromotedBadge > span')

            @property
            def name(self):
                return self.find_element(*self._item_name_locator).text

            @property
            def addon_icon(self):
                return self.find_element(*self._item_icon_locator)

            @property
            def promoted_icon(self):
                WebDriverWait(self.selenium, 10).until(
                    EC.visibility_of_element_located(
                        self._promoted_icon_locator),
                    message='Promoted icon was not found for these search suggestions'
                )
                return self.find_element(*self._promoted_icon_locator).text

            @property
            def select(self):
                self.root.click()
                from pages.desktop.details import Detail
                return Detail(self.selenium, self.page).wait_for_page_to_load()


class Footer(Region):
    _root_locator = (By.CSS_SELECTOR, '.Footer-wrapper')
    _footer_amo_links_locator = (By.CSS_SELECTOR, '.Footer-amo-links')
    _footer_browsers_links_locator = (By.CSS_SELECTOR, '.Footer-browsers-links')
    _footer_products_links_locator = (By.CSS_SELECTOR, '.Footer-product-links')
    _footer_mozilla_link_locator = (By.CSS_SELECTOR, '.Footer-mozilla-link')
    _footer_social_locator = (By.CSS_SELECTOR, '.Footer-links-social')
    _footer_links_locator = (By.CSS_SELECTOR, '.Footer-links li a')
    _footer_legal_locator = (By.CSS_SELECTOR, '.Footer-legal-links ')
    _language_picker_locator = (By.ID, 'lang-picker')

    @property
    def addon_links(self):
        element = self.find_element(*self._footer_amo_links_locator)
        return element.find_elements(*self._footer_links_locator)

    @property
    def browsers_links(self):
        element = self.find_element(*self._footer_browsers_links_locator)
        return element.find_elements(*self._footer_links_locator)

    @property
    def products_links(self):
        element = self.find_element(*self._footer_products_links_locator)
        return element.find_elements(*self._footer_links_locator)

    @property
    def mozilla_link(self):
        return self.find_element(*self._footer_mozilla_link_locator)

    @property
    def social_links(self):
        element = self.find_element(*self._footer_social_locator)
        return element.find_elements(By.CSS_SELECTOR, 'li a')

    @property
    def legal_links(self):
        element = self.find_element(*self._footer_legal_locator)
        return element.find_elements(By.CSS_SELECTOR, 'li a')

    def language_picker(self, value):
        select = Select(self.find_element(*self._language_picker_locator))
        select.select_by_visible_text(value)
