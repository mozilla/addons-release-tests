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
