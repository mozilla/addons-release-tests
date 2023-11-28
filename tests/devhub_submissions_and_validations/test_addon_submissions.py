import pytest

from pages.desktop.developers.devhub_home import DevHubHome
from pages.desktop.developers.manage_versions import ManageVersions
from pages.desktop.developers.submit_addon import (
    SubmitAddon,
    SubmissionConfirmationPage,
)
from scripts import reusables
from api import api_helpers


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.addon
# The first test starts the browser with a normal login in order to store de session cookie
@pytest.mark.login("submissions_user")
def test_submit_unlisted_addon_tc_id_c14886(selenium, base_url, variables, wait):
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    submit_addon = page.click_submit_addon_button()
    # start the upload for an unlisted addon
    submit_addon.select_unlisted_option()
    submit_addon.click_continue()
    # select an addon to upload
    submit_addon.upload_addon("unlisted-addon.zip")
    submit_addon.is_validation_successful()
    assert submit_addon.success_validation_message.is_displayed()
    # on submit source code page, select 'No' as we do not test source code upload here
    source = submit_addon.click_continue_upload_button()
    source.select_no_to_omit_source()
    confirmation_page = source.continue_unlisted_submission()
    assert (
            variables["unlisted_submission_confirmation"]
            in confirmation_page.submission_confirmation_messages[0].text
    )
    manage_addons = confirmation_page.click_manage_listing_button()
    manage_addons.sort_by_created()
    # checking that the latest add-on created is the one just submitted
    wait.until(lambda _: "Unlisted-addon-auto" in manage_addons.addon_list[0].name)


@pytest.mark.serial
@pytest.mark.addon
@pytest.mark.create_session("submissions_user")
def test_verify_first_version_autoapproval(selenium, base_url, variables, wait):
    """This test will wait (for max 5 minutes) until the status of an add-on changes to approved"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    my_addons = page.click_my_addons_header_link()
    # open the edit page of the latest listed add-on submitted
    edit_addon = my_addons.addon_list[0].click_addon_name()
    version_status = edit_addon.click_manage_versions_link()
    version_status.wait_for_version_autoapproval("Approved")


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.addon
@pytest.mark.create_session("submissions_user")
def test_submit_listed_addon_tc_id_c4369(selenium, base_url, variables, wait):
    """Test covering the process of uploading a listed addon"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    submit_addon = page.click_submit_addon_button()
    # start the upload for a listed addon
    submit_addon.select_listed_option()
    submit_addon.click_continue()
    submit_addon.upload_addon("listed-addon.zip")
    # waits for the validation to complete and checks that is successful
    submit_addon.is_validation_successful()
    # checking that the Firefox compatibility checkbox is selected by default
    assert submit_addon.firefox_compat_checkbox.is_selected()
    # select the Android compatibility checkbox
    submit_addon.android_compat_checkbox.click()
    submit_addon.android_compat_pop_up.is_displayed()
    submit_addon.android_compat_yes_button.click()
    # on submit source code page, select 'Yes' to upload source code
    source = submit_addon.click_continue_upload_button()
    source.select_yes_to_submit_source()
    source.choose_source("listed-addon.zip")
    # source.choose_source("listed-addon.zip")
    details_form = source.continue_listed_submission()
    # setting a unique add-on name
    details_form.addon_name_field.clear()
    addon_name = f"Listed-{reusables.current_date()}-{reusables.get_random_string(5)}"
    details_form.set_addon_name(addon_name)
    details_form.set_addon_summary(variables["listed_addon_summary_en"])
    details_form.set_addon_description(variables["listed_addon_description_en"])
    # marks an add-on as experimental
    details_form.is_experimental.click()
    # flag add-on for payment requirements
    details_form.requires_payment.click()
    # reusables.scroll_into_view(selenium, details_form.categories_section)
    # set Firefox and Android categories for the addon
    details_form.select_categories(0)
    # details_form.select_android_categories(0)
    details_form.email_input_field("some-mail@mail.com")
    details_form.support_site_input_field("https://example.com")
    # set an addon license from the available list
    details_form.select_license_options[0].click()
    details_form.set_privacy_policy(variables["listed_addon_privacy_policy_en"])
    details_form.set_reviewer_notes(variables["listed_addon_reviewer_notes"])
    # submit the add-on details
    confirmation_page = details_form.submit_addon()
    assert (
            variables["listed_submission_confirmation"]
            in confirmation_page.submission_confirmation_messages[0].text
    )
    # go to the addon edit listing page and check that it was created
    edit_listing = confirmation_page.click_edit_listing_button()
    assert addon_name in edit_listing.name


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.addon
@pytest.mark.create_session("submissions_user")
def test_submit_addon_3mb_size_tc_id_c2274214(selenium, base_url, wait, variables):
    """Test covering the process of uploading a listed addon with 3-4 mb in size"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    submit_addon = page.click_submit_addon_button()
    # start the upload for a listed addon
    submit_addon.select_listed_option()
    submit_addon.click_continue()
    submit_addon.upload_addon("listed_addon_with_img.zip")
    # waits for the validation to complete and checks that is successful
    submit_addon.is_validation_successful()
    # checking that the Firefox compatibility checkbox is selected by default
    assert submit_addon.firefox_compat_checkbox.is_selected()
    # select the Android compatibility checkbox
    submit_addon.android_compat_checkbox.click()
    submit_addon.android_compat_pop_up.is_displayed()
    submit_addon.android_compat_yes_button.click()
    # on submit source code page, select 'Yes' to upload source code
    source = submit_addon.click_continue_upload_button()
    source.select_no_to_omit_source()
    # source.choose_source("listed-addon.zip")
    details_form = source.continue_listed_submission()
    # setting a unique add-on name
    details_form.addon_name_field.clear()
    addon_name = f"Listed-{reusables.current_date()}-{reusables.get_random_string(5)}"
    details_form.set_addon_name(addon_name)
    details_form.set_addon_summary(variables["listed_addon_summary_en"])
    details_form.set_addon_description(variables["listed_addon_description_en"])
    # marks an add-on as experimental
    details_form.is_experimental.click()
    # flag add-on for payment requirements
    details_form.requires_payment.click()
    # reusables.scroll_into_view(selenium, details_form.categories_section)
    # set Firefox and Android categories for the addon
    details_form.select_categories(0)
    # details_form.select_android_categories(0)
    details_form.email_input_field("some-mail@mail.com")
    details_form.support_site_input_field("https://example.com")
    # set an addon license from the available list
    details_form.select_license_options[0].click()
    details_form.set_privacy_policy(variables["listed_addon_privacy_policy_en"])
    details_form.set_reviewer_notes(variables["listed_addon_reviewer_notes"])
    # submit the add-on details
    confirmation_page = details_form.submit_addon()
    assert (
            variables["listed_submission_confirmation"]
            in confirmation_page.submission_confirmation_messages[0].text
    )
    # go to the addon edit listing page and check that it was created
    edit_listing = confirmation_page.click_edit_listing_button()
    assert addon_name in edit_listing.name


@pytest.mark.serial
@pytest.mark.addon
@pytest.mark.create_session("submissions_user")
def test_addon_last_modified_date(selenium, base_url):
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # check the last modified date in the latest submitted addon on Devhub homepage (should be current date)
    print(page.my_addons_list[0].my_addon_modified_date_text)
    assert (
            reusables.current_date() == page.my_addons_list[0].my_addon_modified_date_text
    )
    edit_addon = page.my_addons_list[0].click_my_addon_edit_link()
    # check the last modified date on the Edit listing page
    assert reusables.current_date() == edit_addon.last_modified_date


@pytest.mark.serial
@pytest.mark.create_session("submissions_user")
@pytest.mark.addon
def test_submit_mixed_addon_versions_tc_id_c14981(selenium, base_url, variables, wait):
    """Uploads an unlisted version to an exiting listed addon"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    my_addons = page.click_my_addons_header_link()
    # open the edit page of the latest listed add-on submitted
    edit_addon = my_addons.addon_list[0].click_addon_name()
    submit_version = edit_addon.click_upload_version_link()
    submit_version.change_version_distribution()
    # select unlisted option for the new version
    submit_version.select_unlisted_option()
    submit_version.click_continue()
    submit_version.upload_addon("mixed-addon-versions.zip")
    # wait for the validation to finish and check if it is successful
    submit_version.is_validation_successful()
    assert submit_version.success_validation_message.is_displayed()
    # on submit source code page, select No as we do not test source code upload here
    source = submit_version.click_continue_upload_button()
    source.select_no_to_omit_source()
    confirmation_page = source.continue_unlisted_submission()
    assert (
            variables["unlisted_submission_confirmation"]
            in confirmation_page.submission_confirmation_messages[0].text
    )
    manage_addons = confirmation_page.click_manage_listing_button()
    edit_addon = manage_addons.addon_list[0].click_addon_name()
    # verify that the unlisted addon badge is now visible on the edit details page
    assert edit_addon.unlisted_version_tooltip.is_displayed()


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.addon
def test_verify_new_unlisted_version_autoapproval_tc_id_C4372(selenium, base_url, variables):
    """Uploads a new version to an existing addon and verifies that is auto-approved"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.devhub_login("developer")
    addon = variables["unlisted_new_version_auto_approval"]
    # in order to upload a new version, we need to increment on the existing version number
    # to obtain the current version number, we make an API request that returns the value
    auth = selenium.get_cookie("sessionid")["value"]
    version_string = api_helpers.get_addon_version_string(base_url, addon, auth)
    # create a new addon version with the incremented versio number
    manifest = {
        "manifest_version": 2,
        "theme": {"frame": "#083af0", "tab_background_text": "#ffffff"},
        "version": f"{float(version_string) + 1}",
        "name": "New version auto-approval",
    }
    api_helpers.make_addon(manifest)
    # go to the unlisted distribution page to submit a new version
    selenium.get(f"{base_url}/developers/addon/{addon}/versions/submit/")
    submit_version = SubmitAddon(selenium).wait_for_page_to_load()
    submit_version.upload_addon("make-addon.zip")
    # wait for the validation to finish and check if it is successful
    submit_version.is_validation_successful()
    assert submit_version.success_validation_message.is_displayed()
    submit_version.click_continue()
    confirmation_page = SubmissionConfirmationPage(selenium)
    assert (
            variables["unlisted_submission_confirmation"]
            in confirmation_page.submission_confirmation_messages[0].text
    )
    # open the manage versions page for the addon and wait for the latest version to be auto-approved
    selenium.get(f"{base_url}/developers/addon/{addon}/versions")
    version_status = ManageVersions(selenium).wait_for_page_to_load()
    version_status.wait_for_version_autoapproval("Approved")


@pytest.mark.serial
@pytest.mark.addon
@pytest.mark.create_session("submissions_user")
def test_cancel_and_disable_version_during_upload(selenium, base_url, wait):
    """Test what happens in the upload process when a user chooses to cancel the submission"""
    selenium.get(f"{base_url}/developers/addon/submit/upload-listed")
    submit_addon = SubmitAddon(selenium, base_url).wait_for_page_to_load()
    # checking that the Firefox compatibility checkbox is selected by default
    wait.until(lambda _: submit_addon.firefox_compat_checkbox.is_selected())
    submit_addon.upload_addon("listed-addon.zip")
    submit_addon.is_validation_successful()
    source = submit_addon.click_continue_upload_button()
    # on the source code page click on the "Cancel and Disable version' button
    source.click_cancel_and_disable_version()
    assert (
            "Are you sure you wish to cancel and disable version?"
            in source.cancel_and_disable_explainer_text
    )
    # click on do not cancel to close the modal
    source.click_do_not_cancel_version()
    # click cancel version again and confirm this time
    source.click_cancel_and_disable_version()
    canceled_version = source.confirm_cancel_and_disable_version()
    assert "Incomplete" in canceled_version.incomplete_status.text
    assert "Disabled by Mozilla" in canceled_version.version_approval_status[0].text
    # delete the incomplete submission
    delete = canceled_version.delete_addon()
    delete.input_delete_confirmation_string()
    delete.confirm_delete_addon()


@pytest.mark.sanity
@pytest.mark.serial
@pytest.mark.addon
@pytest.mark.theme_and_validation
@pytest.mark.create_session("submissions_user")
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
