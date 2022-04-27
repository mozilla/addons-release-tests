import pytest

from pages.desktop.developers.devhub_home import DevHubHome


@pytest.mark.sanity
@pytest.mark.serial
# The first test starts the browser with a normal login in order to store de session cookie
@pytest.mark.login('submissions_user')
def test_submit_listed_addon(selenium, base_url, variables, wait):
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # TODO: add steps for submitting listed addon


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.create_session(
    'submissions_user'
)  # starts the browser with an active session (no login needed)
def test_submit_mixed_addon_versions(selenium, base_url, variables, wait):
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # TODO: add steps for submitting addon new version


# TODO: more tests that use @pytest.mark.create_session go here


# This will be the last test in the suite where we also use the clean-up part from the selenium fixture
@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.create_session('submissions_user')
@pytest.mark.clear_session
def test_delete_all_extensions(selenium, base_url):
    """This test will delete all the extensions submitted above to make sure
    we can start over with this user in the following runs and also for
    verifying that the addon deletion process functions correctly"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # TODO: add steps for deleting the user addons
    # once the test steps are complete, the 'clear_session' fixture will handle the clean-up part
