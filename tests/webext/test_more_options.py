import pytest
import time

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException

from pages.desktop.about_addons import AboutAddons
from pages.desktop.frontend.versions import Versions
from pages.desktop.toolbar.toolbar import Toolbar


@pytest.mark.webext
@pytest.mark.prod
def test_check_extension_toolbar_menu_options_are_functional_C617050(selenium, base_url, variables, firefox, firefox_notifications, firefox_options):
    selenium.get(variables["addon_version_update_webext"])
    versions_page = Versions(selenium, base_url).wait_for_page_to_load()
    versions_page.versions_list[0].add_to_firefox_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    """Installation is completed successfully"""
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    toolbar = Toolbar(selenium, base_url)
    toolbar.click_toolbar_extension_button()
    about_addons_page = toolbar.click_toolbar_extension_wheel_options_buttons()



