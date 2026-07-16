import time
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.developers.devhub_home import DevHubHome
from pages.desktop.developers.edit_addon import EditAddon
from pages.desktop.developers.manage_versions import ManageVersions


@pytest.mark.login("developer")
def test_addon_edit_markdown_support_link(selenium, base_url, wait):
    """Verify the Markdown-supported helper link in the Describe Add-on section
    opens the correct Extension Workshop docs page."""
    selenium.get(f"{base_url}/developers/addon/disable_version_auto/edit")
    edit_addon = EditAddon(selenium, base_url).wait_for_page_to_load()
    # expand the Describe Add-on section to reveal the syntax-support link
    edit_addon.edit_addon_describe_button.click()
    # wait for the AJAX expansion to complete (description textarea only
    # appears in the expanded/edit state)
    wait.until(EC.visibility_of_element_located((By.ID, "id_description_0")))
    # click opens the docs page in a new tab
    edit_addon.markdown_support_link.click()
    wait.until(EC.number_of_windows_to_be(2))
    selenium.switch_to.window(selenium.window_handles[1])
    wait.until(EC.url_contains("create-an-appealing-listing"))
    wait.until(EC.url_contains("make-use-of-markdown"))
    wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "abbr[title^='The description, developer comments']")
        )
    )


@pytest.mark.login("developer")
@pytest.mark.skip(reason="to be fixed when coming back for skipped tests")
def test_set_addon_invisible_tc_id_c4371(selenium, base_url, variables, wait):
    """Set an addon Invisible and then reset the status to Visible"""
    selenium.get(f"{base_url}/developers/addon/invisible_addon_auto/versions")
    manage_version = ManageVersions(selenium, base_url).wait_for_page_to_load()
    # make the test independent of the add-on's starting state: a prior
    # interrupted/rerun run can leave it Invisible, in which case selecting
    # Invisible again would not open the confirmation modal (see issue below)
    manage_version.ensure_addon_visible()
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


@pytest.mark.login("developer")
def test_disable_enable_version_tc_id_c159074(selenium, base_url, variables, wait):
    """Check that developers cand disable and re-enable addon versions;
    This test works with an addon having a single version submitted and Approved"""
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
