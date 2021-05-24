import pytest

from pages.desktop.home import Home

# There was a bug introduced in FxA with the latest Nightly which breaks the
# email input field - see details in https://github.com/mozilla/fxa/issues/8658


@pytest.mark.skip(reason="Skipping because of an FxA bug")
@pytest.mark.nondestructive
def test_login(selenium, base_url):
    page = Home(selenium, base_url).open()
    user = 'regular_user'
    page.login(user)
    assert user in page.header.user_display_name.text


@pytest.mark.skip(reason="Skipping because of an FxA bug")
@pytest.mark.nondestructive
def test_logout(base_url, selenium):
    """User can logout"""
    page = Home(selenium, base_url).open()
    user = 'regular_user'
    page.login(user)
    page.logout()
    assert not page.logged_in
