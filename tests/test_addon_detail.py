import pytest

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as expected

from pages.desktop.details import Detail
from pages.desktop.users import User


@pytest.mark.nondestructive
def test_extension_meta_card(selenium, base_url, variables):
    # Checks addon essential data (name, icon, author name, summary)
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    assert variables['detail_extension_name'] in addon.name
    assert addon.addon_icon.is_displayed()
    assert addon.authors.is_displayed()
    assert addon.summary.is_displayed()


@pytest.mark.nondestructive
def test_detail_author_links(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    # read the add-on author name and clicks on it
    addon = Detail(selenium, base_url)
    author = addon.authors.text
    addon.authors.click()
    # verify that the author profile page opens
    user = User(selenium, base_url)
    assert author in user.user_display_name


@pytest.mark.nondestructive
def test_addon_detail_recommended_badge(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    assert addon.promoted_badge.is_displayed()
    assert 'Recommended' in addon.promoted_badge_category
    # checks that the badge redirects to the correct sumo article
    addon.click_promoted_badge()
    assert 'add-on-badges' in selenium.current_url


@pytest.mark.nondestructive
def test_addon_detail_by_firefox_badge(selenium, base_url, variables):
    extension = variables['by_firefox_addon']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    assert addon.promoted_badge.is_displayed()
    assert 'By Firefox' in addon.promoted_badge_category
    # checks that the badge redirects to the correct sumo article
    addon.click_promoted_badge()
    assert 'add-on-badges' in selenium.current_url


@pytest.mark.nondestructive
def test_non_promoted_addon(selenium, base_url, variables):
    extension = variables['experimental_addon']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    # check that the Promoted badge is not displayed
    with pytest.raises(NoSuchElementException):
        selenium.find_element_by_class_name('PromotedBadge-large')
    # checks the presence of an install warning
    assert addon.install_warning.is_displayed()
    assert variables['install_warning_message'] in \
        addon.install_warning_message
    addon.click_install_warning_button()
    assert 'add-on-badges' in selenium.current_url


@pytest.mark.nondestructive
def test_experimental_addon(selenium, base_url, variables):
    extension = variables['experimental_addon']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    assert addon.experimental_badge.is_displayed()


@pytest.mark.nondestructive
def test_lower_firefox_incompatibility(selenium, base_url, variables):
    extension = variables['lower_firefox_version']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    assert 'This add-on is not compatible with your version of Firefox.' \
           in addon.incompatibility_message
    assert addon.button_state_disabled


@pytest.mark.nondestructive
def test_higher_firefox_incompatibility(selenium, base_url, variables):
    extension = variables['higher_firefox_version']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    assert 'This add-on requires a newer version of Firefox' \
           in addon.incompatibility_message
    assert addon.button_state_disabled


@pytest.mark.nondestructive
def test_platform_incompatibility(selenium, base_url, variables):
    extension = variables['incompatible_platform']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    assert 'This add-on is not available on your platform.' \
           in addon.incompatibility_message
    assert addon.button_state_disabled


@pytest.mark.nondestructive
def test_contribute_button(selenium, base_url, variables):
    extension = variables['detail_extension_slug']
    selenium.get(f'{base_url}/addon/{extension}')
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
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url)
    assert 'Permissions' in addon.permissions.permissions_card_header
    permissions = addon.permissions.permissions_list
    # checks that each permission has a corresponding icon and description
    for permission in permissions:
        assert permission.permission_icon.is_displayed()
        assert permission.permission_description.is_displayed()
    addon.permissions.click_permissions_button()
    addon.wait_for_current_url('permission-request')
