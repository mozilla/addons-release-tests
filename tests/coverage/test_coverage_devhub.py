import pytest
import time

from selenium.webdriver.support import expected_conditions as EC
from pages.desktop.developers.edit_addon import EditAddon

# @pytest.mark.coverage
# @pytest.mark.login("developer")
# def test_upload_4mb_screenshots(base_url, selenium, variables, wait):
#     "Go to the edit product page of an add-on to Images section, click Edit"
#     "Add-on icon and Screenshots sections are displayed"
#     selenium.get(f"{base_url}/developers/addon/{variables['4mb_addon_slug']}/edit")
#     edit_addon_page = EditAddon(selenium, base_url).wait_for_page_to_load()
#     "Add-on icon and Screenshots sections are displayed"
#     edit_addon_page.edit_addon_describe_section.is_displayed()
#     edit_addon_page.edit_addon_media_button.is_displayed()
#     "Click on Add A Screenshot and try to upload a large image > 4MB (png or jpg format)"
#     edit_addon_page.edit_addon_media_button.click()
#     edit_addon_page.screenshot_upload.is_displayed()
#     edit_addon_page.screenshot_file_upload("over_4mb_picture.png")
#     time.sleep(10)
#     "The image cannot be uploaded there's an error message displayed:"
#     "There was an error uploading your file."
#     "Please use images smaller than 4MB."
#     edit_addon_page.edit_preview_error_strong.is_displayed()
#     edit_addon_page.edit_preview_explicit_error.is_displayed()

@pytest.mark.coverage
def test_cancel_review_request(selenium, base_url, variables, wait):
    # Test Case: C1803555 -> AMO Coverage > Devhub
    """Submit the first version of an add-on"""
    addon = submit_addon_method(selenium, base_url)
    manage_versions = ManageVersions(selenium, base_url)
    manage_versions.open_manage_versions_page_for_addon(selenium, base_url, addon)
    """Page is displayed"""
    manage_versions = ManageVersions(selenium, base_url).wait_for_page_to_load()
    """Check that below the version there's a 'Cancel Review Request' blue link. Click it"""
    """Cancel Review Request box is displayed:"""
    cancel_review_request_modal = manage_versions.cancel_review_request()
    assert (
        variables["cancel_your_review_request_message"]
        in cancel_review_request_modal.cancel_your_review_request_message_locator.text,
        variables["are_you_sure_cancel_review_message"]
        in cancel_review_request_modal.are_you_sure_message.text
    )
    """Click on Cancel Review Request blue button"""
    cancel_review_request_modal.click_cancel_review_request_button()
    """Status of the addon is: Incomplete, Version is: Disabled by Mozilla"""
    assert manage_versions.request_review_button.is_displayed()
    assert manage_versions.disabled_by_mozilla_text.is_displayed()
    assert manage_versions.addon_status_incomplete.is_displayed()
    assert (
        variables["addon_status_incomplete"]
        in manage_versions.addon_status_incomplete.text,
        variables["addon_version_disabled_by_mozilla"]
        in manage_versions.disabled_by_mozilla_text.text,
    )
    """Clean-up: Delete created add-on"""
    delete_addon_modal = manage_versions.delete_addon()
    delete_addon_modal.input_delete_confirmation_string()
    delete_addon_modal.confirm_delete_addon()

@pytest.mark.coverage
def test_disable_an_addon_at_submission(selenium, base_url, wait, variables):
    # Test Case: C1898098 AMO Coverage > Devhub
    """Click on "Submit a new Addon" and upload a listed file"""
    devhub_page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    devhub_page.devhub_login("developer")
    submit_addon = devhub_page.click_submit_addon_button()
    submit_addon.select_listed_option()
    submit_addon.click_continue()
    submit_addon.upload_addon("listed-addon.zip")
    """Your add-on was validated with no errors or warnings."""
    submit_addon.is_validation_successful()
    assert submit_addon.success_validation_message.is_displayed()
    """Click on Continue"""
    """The second page of the submission is displayed"""
    source = submit_addon.click_continue_upload_button()
    """Click "Cancel and Disable Version"""
    """A box is opened and it asks for a confirmation: Are you sure you wish to cancel and disable version? """
    """Click Yes, Cancel"""
    source.click_cancel_and_disable_version()
    """The versions page is displayed. 
    The Status of the addon is Incomplete on the left, and "Disabled by Mozilla" in versions history."""
    manage_versions_page = source.confirm_cancel_and_disable_version()
    """Click "Request Review"""
    manage_versions_page.click_request_review_button()
    """The submission form should be displayed /submit/details in order to complete the submission."""
    listed_addon_submission_form = ListedAddonSubmissionForm(selenium, base_url).wait_for_page_to_load()
    """You must provide further details to proceed."""
    random_string = reusables.get_random_string(10)
    summary = reusables.get_random_string(10)
    addon = f"listed-addon{random_string}"
    listed_addon_submission_form.set_addon_name(random_string)
    listed_addon_submission_form.set_addon_summary(summary)
    listed_addon_submission_form.select_firefox_categories(1)
    listed_addon_submission_form.select_license_options[0].click()
    """Complete the form and "Submit Version"""
    listed_addon_submission_form.submit_addon()
    """The version is submitted. ".../addon/cancel-disable/submit/finish" page is displayed"""
    SubmissionConfirmationPage(selenium, base_url).wait_for_page_to_load()
    """Clean-up: Delete created add-on"""
    manage_versions_page.open_manage_versions_page_for_addon(selenium, base_url, addon)
    delete_addon_modal = manage_versions_page.delete_addon()
    delete_addon_modal.input_delete_confirmation_string()
    delete_addon_modal.confirm_delete_addon()

def test_change_the_license(selenium, base_url, variables, wait):
    # Test Case: C1901412 AMO Coverage > Devhub
    """Submit a new add-on"""
    addon = submit_addon_method(selenium, base_url)
    """From Manage Authors and License page -> select a new License for the add-on and Save Changes"""
    manage_authors_page = ManageAuthorsAndLicenses(selenium, base_url)
    manage_authors_page.open_manage_authors_and_licenses_page(selenium, base_url, addon)
    manage_authors_page.wait_for_page_to_load()
    assert manage_authors_page.radio_button_mozilla_public_license.is_selected()
    manage_authors_page.click_general_public_license()
    assert manage_authors_page.radio_button_general_public_license.is_selected()
    manage_authors_page.click_save_changes_button()
    manage_authors_page.wait_for_notification_box_success()
    assert (
        variables["notification_box_success"]
        in manage_authors_page.notification_box_success.text
    )
    selenium.get(f"{base_url}/firefox/addon/{addon}")
    addon_detail_page = Detail(selenium, base_url).wait_for_page_to_load()
    assert addon_detail_page.addon_icon.is_displayed()
    """Clean-up: Delete created add-on"""
    manage_versions_page = ManageVersions(selenium, base_url)
    manage_versions_page.open_manage_versions_page_for_addon(selenium, base_url, addon)
    delete_addon_modal = manage_versions_page.delete_addon()
    delete_addon_modal.input_delete_confirmation_string()
    delete_addon_modal.confirm_delete_addon()
