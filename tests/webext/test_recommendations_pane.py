import pytest
import time

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException

from pages.desktop.about_addons import AboutAddons
from pages.desktop.frontend.versions import Versions
from pages.desktop.toolbar.toolbar import Toolbar

@pytest.mark.webext
def test_install_addon_from_recommendations_pane_TC_ID_C617016(selenium, base_url, firefox, firefox_notifications, wait):
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium, base_url).wait_for_page_to_load()
    about_addons.click_recommendations_side_button()
    addon_name = about_addons.addon_cards_items[1].disco_addon_name.text
    addon_author = about_addons.addon_cards_items[1].disco_addon_author.text
    """A permission door-hanger is displayed under the left side of the URL bar with 2 buttons: Add and Cancel - 
    check if clicking them performs the corresponding actions i.e. 
    Add - installs add-on; Cancel - cancels the installation process. """
    about_addons.addon_cards_items[1].install_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    if len(selenium.window_handles) == 2:
        selenium.switch_to.window(selenium.window_handles[0])
    about_addons.click_extensions_side_button()
    about_addons.click_more_options_button_addon()
    about_addons.more_options_manage_button.is_displayed()
    about_addons.more_options_remove_button.is_displayed()
    about_addons.more_options_report_button.is_displayed()
    about_addons.more_options_preferences_button.is_displayed()
    about_addons.click_more_options_report_addon()
    selenium.switch_to.window(selenium.window_handles[0])
    """On the left side of the "three dots" menu there's the Disable/Enable toggle button - 
    by default the extension is enabled and the toggle button is switched on and blue. """
    """Click on the button to switch it off - when disabled the (disable) tag will be added next to the extension's title."""
    addon_name_disabled = about_addons.extensions_side_toggle_addon()
    assert "(disabled)" in addon_name_disabled
    """Click again to switch toggle button on and enable the extension."""
    addon_name_enabled = about_addons.extensions_side_toggle_addon()
    assert "(disabled)" not in addon_name_enabled

@pytest.mark.webext
def test_install_theme_from_recommendations_pane_TC_ID_C617017(selenium, base_url, firefox, firefox_notifications, wait):
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium, base_url).wait_for_page_to_load()
    about_addons.click_recommendations_side_button()
    theme_name = about_addons.addon_cards_items[0].disco_addon_name.text
    theme_author = about_addons.addon_cards_items[0].disco_addon_author.text
    about_addons.addon_cards_items[0].install_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    if len(selenium.window_handles) == 2:
        selenium.switch_to.window(selenium.window_handles[0])
    about_addons.click_extensions_side_button()
    about_addons.click_more_options_button_addon()
    about_addons.more_options_manage_button.is_displayed()
    about_addons.more_options_remove_button.is_displayed()
    about_addons.more_options_report_button.is_displayed()
    about_addons.more_options_preferences_button.is_displayed()
    about_addons.click_more_options_report_addon()
    selenium.switch_to.window(selenium.window_handles[0])
    """On the left side of the "three dots" menu there's the Disable/Enable toggle button - 
    by default the extension is enabled and the toggle button is switched on and blue. """
    """Click on the button to switch it off - when disabled the (disable) tag will be added next to the extension's title."""
    theme_name_disabled = about_addons.extensions_side_toggle_addon()
    assert "(disabled)" in theme_name_disabled
    """Click again to switch toggle button on and enable the extension."""
    theme_name_enabled = about_addons.extensions_side_toggle_addon()
    assert "(disabled)" not in theme_name_enabled

@pytest.mark.webext
def test_recommendations_page_layout_TC_ID_C617018(selenium, base_url, wait):
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium, base_url).wait_for_page_to_load()
    about_addons.click_recommendations_side_button()
    assert about_addons.search_box().is_displayed()




