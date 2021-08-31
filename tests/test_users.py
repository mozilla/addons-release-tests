import pytest

from pages.desktop.home import Home


@pytest.mark.nondestructive
def test_login(selenium, base_url):
    page = Home(selenium, base_url).open()
    user = 'regular_user'
    page.login(user)
    assert user in page.header.user_display_name.text


@pytest.mark.nondestructive
def test_logout(base_url, selenium):
    """User can logout"""
    page = Home(selenium, base_url).open()
    user = 'regular_user'
    page.login(user)
    page.logout()
    assert not page.logged_in


@pytest.mark.nondestructive
def test_user_menu_collections_link(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.login('regular_user')
    # clicks on View My Collections in the user menu
    # and checks that the user collections page opens
    page.header.click_user_menu_collections_link()


@pytest.mark.nondestructive
def test_user_menu_view_profile(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.login('regular_user')
    # clicks on View Profile in the user menu and checks that the correct page opens
    page.header.click_user_menu_view_profile()


@pytest.mark.nondestructive
def test_user_menu_edit_profile(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.login('regular_user')
    # clicks on Edit Profile in the user menu and checks that the correct page opens
    page.header.click_user_menu_edit_profile()


@pytest.mark.nondestructive
def test_user_menu_devhub_links(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.login('developer')
    count = 0
    # there are 3 links pointing to DevHub pages in the user menu;
    # clicking through each of those links and checking that the correct page opens
    while count < 3:
        page.header.click_user_menu_devhub_links(count)
        # returning to the homepage to select the next link
        selenium.back()
        # waiting for the homepage o reload
        page.wait_for_page_to_load()
        count += 1
