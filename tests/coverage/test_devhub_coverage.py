from pages.desktop.developers.devhub_home import DevHubHome
from pages.desktop.developers.edit_addon import EditAddon
from pages.desktop.developers.submit_addon import ThemeWizard, ListedAddonSubmissionForm


def test_upload_image_larger_than_4_mb_for_screenshots(
    selenium, base_url, variables, wait
):
    # Test Case : C1914716 from AMO Coverage > Devhub
    """Go to the edit product page of an add-on to Images section, click Edit"""
    devhub_home = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    devhub_home.devhub_login("developer")
    edit_addon_page = EditAddon(selenium, base_url)
    edit_addon_page.open_edit_page_for_addon(
        selenium, base_url, variables["dev_reply_review"]
    )
    edit_addon_page.wait_for_page_to_load()
    """Add-on icon and Screenshots sections are displayed"""
    edit_addon_page.click_edit_addon_images_button_locator()
    edit_addon_page.wait_for_images_section_to_load()
    assert (
        edit_addon_page.images_icon_label_locator.is_displayed(),
        edit_addon_page.images_screenshot_locator.is_displayed(),
        edit_addon_page.upload_icon_button_locator.is_displayed(),
        edit_addon_page.upload_screenshot_button_locator.is_displayed(),
    )
    """Click on Add A Screenshot and try to upload a large image > 4MB (png or jpg format)"""
    edit_addon_page.upload_screenshot("over_4mb_picture.png")
    """The image cannot be uploaded there's an error message displayed:"""
    edit_addon_page.wait_for_screenshot_errors()
    assert (
        edit_addon_page.text_error_uploading_screenshot.text
        in variables["screenshot_uploading_error_message"],
        edit_addon_page.text_error_details_screenshot.text
        in variables["screenshot_uploading_error_details_message"],
    )


def test_upload_an_image_larger_than_7mb_for_themes(
    selenium, base_url, variables, wait
):
    # Test Case : C1914717 from AMO Coverage > Devhub
    """Using the theme-wizard try to upload a header image >7 MB"""
    devhub_home = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    devhub_home.devhub_login("developer")
    selenium.get(f'{base_url}/developers/addon/submit/wizard-listed')
    theme_wizard_page = ThemeWizard(selenium, base_url).wait_for_page_to_load()
    theme_wizard_page.upload_theme_header("over_4mb_picture.png")
    theme_wizard_page.wait_for_uploaded_image_preview()
    """The image, colors for theme can be selected"""
    theme_wizard_page.set_header_area_background_color("rgba(230, 37, 37, 1)")
    theme_wizard_page.set_header_area_text_and_icons("rgba(0, 0, 0, 1)")
    """Click Finish Theme"""
    theme_wizard_page.click_submit_theme_button_locator()
    """An error message is displayed: Maximum upload size is 7.00 MB - choose a smaller background image."""
    theme_wizard_page.wait_for_header_image_error_message()
    assert (
        theme_wizard_page.header_image_error.text
        in variables["theme_header_imager_error"]
    )
    """Select a different header image"""
    theme_wizard_page.upload_through_different_header_image("theme_header.png")
    """Image is selected"""
    theme_wizard_page.wait_for_uploaded_image_preview()
    """Click Finish Theme"""
    theme_wizard_page.click_submit_theme_button_locator()
    """The details page (next submission step) is displayed"""
    submit_addon_page = ListedAddonSubmissionForm(selenium, base_url).wait_for_page_to_load()
    assert(
        submit_addon_page.addon_name_field.is_displayed(),
        submit_addon_page.select_license_options.is_displayed()
    )



