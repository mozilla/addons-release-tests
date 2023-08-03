import pytest

from pages.desktop.developers.devhub_addon_validate import DevhubAddonValidate
from pages.desktop.developers.devhub_home import DevHubHome


def test_validate_addon_listed(selenium, base_url, variables, wait):
    """Go to Devhub Home page and login as the submissions_user"""
    devhub_home = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    devhub_home.devhub_login("developer")
    """Go to Devhub Addon Validate page"""
    devhub_addon_validate = (
        DevhubAddonValidate(selenium, base_url).open().wait_for_page_to_load()
    )
    assert (
        variables["on_this_site_label_message"]
        in devhub_addon_validate.addon_on_your_site.text
    )
    assert (
        variables["on_your_own_label_message"]
        in devhub_addon_validate.addon_on_your_own.text
    )
    """Click on On This Site Checkbox"""
    devhub_addon_validate.click_on_this_site_checkbox()
    assert devhub_addon_validate.on_this_site_checkbox.is_selected()
    """Upload addon and check if validation is approved"""
    devhub_addon_validate.upload_file("unlisted-addon.zip")
    devhub_addon_validate.is_validation_approved()
    assert (
        variables["addon_validation_message"]
        in devhub_addon_validate.upload_details_results.text
    )
    assert variables["upload_status"] in devhub_addon_validate.upload_status.text


def test_validate_addon_unlisted(selenium, base_url, variables, wait):
    """Go to Devhub Home page and login as the submissions_user"""
    devhub_home = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    devhub_home.devhub_login("developer")
    """Go to Devhub Addon Validate page"""
    devhub_addon_validate = (
        DevhubAddonValidate(selenium, base_url).open().wait_for_page_to_load()
    )
    assert (
        variables["on_this_site_label_message"]
        in devhub_addon_validate.addon_on_your_site.text
    )
    assert (
        variables["on_your_own_label_message"]
        in devhub_addon_validate.addon_on_your_own.text
    )
    """Click on On Your Own Checkbox"""
    devhub_addon_validate.click_on_your_own_text_checkbox()
    assert devhub_addon_validate.on_your_own_text_checkbox.is_selected()
    devhub_addon_validate.upload_file("unlisted-addon.zip")
    devhub_addon_validate.is_validation_approved()
    assert (
        variables["addon_validation_message"]
        in devhub_addon_validate.upload_details_results.text
    )
    assert variables["upload_status"] in devhub_addon_validate.upload_status.text
