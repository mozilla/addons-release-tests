from pages.desktop.developers.devhub_home import DevHubHome
from pages.desktop.developers.edit_addon import EditAddon
from pages.desktop.developers.submit_addon import ThemeWizard


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
    selenium.get(f'f{base_url}/developers/addon/submit/wizard-listed')
    theme_wizard_page = ThemeWizard(selenium, base_url).wait_for_page_to_load()
    theme_wizard_page.upload_theme_header("over_4mb_picture.png")


