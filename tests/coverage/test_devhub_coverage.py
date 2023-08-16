from pages.desktop.developers.devhub_home import DevHubHome
from pages.desktop.developers.edit_addon import EditAddon
from pages.desktop.developers.manage_versions import ManageVersions
from pages.desktop.developers.submit_addon import ListedAddonSubmissionForm, SubmissionConfirmationPage
from scripts import reusables

import pytest
import time


# def test_upload_image_larger_than_4_mb_for_screenshots(
#     selenium, base_url, variables, wait
# ):
#     # Test Case : C1914716 from AMO Coverage > Devhub
#     """Go to the edit product page of an add-on to Images section, click Edit"""
#     devhub_home = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
#     devhub_home.devhub_login("developer")
#     edit_addon_page = EditAddon(selenium, base_url)
#     edit_addon_page.open_edit_page_for_addon(
#         selenium, base_url, variables["dev_reply_review"]
#     )
#     edit_addon_page.wait_for_page_to_load()
#     """Add-on icon and Screenshots sections are displayed"""
#     edit_addon_page.click_edit_addon_images_button_locator()
#     edit_addon_page.wait_for_images_section_to_load()
#     assert (
#         edit_addon_page.images_icon_label_locator.is_displayed(),
#         edit_addon_page.images_screenshot_locator.is_displayed(),
#         edit_addon_page.upload_icon_button_locator.is_displayed(),
#         edit_addon_page.upload_screenshot_button_locator.is_displayed(),
#     )
#     """Click on Add A Screenshot and try to upload a large image > 4MB (png or jpg format)"""
#     edit_addon_page.upload_screenshot("over_4mb_picture.png")
#     time.sleep(10)
#     """The image cannot be uploaded there's an error message displayed:"""
#     edit_addon_page.wait_for_screenshot_errors()
#     assert (
#         edit_addon_page.text_error_uploading_screenshot.text
#         in variables["screenshot_uploading_error_message"],
#         edit_addon_page.text_error_details_screenshot.text
#         in variables["screenshot_uploading_error_details_message"],
#     )


# Needs additional investigating to the part of changing images
# def test_upload_an_image_larger_than_7mb_for_themes(
#     selenium, base_url, variables, wait
# ):
#     # Test Case : C1914717 from AMO Coverage > Devhub
#     """Using the theme-wizard try to upload a header image >7 MB"""
#     devhub_home = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
#     devhub_home.devhub_login("developer")
#     selenium.get(f'{base_url}/developers/addon/submit/wizard-listed')
#     theme_wizard_page = ThemeWizard(selenium, base_url).wait_for_page_to_load()
#     theme_wizard_page.upload_theme_header("over_4mb_picture.png")
#     theme_wizard_page.wait_for_uploaded_image_preview()
#     """The image, colors for theme can be selected"""
#     theme_wizard_page.set_header_area_background_color("rgba(230, 37, 37, 1)")
#     theme_wizard_page.set_header_area_text_and_icons("rgba(0, 0, 0, 1)")
#     """Click Finish Theme"""
#     theme_wizard_page.click_submit_theme_button_locator()
#     """An error message is displayed: Maximum upload size is 7.00 MB - choose a smaller background image."""
#     theme_wizard_page.wait_for_header_image_error_message()
#     assert (
#         theme_wizard_page.header_image_error.text
#         in variables["theme_header_imager_error"]
#     )
#     """Select a different header image"""
#     theme_wizard_page.wait_for_change_image_button_locator_to_be_clickable()
#     theme_wizard_page.upload_through_different_header_image("theme_header.png")
#     """Image is selected"""
#     theme_wizard_page.wait_for_uploaded_image_preview()
#     """Click Finish Theme"""
#     theme_wizard_page.click_submit_theme_button_locator()
#     """The details page (next submission step) is displayed"""
#     # submit_addon_page = ListedAddonSubmissionForm(selenium, base_url).wait_for_page_to_load()
#     # assert(
#     #     submit_addon_page.addon_name_field.is_displayed(),
#     #     submit_addon_page.select_license_options.is_displayed()
#     # )

@pytest.mark.coverage
def test_cancel_review_request(selenium, base_url, variables, wait):
    # Test Case: C1803555 -> AMO Coverage > Devhub
    """Submit the first version of an add-on"""
    devhub_page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    devhub_page.devhub_login("developer")
    submit_addon = devhub_page.click_submit_addon_button()
    submit_addon.select_listed_option()
    submit_addon.click_continue()
    submit_addon.upload_addon("listed-addon.zip")
    submit_addon.is_validation_successful()
    assert submit_addon.success_validation_message.is_displayed()
    source = submit_addon.click_continue_upload_button()
    source.select_no_to_omit_source()
    confirmation_page = source.continue_listed_submission()
    random_string = reusables.get_random_string(10)
    summary = reusables.get_random_string(10)
    confirmation_page.set_addon_name(random_string)
    confirmation_page.set_addon_summary(summary)
    confirmation_page.select_firefox_categories(1)
    confirmation_page.select_license_options[0].click()
    """The add-on is submitted successfully"""
    confirmation_page.submit_addon()
    """Go to Manage Versions Page"""
    addon = f"listed-addon{random_string}"
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