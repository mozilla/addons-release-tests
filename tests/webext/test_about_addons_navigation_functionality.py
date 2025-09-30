import pytest
import time

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

from pages.desktop.about_addons import AboutAddons
from pages.desktop.frontend.versions import Versions
from pages.desktop.toolbar.toolbar import Toolbar


# @pytest.mark.webext
# @pytest.mark.prod
# def test_addons_manager_search_C617019(selenium, base_url, variables):
#     selenium.get("about:addons")
#     about_addons_page = AboutAddons(selenium, base_url).wait_for_page_to_load()
#     # about_addons_page.click_extensions_side_button_no_addon()
#     about_addons_page.search_box("privacy")

@pytest.mark.webext
# @pytest.mark.prod
def test_addons_manager_through_manage_extensions_C617024(selenium, base_url, variables):
    selenium.get(f"{base_url}")
    about_addons_page = Toolbar(selenium, base_url).click_manage_extension_button_no_addon()
    # about_addons_page.assert_recommendations_page()
    about_addons_page.click_extensions_side_button_no_addon()
    about_addons_page.click_themes_side_button()
    about_addons_page.click_plugins_side_button()


# @pytest.mark.webext
# def test_enable_disable_options_work_through_keyboard_shortcuts_C617046(selenium, base_url, wait, firefox, firefox_notifications):
#     """Check if the Enable/Disable options for an extension work in the extension’s detail page via keyboard shortcuts"""
#     selenium.get("about:addons")
#     """Add-ons Manager is loaded."""
#     about_addons = AboutAddons(selenium).wait_for_page_to_load()
#     """Install an addon in order to have data to test"""
#     wait.until(
#         lambda _: len([el.install_button for el in about_addons.addon_cards_items]) >= 7
#     )
#     addon_name = about_addons.addon_cards_items[2].disco_addon_name.text
#     addon_author = about_addons.addon_cards_items[2].disco_addon_author.text
#     about_addons.addon_cards_items[2].install_button.click()
#     firefox.browser.wait_for_notification(
#         firefox_notifications.AddOnInstallConfirmation
#     ).install()
#     firefox.browser.wait_for_notification(
#         firefox_notifications.AddOnInstallComplete
#     ).close()
#     """Select the Extensions panel"""
#     about_addons.click_extensions_side_button()
#     """The list with installed extensions page is loaded without any display or layout issues."""
#     extension_details = about_addons.click_addon_name()
#     assert addon_name in extension_details.addon_name()
#     assert addon_author in extension_details.addon_author()
#     extension_details.assert_extension_detail_rows()







