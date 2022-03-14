import pytest

from pages.desktop.frontend.home import Home
from pages.desktop.frontend.login import Login


@pytest.mark.sanity
@pytest.mark.serial
def test_create_submissions_user_session(selenium, base_url):
    """Create a user session to be used in subsequent tests"""
    Home(selenium, base_url).open().wait_for_page_to_load()
    login = Login(selenium, base_url)
    login.get_session_cookie('submissions_user')


# TODO: tests covering addon submissions will be added here


# These last parts handle the session cookie invalidation and user file deletion
@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.user_data('submissions_user')
def test_clear_submission_session(base_url, selenium, set_session_cookie):
    """Logout to invalidate session cookie"""
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.logout()


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.user_data('submissions_user')
def test_destroy_file(destroy_file):
    """Destroy user session file and verify that it was deleted"""
    with pytest.raises(FileNotFoundError):
        with open('submissions_user.txt', 'r') as file:
            file.read()
