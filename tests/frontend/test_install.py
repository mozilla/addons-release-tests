import time
import pytest

from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException

from pages.desktop.about_addons import AboutAddons
from pages.desktop.frontend.details import Detail
from pages.desktop.frontend.versions import Versions


def test_install_uninstall_extension(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Open an extension detail page, install it and then uninstall it"""
    selenium.get(f'{base_url}/addon/aarafow-molla-mantinch/')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    amo_addon_name = addon.name
    assert amo_addon_name == 'aarafow-molla-mantinch'
    assert addon.is_compatible
    addon.install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    # check that the install button state changed to "Remove"
    assert 'Remove' in addon.button_text
    # open the manage Extensions page in about:addons to verify that the extension was installed correctly
    selenium.switch_to.new_window('tab')
    selenium.get('about:addons')
    about_addons = AboutAddons(selenium).wait_for_page_to_load()
    about_addons.click_extensions_side_button()
    wait.until(lambda _: amo_addon_name == about_addons.installed_addon_name[0].text)
    # go back to the addon detail page on AMO to uninstall the addon
    selenium.switch_to.window(selenium.window_handles[0])
    # reused the 'install()` method although the next step reflects an uninstall action.
    addon.install()
    # check that the install button state changed back to "Add to Firefox"
    wait.until(lambda _: 'Add to Firefox' in addon.button_text)
    # open the manage Extensions page in about:addons to verify that the extension is no longer in the list
    selenium.switch_to.window(selenium.window_handles[1])
    with pytest.raises(IndexError):
        wait.until(
            lambda _: amo_addon_name == about_addons.installed_addon_name[0].text
        )


def test_enable_disable_extension(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Open an extension detail page, install it, disable it from about:addons then enable it back in AMO"""
    selenium.get(f'{base_url}/addon/aarafow-molla-mantinch/')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    # open the manage Extensions page in about:addons and Disable the extension
    selenium.switch_to.new_window('tab')
    selenium.get('about:addons')
    about_addons = AboutAddons(selenium).wait_for_page_to_load()
    about_addons.click_extensions_side_button()
    about_addons.disable_extension()
    # verify that about:addons marks the extension as disabled -  (disabled) appended to addon name
    wait.until(
        lambda _: about_addons.installed_addon_name[0].text
        == 'aarafow-molla-mantinch (disabled)'
    )
    # go back to the addon detail page on AMO to Enable the addon
    selenium.switch_to.window(selenium.window_handles[0])
    assert addon.button_text == 'Enable'
    addon.install()
    # check that the install button state changed back to "Remove"
    wait.until(lambda _: 'Remove' in addon.button_text)
    # open the manage Extensions page in about:addons to verify that the extension was re-enabled
    selenium.switch_to.window(selenium.window_handles[1])
    wait.until(lambda _: about_addons.installed_addon_name[0].text == 'aarafow-molla-mantinch')


def test_install_uninstall_theme(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Open a theme detail page, install it and then uninstall it"""
    selenium.get(f'{base_url}/addon/japanese-tattoo/')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    amo_theme_name = addon.name
    assert amo_theme_name == 'Japanese Tattoo'
    assert addon.is_compatible
    addon.install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    # check that the install button state changed to "Remove"
    assert 'Remove' in addon.button_text
    # open the manage Themes page in about:addons to verify that the theme was installed correctly
    selenium.switch_to.new_window('tab')
    selenium.get('about:addons')
    about_addons = AboutAddons(selenium).wait_for_page_to_load()
    about_addons.click_themes_side_button()
    wait.until(lambda _: amo_theme_name == about_addons.installed_addon_name[0].text)
    # go back to the addon detail page on AMO to uninstall the theme
    selenium.switch_to.window(selenium.window_handles[0])
    # reused the 'install()` method although the next step reflects an uninstall action.
    addon.install()
    # check that the install button state changed back to "Install Theme"
    wait.until(lambda _: 'Install Theme' in addon.button_text)
    # open the manage Themes page in about:addons to verify that the theme is no longer in the list
    selenium.switch_to.window(selenium.window_handles[1])
    assert amo_theme_name not in [el.text for el in about_addons.installed_addon_name]


def test_install_uninstall_dictionary(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Open a dictionary detail page, install it and then uninstall it"""
    selenium.get(f'{base_url}/addon/release_dictionary/')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    amo_dict_name = addon.name
    assert amo_dict_name == 'release dictionary'
    assert addon.is_compatible
    addon.install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    # check that the install button state changed to "Remove"
    assert 'Remove' in addon.button_text
    # open the manage Dictionaries page in about:addons to verify that the dictionary was installed correctly
    selenium.switch_to.new_window('tab')
    selenium.get('about:addons')
    about_addons = AboutAddons(selenium).wait_for_page_to_load()
    about_addons.click_dictionaries_side_button()
    wait.until(lambda _: amo_dict_name == about_addons.installed_addon_name[0].text)
    # go back to the addon detail page on AMO to uninstall the dictionary
    selenium.switch_to.window(selenium.window_handles[0])
    # reused the 'install()` method although the next step reflects an uninstall action.
    addon.install()
    # check that the install button state changed back to "Add to Firefox"
    wait.until(lambda _: 'Add to Firefox' in addon.button_text)
    # open the manage Dictionaries page in about:addons to verify that the dictionary is no longer in the list
    selenium.switch_to.window(selenium.window_handles[1])
    with pytest.raises(IndexError):
        wait.until(lambda _: amo_dict_name == about_addons.installed_addon_name[0].text)


def test_install_uninstall_langpack(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Open a language pack detail page, install it and then uninstall it"""
    selenium.get(f'{base_url}/addon/release-langpack/')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    amo_langpack_name = addon.name
    assert amo_langpack_name == 'Release lang pack'
    assert addon.is_compatible
    addon.install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    # check that the install button state changed to "Remove"
    assert 'Remove' in addon.button_text
    # open the manage Language page in about:addons to verify that the langpack was installed correctly
    selenium.switch_to.new_window('tab')
    selenium.get('about:addons')
    about_addons = AboutAddons(selenium).wait_for_page_to_load()
    about_addons.click_language_side_button()
    wait.until(lambda _: amo_langpack_name == about_addons.installed_addon_name[0].text)
    # go back to the addon detail page on AMO to uninstall the dictionary
    selenium.switch_to.window(selenium.window_handles[0])
    # reused the 'install()` method although the next step reflects an uninstall action.
    addon.install()
    # check that the install button state changed back to "Add to Firefox"
    wait.until(lambda _: 'Add to Firefox' in addon.button_text)
    # open the manage Language page in about:addons to verify that the langpack is no longer in the list
    selenium.switch_to.window(selenium.window_handles[1])
    with pytest.raises(IndexError):
        wait.until(
            lambda _: amo_langpack_name == about_addons.installed_addon_name[0].text
        )


def test_about_addons_install_extension(
    selenium, base_url, wait, firefox, firefox_notifications
):
    selenium.get('about:addons')
    about_addons = AboutAddons(selenium)
    # waiting for the addon cards data to be retrieved (the install buttons in this case)
    wait.until(
        lambda _: len([el.install_button for el in about_addons.addon_cards_items]) >= 8
    )
    disco_addon_name = about_addons.addon_cards_items[1].disco_addon_name.text
    disco_addon_author = about_addons.addon_cards_items[1].disco_addon_author.text
    # install the recommended extension
    about_addons.addon_cards_items[1].install_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    time.sleep(2)
    # some addons will open support pages in new tabs after installation;
    # we need to return to the first (about:addons) tab if that happens
    if len(selenium.window_handles) > 1:
        selenium.switch_to.window(selenium.window_handles[0])
    # open the manage Extensions page to verify that the addon was installed correctly
    about_addons.click_extensions_side_button()
    # verify that the extension installed is present in manage Extensions; if the names
    # don't match (which happens sometimes due to differences between AMO names and manifest
    # names), check that the add-on author is the same as an alternative check;
    try:
        assert disco_addon_name in [el.text for el in about_addons.installed_addon_name]
    except AssertionError:
        about_addons.installed_addon_cards[0].click()
        wait.until(
            lambda _: disco_addon_author == about_addons.installed_addon_author_name
        )


def test_about_addons_install_theme(
    selenium, base_url, wait, firefox, firefox_notifications
):
    selenium.get('about:addons')
    about_addons = AboutAddons(selenium)
    # waiting for the addon cards data to be retrieved (the install buttons in this case)
    wait.until(
        lambda _: len([el.install_button for el in about_addons.addon_cards_items]) >= 8
    )
    disco_theme_name = about_addons.addon_cards_items[0].disco_addon_name.text
    # make a note of the image source of the theme we are about to install
    disco_theme_image = about_addons.addon_cards_items[0].theme_image.get_attribute(
        'src'
    )
    # install the recommended theme
    about_addons.addon_cards_items[0].install_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    about_addons.click_themes_side_button()
    # check that installed theme should be first on the manage Themes page
    assert disco_theme_name in about_addons.installed_addon_name[0].text
    assert 'true' in about_addons.enabled_theme_active_status


@pytest.mark.sanity
def test_about_addons_extension_updates(
    selenium, base_url, wait, firefox, firefox_notifications, variables
):
    """Install an addon from AMO and check for updates in addons manager;
    this test is set up to be able to run on each AMO environment"""
    extension = variables['extension_version_updates']
    selenium.get(f'{base_url}/addon/{extension}/versions/')
    versions = Versions(selenium, base_url).wait_for_page_to_load()
    # make a note of the latest version number - this should be visible once the addon updates
    latest_version = versions.latest_version_number
    # install an older version of the addon
    versions.versions_list[1].click_download_link()
    # if the addon is installed from dev or stage we might need to confirm the site security
    # in order to be able to install the addon; the following exception accounts for that
    try:
        firefox.browser.wait_for_notification(
            firefox_notifications.AddOnInstallConfirmation
        ).install()
    except TimeoutException as error:
        # check that the timeout message is raised by the AddOnInstallConfirmation class
        assert error.msg == 'AddOnInstallConfirmation was not shown.'
        firefox.browser.wait_for_notification(
            firefox_notifications.AddOnInstallBlocked
        ).allow()
        firefox.browser.wait_for_notification(
            firefox_notifications.AddOnInstallConfirmation
        ).install()
    # go to addons manager and locate the installed addon
    selenium.get('about:addons')
    about_addons = AboutAddons(selenium)
    about_addons.click_extensions_side_button()
    about_addons.installed_addon_cards[0].click()
    # trigger a manual update check to receive the latest addon version
    about_addons.click_options_button()
    action = ActionChains(selenium)
    action.send_keys('c').perform()
    # compare the updated version to the latest version from AMO and make sure they match
    wait.until(
        lambda _: latest_version == about_addons.installed_version_number,
        message=f'Latest version from AMO "{latest_version}" did not match updated version from addons manager '
        f'"{about_addons.installed_version_number}"',
    )
