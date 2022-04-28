import pytest

from pages.desktop.developers.devhub_home import DevHubHome


@pytest.mark.sanity
@pytest.mark.serial
# The first test starts the browser with a normal login in order to store de session cookie
@pytest.mark.login('submissions_user')
def test_submit_unlisted_addon(selenium, base_url, variables, wait):
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    submit_addon = page.click_submit_addon_button()
    # start the upload for an unlisted addon
    submit_addon.select_unlisted_option()
    submit_addon.click_continue()
    # checking that the Firefox compatibility checkbox is selected by default
    wait.until(lambda _: submit_addon.firefox_compat_checkbox.is_selected())
    # select an addon to upload
    submit_addon.upload_addon('unlisted-addon.zip')
    submit_addon.is_validation_successful()
    assert submit_addon.success_validation_message.is_displayed()
    # on submit source code page, select 'No' as we do not test source code upload here
    source = submit_addon.click_continue_upload_button()
    source.select_no_to_omit_source()
    confirmation_page = source.continue_unlisted_submission()
    assert (
        variables['unlisted_submission_confirmation']
        in confirmation_page.submission_confirmation_messages[0].text
    )
    manage_addons = confirmation_page.click_manage_listing_button()
    manage_addons.sort_by_created()
    # checking that the latest add-on created is the one just submitted
    wait.until(lambda _: 'Unlisted-addon-auto' in manage_addons.addon_list[0].name)


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.create_session(
    'submissions_user'
)  # starts the browser with an active session (no login needed)
def test_submit_mixed_addon_versions(selenium, base_url, variables, wait):
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # TODO: add steps for submitting addon new version


# TODO: more tests that use @pytest.mark.create_session go here


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.create_session('submissions_user')
@pytest.mark.clear_session
def test_delete_all_extensions(selenium, base_url):
    """This test will delete all the extensions submitted above to make sure
    we can start over with this user in the following runs and also for
    verifying that the addon deletion process functions correctly"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    manage_addons = page.click_my_addons_header_link()
    # run the delete steps until all the addons are cleared from the list
    while len(manage_addons.addon_list) > 0:
        addon = manage_addons.addon_list[0]
        edit = addon.click_addon_name()
        manage = edit.click_manage_versions_link()
        delete = manage.delete_addon()
        delete.input_delete_confirmation_string()
        delete.confirm_delete_addon()
