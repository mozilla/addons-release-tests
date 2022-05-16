import time
import pytest

from pages.desktop.about_addons import AboutAddons
from pages.desktop.frontend.details import Detail


@pytest.mark.nondestructive
@pytest.mark.parametrize(
    'addon_type, name_type',
    [
        ['weather-stage', 'Weather Stage'],
        ['japanese-tattoo', 'Japanese Tattoo'],
        ['release-langpack', 'Release Langpack'],
        ['release_dictionary', 'Release Dictionary'],
    ],
)
def test_addon_install(
    base_url, selenium, firefox, firefox_notifications, addon_type, name_type
):
    """Test that navigates to an addon and installs it."""
    selenium.get(f'{base_url}/addon/{addon_type}')
    addon = Detail(selenium, base_url)
    assert name_type in addon.name
    assert addon.is_compatible
    addon.install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    assert 'Remove' in addon.button_text
    # Reused the 'install()` method although the next step reflects an uninstall action.
    addon.install()
    # using a 'try - except AssertionError' method because the install button text is different for Themes.
    try:
        assert 'Add to Firefox' in addon.button_text
    except AssertionError:
        assert 'Install Theme' in addon.button_text


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
