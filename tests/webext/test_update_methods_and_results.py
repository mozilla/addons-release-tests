import pytest
import time

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException

from pages.desktop.about_addons import AboutAddons
from pages.desktop.frontend.versions import Versions


# @pytest.mark.webext
@pytest.mark.prod
def test_addon_version_check_in_addons_manager_C617022_and_C1770375(selenium, base_url, wait, firefox, firefox_notifications, variables):
    """Test Cases: - https://mozilla.testrail.io/index.php?/cases/view/1770375
                   - https://mozilla.testrail.io/index.php?/cases/view/617022"""
    """Open the All versions page for any of the following add-ons:"""
    """ https://addons.allizom.org/en-US/firefox/addon/worldwide-radio/versions/
        https://addons.allizom.org/en-US/firefox/addon/bloody-vikings/versions/
        https://addons.allizom.org/en-US/firefox/addon/listed-vers/versions/
        https://addons.allizom.org/en-US/firefox/addon/bitwarden-password-manager/versions/
        Install one of the previous versions of these add-ons (not the latest version)"""
    selenium.get(variables["addon_version_update_webext"])
    versions_page = Versions(selenium, base_url).wait_for_page_to_load()
    latest_version_number = versions_page.latest_version_number
    older_version_number = versions_page.versions_list[1].version_number
    versions_page.versions_list[1].click_download_link()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    """Installation is completed successfully"""
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    """Go to the Manage Extensions page in about:addons, click on options ⚙️ at the top of the page and select Check for updates"""
    selenium.get("about:addons")
    about_addons_page = AboutAddons(selenium, base_url).wait_for_page_to_load()
    about_addons_page.click_extensions_side_button()
    extension_detail_region = about_addons_page.click_addon_name()
    assert older_version_number in extension_detail_region.addon_detail_version_number()
    """The update process starts and once it is successfully finished a confirmation message is displayed next to the Options ⚙️"""
    about_addons_page.click_options_button()
    action = ActionChains(selenium)
    action.send_keys("c").perform()
    assert variables["addon_version_updated_message"] in extension_detail_region.updates_message()
    assert latest_version_number in extension_detail_region.addon_detail_version_number()

