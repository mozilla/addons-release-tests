import time
import pytest

from pages.desktop.developers.devhub_home import DevHubHome
from pages.desktop.developers.manage_versions import ManageVersions


@pytest.mark.login("developer")
def test_set_addon_invisible(selenium, base_url, variables, wait):
    """Set an addon Invisible and then reset the status to Visible"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # page.devhub_login("developer")
    selenium.get(f"{base_url}/developers/addon/invisible_addon_auto/versions")
    manage_version = ManageVersions(selenium, base_url).wait_for_page_to_load()
    # check that the Listing visibility section has the necessary information for developers
    assert (
        variables["visible_status_explainer"] in manage_version.visible_status_explainer
    )
    assert (
        variables["invisible_status_explainer"]
        in manage_version.invisible_status_explainer
    )
    # set the addon Invisible and Cancel the process
    manage_version.set_addon_invisible()
    assert (
        variables["hide_addon_confirmation_text"]
        in manage_version.hide_addon_confirmation_text
    )
    manage_version.cancel_hide_addon_process()
    # set the addon Invisible again and finish the process this time
    manage_version.set_addon_invisible()
    manage_version.click_hide_addon()
    wait.until(
        lambda _: "Invisible" in manage_version.addon_listed_status,
        message=f"Actual addon status was {manage_version.addon_listed_status}",
    )
    # set the addon status back to visible
    manage_version.set_addon_visible()
    wait.until(
        lambda _: "Approved" in manage_version.addon_listed_status,
        message=f"Actual addon status was {manage_version.addon_listed_status}",
    )


@pytest.mark.create_session("developer")
def test_disable_enable_version(selenium, base_url, variables, wait):
    """Check that developers cand disable and re-enable addon versions;
    This test works with an addon having a single version submitted and Approved"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    # page.devhub_login("developer")
    selenium.get(f"{base_url}/developers/addon/disable_version_auto/versions")
    manage_version = ManageVersions(selenium, base_url).wait_for_page_to_load()
    # had to use a time.sleep here because I couldn't get an explicit wait to work on the button
    time.sleep(2)
    # click on Delete/Disable button and then cancel the process to close the modal
    manage_version.click_delete_disable_version()
    assert (
        variables["delete_version_helptext"]
        in manage_version.delete_disable_version_helptext
    )
    assert (
        variables["delete_version_warning_text"]
        in manage_version.delete_disable_version_warning
    )
    manage_version.click_cancel_version_delete_link()
    # restart the Disable process again and finalize it this time
    manage_version.click_delete_disable_version()
    manage_version.click_disable_version_button()
    # verify that the version status changed to Disabled
    wait.until(
        lambda _: "Disabled by Mozilla"
        in manage_version.version_approval_status[0].text,
        message=f'Actual version status after Disable was: "{manage_version.version_approval_status[0].text}"',
    )
    # re-enable the version and verify that the status changes back to Approved
    manage_version.click_enable_version()
    wait.until(
        lambda _: "Approved" in manage_version.current_version_status,
        message=f'Actual version status after Re-enable was: "{manage_version.current_version_status}"',
    )
