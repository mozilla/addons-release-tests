import time

from pypom import Page, Region

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.about_debug_addons import AboutDebug
from pages.desktop.view_recent_updates import ViewRecentUpdates


class AboutAddons(Page):
    _addon_cards_locator = (By.CLASS_NAME, "card.addon")
    _addon_card_general_locator = (By.CSS_SELECTOR, ".card.addon")
    _search_box_locator = (By.CSS_SELECTOR, ".main-search search-textbox")
    _find_more_addons_search_box_locator = (By.CSS_SELECTOR, "moz-input-search[placeholder='Search addons.mozilla.org']")
    _find_more_addons_text_locator = (By.CSS_SELECTOR, ".search-label")
    # Side-tab buttons — recent Firefox versions render them as
    # `moz-page-nav-button` instead of legacy `button[name=...]`. Selecting
    # the `id` works for both shapes.
    _extension_tab_button_locator = (By.CSS_SELECTOR, "#category-extension")
    _recommendations_tab_button_locator = (By.CSS_SELECTOR, "#category-discover")
    _recommendations_tab_addon_list_locator = (By.CSS_SELECTOR, "card addon")
    _recommendations_tab_find_more_addons_locator = (By.CSS_SELECTOR, "button.primary")
    _theme_tab_button_locator = (By.CSS_SELECTOR, "#category-theme")
    _plugins_tab_button_locator = (By.CSS_SELECTOR, "#category-plugin")
    _dictionary_tab_button_locator = (By.CSS_SELECTOR, "#category-dictionary")
    _langpack_tab_button_locator = (By.CSS_SELECTOR, "#category-locale")
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
    _options_button_locator = (By.CSS_SELECTOR, ".more-options-button")
    # In current Firefox the three-dot trigger is a `<moz-button>`, not a
    # plain `<button>`. There are also `.more-options-button` triggers at the
    # page level (the "Tools for all add-ons" gear) and one per addon-card —
    # scope to `addon-card` so we don't accidentally click the page gear.
    _more_options_button_locator = (By.CSS_SELECTOR, "addon-card .more-options-button")
    _panel_item_action_debug_addons = (By.XPATH, "//panel-item[@action='debug-addons']")
    _panel_item_action_view_recent_updates_locator = (By.XPATH, "//panel-item[@action='view-recent-updates']")
    _remove_addon_dialog_locator = (By.ID, "commonDialog")
    # Every addon-card renders its own `panel-list` with the same set of
    # `panel-item[action='…']` entries, so an unscoped selector returns the
    # *first* one in document order — which is hidden until that specific
    # panel is opened. Scope to `panel-list[open]` so we only resolve items
    # inside the panel that is actually showing.
    _more_options_panel_item_remove_button_locator = (By.CSS_SELECTOR, "panel-list[open] panel-item[action='remove']")
    _more_options_panel_item_preferences_locator = (By.CSS_SELECTOR, "panel-list[open] panel-item[action='preferences']")
    _more_options_panel_item_report_locator = (By.CSS_SELECTOR, "panel-list[open] panel-item[action='report']")
    _more_options_panel_item_manage_locator = (By.CSS_SELECTOR, "panel-list[open] panel-item[action='expand']")
    _extensions_side_toggle_addon_locator = (By.CSS_SELECTOR, "moz-toggle[class='extension-enable-button']")
    _extensions_side_addon_name_link_locator = (By.CSS_SELECTOR, "a[class='addon-name-link']")
    # the undo control on the pending-uninstall message bar — Firefox has used a few
    # different attribute combinations over time, so we match either form
    _undo_remove_addon_button_locator = (
        By.CSS_SELECTOR,
        "button[data-l10n-id='pending-uninstall-undo-button'], button[action='undo']",
    )
    _firefox_recommends_link_locator = (By.CSS_SELECTOR, "a[class='discopane-intro-learn-more-link']")
    _recommends_link_header_text_locator = (
        By.XPATH,
        "//h1[contains(text(), 'Recommended Extensions program')]",
    )
    _personalized_recommendations_link_locator = (
        By.CSS_SELECTOR,
        "a[href*='personalized-extension-recommendations']",
    )
    _personalized_recommendations_header_locator = (
        By.XPATH,
        "//h1[contains(text(), 'Personalized')]",
    )
    _privacy_policy_link_locator = (
        By.CSS_SELECTOR,
        "a[href*='privacy/firefox']",
    )

    def wait_for_page_to_load(self):
        self.wait.until(
            EC.visibility_of_element_located(self._addon_card_general_locator)
        )
        return self

    @property
    def more_options_remove_button(self):
        self.wait.until(
            EC.visibility_of_element_located(self._more_options_panel_item_remove_button_locator)
        )
        return self.find_element(*self._more_options_panel_item_remove_button_locator)

    @property
    def more_options_preferences_button(self):
        self.wait.until(
            EC.visibility_of_element_located(self._more_options_panel_item_preferences_locator)
        )
        return self.find_element(*self._more_options_panel_item_preferences_locator)

    @property
    def more_options_report_button(self):
        self.wait.until(
            EC.visibility_of_element_located(self._more_options_panel_item_report_locator)
        )
        return self.find_element(*self._more_options_panel_item_report_locator)

    @property
    def more_options_manage_button(self):
        self.wait.until(
            EC.visibility_of_element_located(self._more_options_panel_item_manage_locator)
        )
        return self.find_element(*self._more_options_panel_item_manage_locator)

    @property
    def recommends_link_header_text(self):
        self.wait.until(
            EC.visibility_of_element_located(self._recommends_link_header_text_locator)
        )
        return self.find_element(*self._recommends_link_header_text_locator)


    def click_more_options_button_addon(self):
        self.wait.until(
            EC.visibility_of_element_located(self._more_options_button_locator)
        )
        self.find_element(*self._more_options_button_locator).click()

    def click_more_options_remove_addon(self):
        self.wait.until(
            EC.visibility_of_element_located(self._more_options_panel_item_remove_button_locator)
        )
        self.find_element(*self._more_options_panel_item_remove_button_locator).click()

    def click_more_options_report_addon(self):
        self.wait.until(
            EC.visibility_of_element_located(self._more_options_panel_item_report_locator)
        )
        self.find_element(*self._more_options_panel_item_report_locator).click()
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.wait.until(EC.url_contains("/firefox/feedback/addon"))

    def extensions_side_toggle_addon(self):
        self.wait.until(
            EC.visibility_of_element_located(self._extensions_side_toggle_addon_locator)
        )
        self.find_element(*self._extensions_side_toggle_addon_locator).click()
        time.sleep(2)
        return self.find_element(*self._extensions_side_addon_name_link_locator).text

    @property
    def undo_remove_button(self):
        self.wait.until(
            EC.visibility_of_element_located(self._undo_remove_addon_button_locator)
        )
        return self.find_element(*self._undo_remove_addon_button_locator)

    def click_undo_remove(self):
        self.undo_remove_button.click()
        # the message bar disappears after Undo and the addon name link reappears
        self.wait.until(
            EC.visibility_of_element_located(self._extensions_side_addon_name_link_locator)
        )


    # def click_more_options_remove_addon(self):
    #     with self.driver.context(self.driver.CONTEXT_CHROME):
    #         el = self.driver.execute_script("""
    #                         return document.querySelector('panel-item[action="remove"]');
    #                     """)
    #         el.click()

    def click_panel_item_action_debug_addon(self):
        # with self.driver.context(self.driver.CONTEXT_CHROME):
        el = self.driver.execute_script("""
                return document.querySelector('panel-item[action="debug-addons"]');
            """)
        el.click()
        return AboutDebug(self.driver, self.base_url).wait_for_page_to_load()

    def click_panel_item_action_check_for_updates(self):
        el = self.driver.execute_script("""
            return document.querySelector('panel-item[action="view-recent-updates"]');
        """)
        el.click()
        return ViewRecentUpdates(self.driver, self.base_url).wait_for_page_to_load()

    def _click_options_menu_action(self, action):
        """Click an Options-menu panel-item by its `action` attribute."""
        el = self.driver.execute_script(
            "return document.querySelector(arguments[0]);",
            f'panel-item[action="{action}"]',
        )
        if el is None:
            raise NoSuchElementException(f"panel-item[action='{action}']")
        el.click()

    def click_view_recent_updates(self):
        """Open the Options menu's "View Recent Updates" entry."""
        self._click_options_menu_action("view-recent-updates")
        return ViewRecentUpdates(self.driver, self.base_url).wait_for_page_to_load()

    def click_check_for_updates(self):
        """Trigger an addon update check via the Options menu."""
        self._click_options_menu_action("check-for-updates")

    def click_install_addon_from_file(self):
        """Click the Options menu's "Install Add-on From File…" entry. The
        native file picker that this opens is owned by the OS and cannot be
        driven from a content-context Selenium session — callers must handle
        the picker via Marionette's chrome context (or skip the assertion)."""
        self._click_options_menu_action("install-from-file")

    def click_manage_shortcuts(self):
        """Open the Options menu's "Manage Extension Shortcuts" entry."""
        self._click_options_menu_action("manage-shortcuts")

    def assert_recommendations_page(self):
        """Assert list of addons"""
        self.wait.until(
            EC.visibility_of_element_located(self._recommendations_tab_addon_list_locator)
        )
        addon_cards = self.find_elements(*self._recommendations_tab_addon_list_locator)
        assert len(addon_cards) == 7, f"Expected 7 addon cards, got {len(addon_cards)}"
        self.wait.until(
            EC.visibility_of_element_located(self._recommendations_tab_find_more_addons_locator)
        )
        find_more_addons = self.find_element(*self._recommendations_tab_find_more_addons_locator)
        assert find_more_addons.text in "Find more add-ons"

    def remove_addon_dialog(self):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.wait.until(
                EC.visibility_of_element_located(self._remove_addon_dialog_locator)
            )
            el = self.driver.execute_script("""
                        return document.querySelector('button[dlgtype="accept"]');
                    """)
            el.click()

    @property
    def search_box(self):
        self.wait.until(
            EC.visibility_of_element_located(self._find_more_addons_search_box_locator)
        )
        return self.find_element(*self._find_more_addons_search_box_locator)

    @property
    def search_box_element(self):
        # the same moz-input-search element as `search_box` but exposed as a property
        # that does not collide with the `search_box(value)` method overload below
        self.wait.until(
            EC.visibility_of_element_located(self._find_more_addons_search_box_locator)
        )
        return self.find_element(*self._find_more_addons_search_box_locator)

    # def search_box(self, value):
    #     self.wait.until(EC.visibility_of_element_located(self._find_more_addons_search_box_locator))
    #     search_field = self.driver.execute_script(
    #         "return document.querySelector('moz-input-search[placeholder='Search addons.mozilla.org']')"
    #     )
    #     search_field.clear()
    #     search_field.send_keys(value)
    #     actions = ActionChains(self.driver)
    #     actions.send_keys(Keys.TAB)
    #     actions.send_keys(Keys.ENTER)
    #
    #     # AMO search results open in a new tab, so we need to switch windows
    #     self.wait.until(
    #         EC.number_of_windows_to_be(2),
    #         message=f"Number of windows was {len(self.driver.window_handles)}, expected 2",
    #     )
    #     self.driver.switch_to.window(self.driver.window_handles[1])
    #     from pages.desktop.frontend.search import Search
    #
    #     return Search(self.driver, self.base_url).wait_for_page_to_load()

    def search_box(self, value):
        self.wait.until(EC.visibility_of_element_located(self._find_more_addons_search_box_locator))

        host = self.driver.execute_script("""
            return document.querySelector("moz-input-search[placeholder='Search addons.mozilla.org']");
        """)
        input_el = self.driver.execute_script("return arguments[0].shadowRoot?.querySelector('input')", host)

        input_el.clear()
        input_el.send_keys(value)

        btn_host = self.driver.execute_script("""
          return document.querySelector("moz-button[data-l10n-id='addons-heading-search-button']");
        """)

        inner_btn = self.driver.execute_script("""
          const host = arguments[0];
          return host?.shadowRoot?.querySelector("button") || null;
        """, btn_host)

        assert inner_btn, "Inner <button> not found in moz-button shadowRoot"

        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", inner_btn)
        self.driver.execute_script("arguments[0].click();", inner_btn)  # JS click on real button

        ActionChains(self.driver).move_to_element(inner_btn).click().perform()
        ActionChains(self.driver).move_to_element(inner_btn).send_keys(Keys.ENTER).perform()

        self.wait.until(EC.number_of_windows_to_be(2))
        self.driver.switch_to.window(self.driver.window_handles[1])

        from pages.desktop.frontend.search import Search
        return Search(self.driver, self.base_url).wait_for_page_to_load()

    def find_more_addons_search_box(self, value):
        self.wait.until(EC.visibility_of_element_located(self._find_more_addons_search_box_locator))
        search_field = self.driver.execute_script(
            "return document.querySelector('moz-input-search[placeholder='Search addons.mozilla.org']')"
        )
        search_field.send_keys(value)
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

    def click_extensions_side_button_no_addon(self):
        self.wait.until(EC.element_to_be_clickable(self._extension_tab_button_locator))
        self.find_element(*self._extension_tab_button_locator).click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, "header-name"), "Manage Your Extensions"
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

    def click_recommendations_side_button(self):
        self.wait.until(EC.element_to_be_clickable(self._recommendations_tab_button_locator))
        self.find_element(*self._recommendations_tab_button_locator).click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h1[@class='header-name']"), "Personalize Your"
            )
        )

    def click_plugins_side_button(self):
        self.wait.until(EC.element_to_be_clickable(self._plugins_tab_button_locator))
        self.find_element(*self._plugins_tab_button_locator).click()
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
    def find_more_addons_text(self):
        self.wait.until(
            EC.visibility_of_element_located(self._find_more_addons_text_locator)
        )
        return self.find_element(*self._find_more_addons_text_locator).text

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

    def click_options_button(self):
        self.wait.until(EC.element_to_be_clickable(self._options_button_locator))
        self.find_element(*self._options_button_locator).click()

    def click_addon_name(self):
        self.wait.until(EC.element_to_be_clickable(self._installed_addon_name_locator))
        self.find_element(*self._installed_addon_name_locator).click()
        return self.ExtensionDetail(self).wait_for_region_to_load()

    def firefox_recommends_link(self):
        self.wait.until(EC.element_to_be_clickable(self._firefox_recommends_link_locator))
        self.find_element(*self._firefox_recommends_link_locator).click()
        self.wait.until(EC.number_of_windows_to_be(2))
        self.driver.switch_to.window(self.driver.window_handles[1])
        # the SUMO kb article URL is more stable than its h1 text
        self.wait.until(
            EC.url_contains("recommended-extensions-program"),
            message=f"Unexpected URL after clicking recommends link: "
                    f"{self.driver.current_url}",
        )
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def personalized_recommendations_link(self):
        self.wait.until(
            EC.element_to_be_clickable(self._personalized_recommendations_link_locator)
        )
        self.find_element(*self._personalized_recommendations_link_locator).click()
        self.wait.until(EC.number_of_windows_to_be(2))
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.wait.until(
            EC.url_contains("personalized-extension-recommendations"),
            message=f"Unexpected URL after clicking personalized recommendations link: "
                    f"{self.driver.current_url}",
        )
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def privacy_policy_link(self):
        self.wait.until(EC.element_to_be_clickable(self._privacy_policy_link_locator))
        self.find_element(*self._privacy_policy_link_locator).click()
        self.wait.until(EC.number_of_windows_to_be(2))
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.wait.until(
            EC.url_contains("privacy"),
            message=f"Unexpected URL after clicking privacy policy link: "
                    f"{self.driver.current_url}",
        )
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])




    class ExtensionDetail(Region):
        _addon_card_locator = (By.CSS_SELECTOR, "addon-card")
        _addon_name_locator = (By.CLASS_NAME, "addon-name")
        _addon_author_locator = (By.CSS_SELECTOR, ".addon-detail-row-author a")
        _addon_detail_row_updates_locator = (By.CSS_SELECTOR, ".addon-detail-row-updates span")
        _addon_detail_row_private_browsing_locator = (
        By.CSS_SELECTOR, "span[data-l10n-id='detail-private-browsing-label']")
        _addon_detail_version_locator = (By.CSS_SELECTOR, ".addon-detail-row-version label")
        _addon_detail_last_updated_locator = (By.CSS_SELECTOR, ".addon-detail-row-lastUpdated label")
        _addon_detail_rating_locator = (By.CSS_SELECTOR, ".addon-detail-row-rating label")
        _addon_detail_row_version_locator = (By.CSS_SELECTOR, ".addon-detail-row-version")
        _updates_message_locator = (By.ID, "updates-message")

        def wait_for_region_to_load(self):
            self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "addon-card")),
                message="Addon Card region was not loaded",
            )
            return self

        def addon_name(self):
            self.wait.until(
                EC.visibility_of_element_located(self._addon_name_locator)
            )
            return self.find_element(*self._addon_name_locator).text

        def addon_author(self):
            self.wait.until(
                EC.visibility_of_element_located(self._addon_author_locator)
            )
            return self.find_element(*self._addon_author_locator).text

        def addon_detail_updates_locator(self):
            self.wait.until(
                EC.visibility_of_element_located(self._addon_detail_row_updates_locator)
            )
            return self.find_element(*self._addon_detail_row_updates_locator).text

        def addon_detail_private_browsing(self):
            self.wait.until(
                EC.visibility_of_element_located(self._addon_detail_row_private_browsing_locator)
            )
            return self.find_element(*self._addon_detail_row_private_browsing_locator).text

        def addon_detail_version(self):
            self.wait.until(
                EC.visibility_of_element_located(self._addon_detail_version_locator)
            )
            return self.find_element(*self._addon_detail_version_locator).text

        def addon_detail_version_number(self):
            self.wait.until(
                EC.visibility_of_element_located(self._addon_detail_row_version_locator)
            )
            return self.find_element(*self._addon_detail_row_version_locator).text.split()[1]

        def addon_detail_last_updated(self):
            self.wait.until(
                EC.visibility_of_element_located(self._addon_detail_last_updated_locator)
            )
            return self.find_element(*self._addon_detail_last_updated_locator).text

        def addon_detail_rating(self):
            self.wait.until(
                EC.visibility_of_element_located(self._addon_detail_rating_locator)
            )
            return self.find_element(*self._addon_detail_rating_locator).text

        def updates_message(self):
            self.wait.until(
                EC.visibility_of_element_located(self._updates_message_locator)
            )
            self.wait.until(
                lambda d: d.find_element(*self._updates_message_locator).get_attribute("state") == "installed",
                message="Addon did not reach state=installed within timeout"
            )
            return self.find_element(*self._updates_message_locator).text

        def assert_extension_detail_rows(self):
            assert self.addon_detail_updates_locator() in "Allow automatic updates", "Detail Updates Row is not displayed or text has been modified"
            assert self.addon_detail_rating() in "Rating", "Rating Row is not displayed or text has been modified"
            assert self.addon_detail_private_browsing() in "Run in Private Windows", "Private browsing row is not displayed or text has been modified"
            assert self.addon_detail_last_updated() in "Last Updated", "Last updated row is not displayed or text has been modified"
            assert self.addon_detail_version() in "Version", "Version row is not displayed or text has been modified"

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
        _manage_addon_button_locator = (
            By.CSS_SELECTOR,
            "button[action='manage-addon']:not([hidden])",
        )

        def is_extension_card(self):
            """Determines if we have an extension or a theme card.
            Theme cassettes label their install button with
            `data-l10n-id="install-theme-button"`, extensions with
            `data-l10n-id="install-extension-button"`."""
            try:
                btn = self.find_element(*self._addon_install_button_locator)
            except NoSuchElementException:
                return False
            return btn.get_attribute("data-l10n-id") == "install-extension-button"

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

        @property
        def manage_addon_button(self):
            self.wait.until(
                EC.visibility_of_element_located(self._manage_addon_button_locator)
            )
            return self.find_element(*self._manage_addon_button_locator)
