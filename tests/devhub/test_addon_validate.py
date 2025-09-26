"""test_addon_validate.py focuses on the validation page for addons"""
import pytest

from pages.desktop.developers.devhub_addon_validate import DevhubAddonValidate
from pages.desktop.developers.devhub_home import DevHubHome


@pytest.mark.sanity
@pytest.mark.login("developer")
def test_validate_addon_listed(selenium, base_url, variables):
    """Verifies the process of validating a listed addon using the "On This Site"
    checkbox in the DevHub Addon Validate page.
    The test ensures that the addon is uploaded and validated successfully,
    displaying appropriate success messages."""
    """Go to Devhub Addon Validate page"""
    DevHubHome(selenium, base_url).open().wait_for_page_to_load()
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
    devhub_addon_validate.upload_file("listed-addon.zip")
    devhub_addon_validate.is_validation_approved()
    assert (
        variables["addon_validation_message"]
        in devhub_addon_validate.upload_details_results_succes.text
    )
    assert variables["upload_status"] in devhub_addon_validate.upload_status.text


@pytest.mark.sanity
@pytest.mark.create_session("developer")
def test_validate_listed_addon_option_no_manifest_found(
    selenium, base_url, variables
):
    """Tests the scenario where an addon is uploaded with no manifest file.
    It verifies that the validation fails and that the appropriate error
    message is shown when using the "On This Site" checkbox for a listed addon."""
    DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    """Go to Devhub Addon Validate page"""
    devhub_addon_validate = (
        DevhubAddonValidate(selenium, base_url).open().wait_for_page_to_load()
    )
    """Click on On This Site Checkbox"""
    devhub_addon_validate.click_on_this_site_checkbox()
    assert devhub_addon_validate.on_this_site_checkbox.is_selected()
    devhub_addon_validate.upload_file("no_manifest_addon.zip")
    devhub_addon_validate.is_not_validated()
    assert (
        variables["upload_status_results_failed"]
        in devhub_addon_validate.upload_details_results_failed.text
    )
    assert (
        variables["no_manifest_found_message"]
        in devhub_addon_validate.upload_errors.text
    )


@pytest.mark.sanity
@pytest.mark.create_session("developer")
def test_validate_listed_addon_option_unsupported_format(
    selenium, base_url, variables
):
    """Verifies the behavior when an unsupported addon format is uploaded (e.g., an image file).
    The test ensures that the validation fails and that the correct error message for unsupported
    formats is displayed when using the "On This Site" checkbox for a listed addon."""
    DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    """Go to Devhub Addon Validate page"""
    devhub_addon_validate = (
        DevhubAddonValidate(selenium, base_url).open().wait_for_page_to_load()
    )
    """Click on On This Site Checkbox"""
    devhub_addon_validate.click_on_this_site_checkbox()
    assert devhub_addon_validate.on_this_site_checkbox.is_selected()
    devhub_addon_validate.upload_file("unsupported-format-addon.jpg")
    devhub_addon_validate.is_not_validated()
    assert (
        variables["upload_status_results_failed"]
        in devhub_addon_validate.upload_details_results_failed.text
    )
    assert (
        variables["unsupported_format_message"]
        in devhub_addon_validate.upload_errors.text
    )


@pytest.mark.sanity
@pytest.mark.login("developer")
def test_validate_addon_unlisted(selenium, base_url, variables):
    """Verifies the process of validating an unlisted addon using
    the "On Your Own" checkbox in the DevHub Addon Validate page.
    The test checks that the addon is uploaded and validated successfully,
    displaying appropriate success messages."""
    """Go to Devhub Addon Validate page"""
    DevHubHome(selenium, base_url).open().wait_for_page_to_load()
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
        in devhub_addon_validate.upload_details_results_succes.text
    )
    assert variables["upload_status"] in devhub_addon_validate.upload_status.text


@pytest.mark.sanity
@pytest.mark.create_session("developer")
def test_validate_unlisted_addon_option_no_manifest_found(
    selenium, base_url, variables
):
    """Tests the scenario where an unlisted addon is uploaded with no manifest file.
    The test ensures that validation fails and the correct error message is displayed
    when using the "On Your Own" checkbox for an unlisted addon."""
    """Go to Devhub Addon Validate page"""
    devhub_addon_validate = (
        DevhubAddonValidate(selenium, base_url).open().wait_for_page_to_load()
    )
    """Click on On Your Own Checkbox"""
    devhub_addon_validate.click_on_your_own_text_checkbox()
    assert devhub_addon_validate.on_your_own_text_checkbox.is_selected()
    devhub_addon_validate.upload_file("no_manifest_addon.zip")
    devhub_addon_validate.is_not_validated()
    assert (
        variables["upload_status_results_failed"]
        in devhub_addon_validate.upload_details_results_failed.text
    )
    assert (
        variables["no_manifest_found_message"]
        in devhub_addon_validate.upload_errors.text
    )


@pytest.mark.sanity
@pytest.mark.create_session("developer")
def test_validate_unlisted_addon_option_unsupported_format(
    selenium, base_url, variables
):
    """Verifies the behavior when an unsupported addon format is uploaded
     for an unlisted addon. The test ensures that the validation fails
     and displays the correct error message for unsupported formats."""
    """Go to Devhub Addon Validate page"""
    devhub_addon_validate = (
        DevhubAddonValidate(selenium, base_url).open().wait_for_page_to_load()
    )
    """Click on On Your Own Checkbox"""
    devhub_addon_validate.click_on_your_own_text_checkbox()
    assert devhub_addon_validate.on_your_own_text_checkbox.is_selected()
    devhub_addon_validate.upload_file("unsupported-format-addon.jpg")
    devhub_addon_validate.is_not_validated()
    assert (
        variables["upload_status_results_failed"]
        in devhub_addon_validate.upload_details_results_failed.text
    )
    assert (
        variables["unsupported_format_message"]
        in devhub_addon_validate.upload_errors.text
    )
