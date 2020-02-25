import pytest

from pages.desktop.details import Detail
from variables import TestData


@pytest.fixture(params=TestData.addon_type_install)
def get_addon_type(request):
    return request.param


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_addon_install(base_url, selenium, firefox, firefox_notifications, get_addon_type):
    """Test that navigates to an addon and installs it."""
    selenium.get('{}/addon/{}'.format(base_url, get_addon_type['addon_type']))
    addon_title = selenium.title
    addon = Detail(selenium, base_url)
    assert get_addon_type['name_type'] in addon.name
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
    # The following if conditions validates that he add-on was uninstalled successfully
    # by inspecting the install button state
    if 'Extension' in addon_title or 'Language Pack' in addon_title or 'Dictionary' in addon_title:
        assert 'Add to Firefox' in addon.button_text
    else:
        assert 'Install Theme' in addon.button_text
