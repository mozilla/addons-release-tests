from pypom import Page, Region

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC


class AboutAddons(Page):
    _addon_cards_locator = (By.CLASS_NAME, "card.addon")
    _search_box_locator = (By.CSS_SELECTOR, ".main-search search-textbox")
    _extension_tab_button_locator = (By.CSS_SELECTOR, 'button[name = "extension"]')
    _theme_tab_button_locator = (By.CSS_SELECTOR, 'button[name = "theme"]')
    _dictionary_tab_button_locator = (By.CSS_SELECTOR, 'button[name = "dictionary"]')
    _langpack_tab_button_locator = (By.CSS_SELECTOR, 'button[name = "locale"]')
    _extension_disable_toggle_locator = (By.CLASS_NAME, "extension-enable-button")
    _enabled_theme_status_locator = (By.CLASS_NAME, "card.addon")
    _installed_addon_cards_locator = (By.CSS_SELECTOR, ".card.addon")
    _enabled_theme_image_locator = (By.CLASS_NAME, "card-heading-image")
    _installed_addon_name_locator = (By.CSS_SELECTOR, ".addon-name a")
    _installed_addon_author_locator = (By.CSS_SELECTOR, ".addon-detail-row-author a")
    _find_more_addons_button_locator = (By.CLASS_NAME, "primary")
    _installed_extension_version_locator = (
        By.CSS_SELECTOR,
        ".addon-detail-row-version",
    )
    _options_button_locator = (By.CSS_SELECTOR, "button.more-options-button[action='more-options']")
    _menu_remove_item_locator = (By.CSS_SELECTOR, 'panel-item[action="remove"]')
    _menu_report_item_locator = (By.CSS_SELECTOR, 'panel-item[action="report"]')
    _menu_expand_item_locator = (By.CSS_SELECTOR, 'panel-item[action="expand"]')
    _menu_preferences_item_locator = (
        By.CSS_SELECTOR,
        'panel-item[action="preferences"]',
    )
    _undo_remove_button_locator = (By.CSS_SELECTOR, 'button[action="undo"]')

    def wait_for_page_to_load(self):
        self.wait.until(
            EC.visibility_of_element_located(self._find_more_addons_button_locator)
        )
        return self

    @property
    def search_field(self):
        self.wait.until(EC.presence_of_element_located(self._search_box_locator))
        host = self.find_element(*self._search_box_locator)
        inner_input = self.driver.execute_script(
            "return arguments[0].shadowRoot && arguments[0].shadowRoot.querySelector('input')",
            host,
        )
        return inner_input if inner_input else host

    def search_box(self, value):
        search_field = self.search_field
        search_field.send_keys(value)
        # send Enter to initiate search redirection to AMO
        search_field.send_keys(Keys.ENTER)
        # AMO search results open in a new tab, so we need to switch windows
        self.wait.until(
            EC.number_of_windows_to_be(2),
            message=f"Number of windows was {len(self.driver.window_handles)}, expected 2",
        )
        self.driver.switch_to.window(self.driver.window_handles[1])
        from pages.desktop.frontend.search import Search

        return Search(self.driver, self.base_url).wait_for_page_to_load()

    def click_extensions_side_button(self):
        self.wait.until(EC.element_to_be_clickable(self._extension_tab_button_locator))
        self.find_element(*self._extension_tab_button_locator).click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, "list-section-heading"), "Enabled"
            )
        )

    def click_themes_side_button(self):
        self.wait.until(EC.element_to_be_clickable(self._theme_tab_button_locator))
        self.find_element(*self._theme_tab_button_locator).click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, "list-section-heading"), "Enabled"
            )
        )

    def click_dictionaries_side_button(self):
        self.wait.until(EC.element_to_be_clickable(self._dictionary_tab_button_locator))
        self.find_element(*self._dictionary_tab_button_locator).click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, "list-section-heading"), "Enabled"
            )
        )

    def click_language_side_button(self):
        self.wait.until(EC.element_to_be_clickable(self._langpack_tab_button_locator))
        self.find_element(*self._langpack_tab_button_locator).click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, "list-section-heading"), "Enabled"
            )
        )

    def disable_extension(self):
        self.wait.until(
            EC.element_to_be_clickable(self._extension_disable_toggle_locator)
        )
        self.find_element(*self._extension_disable_toggle_locator).click()

    @property
    def installed_addon_cards(self):
        self.wait.until(
            EC.visibility_of_element_located(self._installed_addon_cards_locator)
        )
        return self.find_elements(*self._installed_addon_cards_locator)

    @property
    def installed_addon_name(self):
        return self.find_elements(*self._installed_addon_name_locator)

    @property
    def installed_addon_author_name(self):
        self.wait.until(
            EC.visibility_of_element_located(self._installed_addon_author_locator)
        )
        return self.find_element(*self._installed_addon_author_locator).text

    @property
    def enabled_theme_active_status(self):
        """Verifies if a theme is enabled"""
        self.wait.until(
            EC.visibility_of_element_located(self._enabled_theme_status_locator)
        )
        el = self.find_elements(*self._enabled_theme_status_locator)
        return el[0].get_attribute("active")

    @property
    def enabled_theme_image(self):
        return self.find_elements(*self._enabled_theme_image_locator)[0].get_attribute(
            "src"
        )

    @property
    def addon_cards_items(self):
        self.wait.until(EC.visibility_of_element_located(self._addon_cards_locator))
        items = self.find_elements(*self._addon_cards_locator)
        return [self.AddonCards(self, el) for el in items]

    def click_find_more_addons(self):
        self.wait.until(
            EC.element_to_be_clickable(self._find_more_addons_button_locator)
        )
        self.find_element(*self._find_more_addons_button_locator).click()
        # this button opens AMO homepage in a new tab
        self.wait.until(
            EC.number_of_windows_to_be(2),
            message=f"Number of windows was {len(self.driver.window_handles)}, expected 2",
        )
        self.driver.switch_to.window(self.driver.window_handles[1])
        from pages.desktop.frontend.home import Home

        return Home(self.driver, self.base_url).wait_for_page_to_load()

    @property
    def installed_version_number(self):
        self.wait.until(
            EC.visibility_of_element_located(self._installed_extension_version_locator)
        )
        return self.find_element(
            *self._installed_extension_version_locator
        ).text.replace("Version\n", "")

    @property
    def menu_remove_item_locator(self):
        self.wait.until(
            EC.visibility_of_element_located(self._menu_remove_item_locator)
        )
        return self.find_element(*self._menu_remove_item_locator)

    def click_options_button(self):
        self.wait.until(EC.element_to_be_clickable(self._options_button_locator))
        self.find_element(*self._options_button_locator).click()

    def click_panel_item_action_check_for_updates(self):
        el = self.driver.execute_script(
            "return document.querySelector('panel-item[action=\"view-recent-updates\"]')"
        )
        el.click()
        from pages.desktop.view_recent_updates import ViewRecentUpdates

        return ViewRecentUpdates(self.driver, self.base_url).wait_for_page_to_load()

    def click_panel_item_action_debug_addons(self):
        initial_handles = list(self.driver.window_handles)
        el = self.driver.execute_script(
            "return document.querySelector('panel-item[action=\"debug-addons\"]')"
        )
        el.click()
        self.wait.until(
            lambda _: len(self.driver.window_handles) > len(initial_handles),
            message="Debug Add-ons did not open in a new tab",
        )
        new_handle = next(
            h for h in self.driver.window_handles if h not in initial_handles
        )
        self.driver.switch_to.window(new_handle)
        from pages.desktop.about_debug_addons import AboutDebug

        return AboutDebug(self.driver, self.base_url).wait_for_page_to_load()

    def click_panel_item_action_manage_shortcuts(self):
        el = self.driver.execute_script(
            "return document.querySelector('panel-item[action=\"manage-shortcuts\"]')"
        )
        el.click()
        from pages.desktop.manage_shortcuts import ManageShortcuts

        return ManageShortcuts(self.driver, self.base_url).wait_for_page_to_load()

    def menu_item_actions(self):
        return [
            el.get_attribute("action")
            for el in self.find_elements(By.CSS_SELECTOR, "button.more-options-button[action='more-options']")
            if el.is_displayed()
        ]

    def click_menu_remove(self):
        self.wait.until(EC.element_to_be_clickable(self._menu_remove_item_locator))
        self.find_element(*self._menu_remove_item_locator).click()

    def click_menu_report(self):
        self.wait.until(EC.element_to_be_clickable(self._menu_report_item_locator))
        self.find_element(*self._menu_report_item_locator).click()

    def click_undo_remove(self):
        self.wait.until(EC.element_to_be_clickable(self._undo_remove_button_locator))
        self.find_element(*self._undo_remove_button_locator).click()

    class AddonCards(Region):
        _theme_image_locator = (By.CLASS_NAME, "card-heading-image")
        _extension_icon_locator = (By.CLASS_NAME, "card-heading-icon")
        _disco_addon_name_locator = (By.CLASS_NAME, "disco-addon-name")
        _disco_addon_author_locator = (By.CSS_SELECTOR, ".disco-addon-author a")
        _extension_summary_locator = (By.CLASS_NAME, "disco-description-main")
        _extension_rating_locator = (
            By.CSS_SELECTOR,
            ".disco-description-statistics moz-five-star",
        )
        _extension_users_count_locator = (By.CLASS_NAME, "disco-user-count")
        _addon_install_button_locator = (
            By.CSS_SELECTOR,
            'button[action="install-addon"]',
        )

        def is_extension_card(self):
            """Determines if we have an extension of a theme card.
            If it is a Theme, we return false"""
            try:
                # this statement returns true if the card has an extension
                return self.disco_extension_rating.is_displayed()
            except NoSuchElementException:
                return False

        @property
        def theme_image(self):
            self.wait.until(EC.visibility_of_element_located(self._theme_image_locator))
            return self.find_element(*self._theme_image_locator)

        @property
        def extension_image(self):
            return self.find_element(*self._extension_icon_locator)

        @property
        def disco_addon_name(self):
            self.wait.until(
                EC.visibility_of_element_located(self._disco_addon_name_locator)
            )
            return self.find_element(*self._disco_addon_name_locator)

        @property
        def disco_addon_author(self):
            self.wait.until(
                EC.visibility_of_element_located(self._disco_addon_author_locator)
            )
            return self.find_element(*self._disco_addon_author_locator)

        def click_disco_addon_author(self):
            self.disco_addon_author.click()
            self.wait.until(
                EC.number_of_windows_to_be(2),
                message=f"Number of windows was {len(self.driver.window_handles)}, expected 2",
            )
            self.driver.switch_to.window(self.driver.window_handles[1])
            from pages.desktop.frontend.details import Detail

            return Detail(self.driver, self.page.base_url)

        @property
        def disco_extension_summary(self):
            self.wait.until(
                EC.visibility_of_element_located(self._extension_summary_locator)
            )
            return self.find_element(*self._extension_summary_locator).text

        @property
        def disco_extension_rating(self):
            self.wait.until(
                EC.visibility_of_element_located(self._extension_rating_locator)
            )
            return self.find_element(*self._extension_rating_locator)

        @property
        def rating_score(self):
            return self.disco_extension_rating.get_attribute("rating")

        @property
        def disco_extension_users(self):
            self.wait.until(
                EC.visibility_of_element_located(self._extension_users_count_locator)
            )
            return self.find_element(*self._extension_users_count_locator)

        @property
        def user_count(self):
            return int(
                self.disco_extension_users.text.replace("Users: ", "").replace(",", "")
            )

        @property
        def install_button(self):
            self.wait.until(
                EC.visibility_of_element_located(self._addon_install_button_locator)
            )
            return self.find_element(*self._addon_install_button_locator)
