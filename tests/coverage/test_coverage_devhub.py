import pytest
import time

from selenium.webdriver.support import expected_conditions as EC
from pages.desktop.developers.edit_addon import EditAddon

@pytest.mark.coverage
@pytest.mark.login("developer")
def test_upload_4mb_screenshots(base_url, selenium, variables, wait):
    "Go to the edit product page of an add-on to Images section, click Edit"
    "Add-on icon and Screenshots sections are displayed"
    selenium.get(f"{base_url}/developers/addon/{variables['4mb_addon_slug']}/edit")
    edit_addon_page = EditAddon(selenium, base_url).wait_for_page_to_load()
    "Add-on icon and Screenshots sections are displayed"
    edit_addon_page.edit_addon_describe_section.is_displayed()
    edit_addon_page.edit_addon_media_button.is_displayed()
    "Click on Add A Screenshot and try to upload a large image > 4MB (png or jpg format)"
    edit_addon_page.edit_addon_media_button.click()
    edit_addon_page.screenshot_upload.is_displayed()
    edit_addon_page.screenshot_file_upload("over_4mb_picture.png")
    time.sleep(10)
    "The image cannot be uploaded there's an error message displayed:"
    "There was an error uploading your file."
    "Please use images smaller than 4MB."
    edit_addon_page.edit_preview_error_strong.is_displayed()
    edit_addon_page.edit_preview_explicit_error.is_displayed()


