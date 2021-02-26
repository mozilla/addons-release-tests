import pytest

from pages.desktop.details import Detail


@pytest.mark.nondestructive
def test_lower_firefox_incompatibility(selenium, base_url, variables):
    extension = variables['lower_firefox_version']
    selenium.get('{}/addon/{}'.format(base_url, extension))
    addon = Detail(selenium, base_url)
    assert 'This add-on is not compatible with your version of Firefox.' \
           in addon.incompatibility_message
    assert addon.button_state_disabled


@pytest.mark.nondestructive
def test_higher_firefox_incompatibility(selenium, base_url, variables):
    extension = variables['higher_firefox_version']
    selenium.get('{}/addon/{}'.format(base_url, extension))
    addon = Detail(selenium, base_url)
    assert 'This add-on requires a newer version of Firefox' \
           in addon.incompatibility_message
    assert addon.button_state_disabled


@pytest.mark.nondestructive
def test_platform_incompatibility(selenium, base_url, variables):
    extension = variables['incompatible_platform']
    selenium.get('{}/addon/{}'.format(base_url, extension))
    addon = Detail(selenium, base_url)
    assert 'This add-on is not available on your platform.' \
           in addon.incompatibility_message
    assert addon.button_state_disabled
