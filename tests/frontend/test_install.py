import time
import pytest

from pages.desktop.about_addons import AboutAddons
from pages.desktop.frontend.details import Detail


def test_install_uninstall_extension(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Open an extension detail page, install it and then uninstall it"""
    selenium.get(f'{base_url}/addon/bloody-vikings/')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    amo_addon_name = addon.name
    assert amo_addon_name == 'Bloody Vikings!'
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
    selenium.get(f'{base_url}/addon/bloody-vikings/')
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
        == 'Bloody Vikings! (disabled)'
    )
    # go back to the addon detail page on AMO to Enable the addon
    selenium.switch_to.window(selenium.window_handles[0])
    assert addon.button_text == 'Enable'
    addon.install()
    # check that the install button state changed back to "Remove"
    wait.until(lambda _: 'Remove' in addon.button_text)
    # open the manage Extensions page in about:addons to verify that the extension was re-enabled
    selenium.switch_to.window(selenium.window_handles[1])
    wait.until(lambda _: about_addons.installed_addon_name[0].text == 'Bloody Vikings!')


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
