import pytest
import time

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException

from pages.desktop.about_addons import AboutAddons
from pages.desktop.frontend.versions import Versions
from pages.desktop.toolbar.toolbar import Toolbar


@pytest.mark.webext
@pytest.mark.skip
def test_verify_if_the_extension_is_installed_from_extensions_section_C617037(selenium, base_url, firefox, firefox_notifications, variables):
    """Install addon in order to have data to test with"""
    selenium.get(variables["addon_version_update_webext"])
    versions_page = Versions(selenium, base_url).wait_for_page_to_load()
    versions_page.versions_list[1].click_download_link()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    """Installation is completed successfully"""
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    toolbar_section = Toolbar(selenium, base_url)
    """In browser select “Menu” (hamburger icon) from the top right of the page."""
    """A pop-up menu is displayed with several options."""
    toolbar_section.click_panel_ui_menu()
    """From the menu select “Add-ons” option."""
    """The “Add-ons Manager” page is loaded without any display or layout issues."""
    about_addons = toolbar_section.click_panel_ui_extensions_and_themes()
    """Select “Extensions” from the left side menu."""
    """The list with installed extensions page is loaded without any display or layout issues."""
    about_addons.click_extensions_side_button()

@pytest.mark.webext
def test_remove_extension_from_about_addons(selenium, base_url, firefox, firefox_notifications, variables):
    selenium.get(variables["addon_version_update_webext"])
    versions_page = Versions(selenium, base_url).wait_for_page_to_load()
    versions_page.versions_list[1].click_download_link()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    """Installation is completed successfully"""
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    toolbar_section = Toolbar(selenium, base_url)
    """In browser select “Menu” (hamburger icon) from the top right of the page."""
    """A pop-up menu is displayed with several options."""
    toolbar_section.click_panel_ui_menu()
    """From the menu select “Add-ons” option."""
    """The “Add-ons Manager” page is loaded without any display or layout issues."""
    about_addons = toolbar_section.click_panel_ui_extensions_and_themes()
    about_addons.click_extensions_side_button()
    about_addons.click_more_options_button_addon()
    about_addons.click_more_options_remove_addon()

