from pages.desktop.developers.devhub_home import DevHubHome
from pages.desktop.developers.manage_versions import ManageVersions


def test_set_addon_invisible(selenium, base_url, variables, wait):
    """Set an addon Invisible and then reset the status to Visible"""
    page = DevHubHome(selenium, base_url).open().wait_for_page_to_load()
    page.devhub_login('developer')
    selenium.get(f'{base_url}/developers/addon/invisible_addon_auto/versions')
    manage_version = ManageVersions(selenium, base_url).wait_for_page_to_load()
    # check that the Listing visibility section has the necessary information for developers
    assert (
        variables['visible_status_explainer'] in manage_version.visible_status_explainer
    )
    assert (
        variables['invisible_status_explainer']
        in manage_version.invisible_status_explainer
    )
    # set the addon Invisible and Cancel the process
    manage_version.set_addon_invisible()
    assert (
        variables['hide_addon_confirmation_text']
        in manage_version.hide_addon_confirmation_text
    )
    manage_version.cancel_hide_addon_process()
    # set the addon Invisible again and finish the process this time
    manage_version.set_addon_invisible()
    manage_version.click_hide_addon()
    wait.until(
        lambda _: 'Invisible' in manage_version.addon_listed_status,
        message=f'Actual addon status was {manage_version.addon_listed_status}',
    )
    # set the addon status back to visible
    manage_version.set_addon_visible()
    wait.until(
        lambda _: 'Approved' in manage_version.addon_listed_status,
        message=f'Actual addon status was {manage_version.addon_listed_status}',
    )
