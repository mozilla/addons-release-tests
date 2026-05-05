import pytest

from selenium.common.exceptions import TimeoutException

from pages.desktop.about_addons import AboutAddons
from pages.desktop.toolbar.toolbar import Toolbar


def _install_first_recommended_extension(
    selenium, wait, firefox, firefox_notifications
):
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium).wait_for_page_to_load()
    wait.until(
        lambda _: len(
            [card.install_button for card in about_addons.addon_cards_items]
        )
        >= 4,
        message="Recommendations pane did not return enough cards to install from",
    )
    for card in about_addons.addon_cards_items:
        if card.is_extension_card():
            addon_name = card.disco_addon_name.text
            card.install_button.click()
            firefox.browser.wait_for_notification(
                firefox_notifications.AddOnInstallConfirmation
            ).install()
            try:
                firefox.browser.wait_for_notification(
                    firefox_notifications.AddOnInstallComplete
                ).close()
            except TimeoutException:
                pass
            if len(selenium.window_handles) > 1:
                selenium.switch_to.window(selenium.window_handles[0])
            return about_addons, addon_name
    raise AssertionError("No extension cards were available in the Recommendations pane")

@pytest.mark.skip
def test_extension_toolbar_icon_menu_tc_id_c617050(
    selenium, base_url, wait, firefox, firefox_notifications
):
    """Test 1: the unified extensions toolbar menu lists Manage / Remove / Report
    for an installed extension, and 'Manage Extension' navigates to the addon's
    detail page in about:addons."""
    _install_first_recommended_extension(
        selenium, wait, firefox, firefox_notifications
    )

    toolbar = Toolbar(selenium, base_url)
    toolbar.open_unified_extensions_panel()
    toolbar.open_extension_item_menu()

    options = toolbar.menu_options_present
    expected = {
        "unified-extensions-context-menu-manage-extension",
        "unified-extensions-context-menu-remove-extension",
        "unified-extensions-context-menu-report-extension",
    }
    missing = expected - set(options)
    assert not missing, (
        f"Toolbar context menu is missing expected items: {missing}; "
        f"saw: {options}"
    )

    initial_handle = selenium.current_window_handle
    initial_handles = list(selenium.window_handles)
    toolbar.click_manage_extension()

    wait.until(
        lambda _: (
            len(selenium.window_handles) > len(initial_handles)
            or "about:addons" in selenium.current_url
        ),
        message="Manage Extension did not open or focus about:addons",
    )
    if len(selenium.window_handles) > len(initial_handles):
        new_handle = next(
            h for h in selenium.window_handles if h not in initial_handles
        )
        selenium.switch_to.window(new_handle)
    else:
        selenium.switch_to.window(initial_handle)

    assert "about:addons" in selenium.current_url, (
        f"After clicking Manage Extension, expected about:addons in URL, "
        f"got {selenium.current_url!r}"
    )

@pytest.mark.skip
def test_about_addons_view_recent_updates_tc_id_c617063(
    selenium, base_url, wait, firefox, firefox_notifications
):
    """Test 2: the View Recent Updates option from the about:addons cogwheel
    menu opens the Recent Updates section, and a freshly installed addon shows
    up in that list."""
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium).wait_for_page_to_load()
    about_addons.click_options_button()
    view_recent_updates = about_addons.click_panel_item_action_check_for_updates()

    assert view_recent_updates.list_section_name.is_displayed(), (
        "Recent Updates section header was not visible after selecting "
        "'View Recent Updates'"
    )

    initial_addons = set(view_recent_updates.addon_names)

    selenium.get("about:addons")
    refreshed = AboutAddons(selenium).wait_for_page_to_load()
    _, installed_name = _install_first_recommended_extension(
        selenium, wait, firefox, firefox_notifications
    )

    refreshed.click_options_button()
    view_recent_updates = refreshed.click_panel_item_action_check_for_updates()
    updated_addons = view_recent_updates.addon_names

    assert any(installed_name in name for name in updated_addons), (
        f"Newly installed addon {installed_name!r} did not appear in the "
        f"Recent Updates list; current entries: {updated_addons}"
    )
    assert set(updated_addons) - initial_addons, (
        "Recent Updates list did not change after installing a new addon"
    )


def test_about_addons_debug_addons_opens_about_debugging(selenium, wait):
    """Selecting 'Debug Add-ons' from the about:addons cogwheel menu opens
    about:debugging#/runtime/this-firefox in a new tab."""
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium).wait_for_page_to_load()
    about_addons.click_options_button()
    about_addons.click_panel_item_action_debug_addons()

    wait.until(
        lambda _: "about:debugging" in selenium.current_url,
        message=f"Expected about:debugging URL, got {selenium.current_url!r}",
    )
    assert "runtime/this-firefox" in selenium.current_url, (
        f"Debug Add-ons opened {selenium.current_url!r}, "
        f"expected the runtime/this-firefox panel"
    )


def test_about_addons_manage_extension_shortcuts(selenium, wait):
    """Selecting 'Manage Extension Shortcuts' from the cogwheel opens the
    shortcuts page; the page lists at least one extension card and the Back
    button returns the user to the previous about:addons section."""
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium).wait_for_page_to_load()
    about_addons.click_extensions_side_button()
    extensions_url = selenium.current_url

    about_addons.click_options_button()
    shortcuts = about_addons.click_panel_item_action_manage_shortcuts()

    assert shortcuts.header.is_displayed(), (
        "Manage Extension Shortcuts header was not displayed after selecting the menu item"
    )
    assert shortcuts.shortcut_cards or shortcuts.no_shortcuts_section_visible, (
        "Manage Extension Shortcuts page showed neither shortcut cards nor a "
        "'no shortcuts' section"
    )

    shortcuts.click_back()
    wait.until(
        lambda _: selenium.current_url == extensions_url,
        message=(
            f"Back button did not return to {extensions_url!r}; "
            f"current URL is {selenium.current_url!r}"
        ),
    )
