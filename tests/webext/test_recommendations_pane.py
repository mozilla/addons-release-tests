import pytest
import time

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException

from pages.desktop.about_addons import AboutAddons
from pages.desktop.frontend.versions import Versions
from pages.desktop.toolbar.toolbar import Toolbar

@pytest.mark.webext
def test_install_addon_from_recommendations_pane_TC_ID_C617016(selenium, base_url, firefox, firefox_notifications, variables, wait):
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium, base_url).wait_for_page_to_load()
    addon_name = about_addons.addon_cards_items[1].disco_addon_name.text
    addon_author = about_addons.addon_cards_items[1].disco_addon_author.text
    about_addons.addon_cards_items[1].install_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    if len(selenium.window_handles) == 2:
        selenium.switch_to.window(selenium.window_handles[0])




