import pytest

from pages.desktop.details import Detail


@pytest.mark.desktop_only
@pytest.mark.nondestructive
@pytest.mark.parametrize('addon_type, name_type', [
    ['flagfox', 'Flagfox'],
    ['green-floral', 'Green Floral'],
    ['langpack-test', 'Acholi (UG) Language Pack'],
    ['dictionary-release-test', 'Dictionary webextension']
])
def test_addon_install(base_url, selenium, firefox, firefox_notifications, addon_type, name_type):
    """Test that navigates to an addon and installs it."""
    selenium.get('{}/addon/{}'.format(base_url, addon_type))
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


