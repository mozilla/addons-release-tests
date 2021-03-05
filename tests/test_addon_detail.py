import pytest

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as expected

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


@pytest.mark.nondestructive
def test_contribute_button(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get('{}/addon/{}'.format(base_url, extension))
    addon = Detail(selenium, base_url)
    assert 'Support this developer' in addon.contribute.contribute_card_header
    assert variables['contribute_card_summary'] in\
           addon.contribute.contribute_card_content
    addon.contribute.click_contribute_button()
    # verifies that utm params are passed from AMO to the external contribute site
    wait = WebDriverWait(selenium, 10)
    wait.until(expected.url_contains(variables['contribute_utm_param']))


@pytest.mark.nondestructive
def test_extension_permissions(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get('{}/addon/{}'.format(base_url, extension))
    addon = Detail(selenium, base_url)
    assert 'Permissions' in addon.permissions.permissions_card_header
    permissions = addon.permissions.permissions_list
    # checks that each permission has a corresponding icon and description
    for permission in permissions:
        assert permission.permission_icon.is_displayed()
        assert permission.permission_description.is_displayed()
    addon.permissions.click_permissions_button()
    addon.wait_for_current_url('permission-request')
