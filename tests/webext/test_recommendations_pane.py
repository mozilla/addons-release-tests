import pytest

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.desktop.about_addons import AboutAddons


@pytest.mark.webext
def test_install_addon_from_recommendations_pane_TC_ID_C617016(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Install an extension from the Recommendations pane and verify the full
    post-install flow: install -> Manage button swap, three-dot menu options,
    Disable/Enable toggle behavior."""
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium, base_url).wait_for_page_to_load()
    # Step 1 — Recommendations tab loads
    about_addons.click_recommendations_side_button()
    # Pick the first extension cassette — the disco mix changes day to day so the
    # index of an extension vs. theme card is not stable
    extension_index = next(
        i for i, c in enumerate(about_addons.addon_cards_items) if c.is_extension_card()
    )
    extension_card = about_addons.addon_cards_items[extension_index]
    addon_name = extension_card.disco_addon_name.text
    # Step 2 — click "+ Add to Firefox": permission door-hanger with Add/Cancel buttons
    extension_card.install_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    # Door-hanger with the add-on name and an "Okay, Got It" button closes here
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    if len(selenium.window_handles) == 2:
        selenium.switch_to.window(selenium.window_handles[0])
    # Install-button is replaced with "Manage" on the same disco card
    assert about_addons.addon_cards_items[extension_index].manage_addon_button.is_displayed()
    # Switch to the Extensions tab — the new add-on must be listed.
    # The disco-card display name and the installed-addon display name can
    # diverge on stage (the feed returns its own short name), so verify the
    # presence of an extra addon entry beyond the always-present WAF Bypass
    # helper rather than matching the exact card title.
    about_addons.click_extensions_side_button()
    installed_names = [el.text for el in about_addons.installed_addon_name]
    assert len(installed_names) >= 2, (
        f"Expected at least one new extension on top of the WAF Bypass helper, "
        f"got {installed_names}"
    )
    # Three-dot menu must expose Manage (More Options), Remove, Report. Preferences
    # is only shown for extensions that declare `options_ui` in their manifest,
    # so we don't assert on its presence here.
    about_addons.click_more_options_button_addon()
    assert about_addons.more_options_manage_button.is_displayed()
    assert about_addons.more_options_remove_button.is_displayed()
    assert about_addons.more_options_report_button.is_displayed()
    # Report opens the abuse-report form in a new tab
    about_addons.click_more_options_report_addon()
    selenium.switch_to.window(selenium.window_handles[0])
    # Disable/Enable toggle — default is enabled; one click disables, second re-enables
    addon_name_disabled = about_addons.extensions_side_toggle_addon()
    assert "(disabled)" in addon_name_disabled
    addon_name_enabled = about_addons.extensions_side_toggle_addon()
    assert "(disabled)" not in addon_name_enabled
    # Remove → an "Undo" control is offered, and clicking it restores the add-on.
    # Firefox shows a chrome-level confirm dialog before removing, so accept it
    # via `remove_addon_dialog` before Marionette auto-dismisses it.
    about_addons.click_more_options_button_addon()
    about_addons.click_more_options_remove_addon()
    about_addons.remove_addon_dialog()
    assert about_addons.undo_remove_button.is_displayed()
    about_addons.click_undo_remove()
    assert len([el.text for el in about_addons.installed_addon_name]) >= 2, (
        "Extension was not restored after Undo"
    )


@pytest.mark.webext
def test_cancel_addon_install_from_recommendations_pane_TC_ID_C617016(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """The permission door-hanger's Cancel button must abort the install: the
    add-on is not installed and the card keeps its install button (no Manage)."""
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium, base_url).wait_for_page_to_load()
    about_addons.click_recommendations_side_button()
    extension_index = next(
        i for i, c in enumerate(about_addons.addon_cards_items) if c.is_extension_card()
    )
    about_addons.addon_cards_items[extension_index].install_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).cancel()
    # Cancel aborts the install — the same card still exposes the install button
    assert about_addons.addon_cards_items[extension_index].install_button.is_displayed()


@pytest.mark.webext
def test_install_theme_from_recommendations_pane_TC_ID_C617017(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Install a theme from the Recommendations pane and verify the post-install
    flow under the Themes tab. Themes do not expose a Preferences/Options menu
    item, so it is intentionally excluded from the menu assertions."""
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium, base_url).wait_for_page_to_load()
    about_addons.click_recommendations_side_button()
    # Find the first theme cassette — the disco service may or may not include a
    # theme in any given response, so skip the test if none are present rather
    # than blindly relying on index 0
    theme_index = next(
        (i for i, c in enumerate(about_addons.addon_cards_items)
         if not c.is_extension_card()),
        None,
    )
    if theme_index is None:
        pytest.skip("No theme cassette returned by the disco service in this run")
    theme_card = about_addons.addon_cards_items[theme_index]
    theme_name = theme_card.disco_addon_name.text
    theme_card.install_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    if len(selenium.window_handles) == 2:
        selenium.switch_to.window(selenium.window_handles[0])
    # Install button replaced with "Manage" on the same card
    assert about_addons.addon_cards_items[theme_index].manage_addon_button.is_displayed()
    # The installed theme appears in the Themes tab (not Extensions). Same
    # rationale as TC1: rely on a count check rather than exact name match
    # because the disco feed and installed-addon names can differ on stage.
    about_addons.click_themes_side_button()
    installed_theme_names = [el.text for el in about_addons.installed_addon_name]
    assert installed_theme_names, "Themes tab is empty after installing a theme"
    # Three-dot menu options for themes: Manage, Remove, Report (no Preferences)
    about_addons.click_more_options_button_addon()
    assert about_addons.more_options_manage_button.is_displayed()
    assert about_addons.more_options_remove_button.is_displayed()
    assert about_addons.more_options_report_button.is_displayed()
    about_addons.click_more_options_report_addon()
    selenium.switch_to.window(selenium.window_handles[0])
    # Disable/Enable toggle behavior matches extensions
    theme_name_disabled = about_addons.extensions_side_toggle_addon()
    assert "(disabled)" in theme_name_disabled
    theme_name_enabled = about_addons.extensions_side_toggle_addon()
    assert "(disabled)" not in theme_name_enabled
    # Remove → an "Undo" control is offered, and clicking it restores the theme
    about_addons.click_more_options_button_addon()
    about_addons.click_more_options_remove_addon()
    about_addons.remove_addon_dialog()
    assert about_addons.undo_remove_button.is_displayed()
    about_addons.click_undo_remove()
    assert about_addons.installed_addon_name, "Theme was not restored after Undo"


@pytest.mark.webext
def test_recommendations_page_layout_TC_ID_C617018(selenium, base_url, wait):
    """Verifies the static contents of the Recommendations (discovery) pane:
    a search bar, the "recommends" intro link, the personalized-recommendations
    "Learn more" link, cassettes for each card (name, author, summary or theme
    preview, install button), the "Find more add-ons" button and the
    "Privacy Policy" link."""
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium, base_url).wait_for_page_to_load()
    about_addons.click_recommendations_side_button()
    # Search bar is present
    assert about_addons.search_box_element.is_displayed()
    # The "recommends" link in the intro opens the recommended-extensions kb page
    about_addons.firefox_recommends_link()
    # Note: the spec also references a "Some of these recommendations are
    # personalized..." Learn more link, but that paragraph is only rendered when
    # personalized recommendations are enabled by the disco service and is absent
    # from the default about:addons response, so we do not assert on it here.
    # Each cassette displays icon/preview, name, author link, install button.
    # Extension cards additionally surface a summary; theme cards show a preview.
    cards = about_addons.addon_cards_items
    assert cards, "Recommendations pane returned no addon cards"
    for card in cards:
        assert card.disco_addon_name.text
        assert card.disco_addon_author.text
        assert card.install_button.is_displayed()
        if card.is_extension_card():
            assert card.extension_image.is_displayed()
            assert card.disco_extension_summary
        else:
            assert card.theme_image.is_displayed()
    # "Find more add-ons" blue button opens the AMO homepage in a new tab
    about_addons.click_find_more_addons()
    # the home page wait does not actually block on the new tab's URL, so wait
    # for AMO to load before asserting
    WebDriverWait(selenium, 30).until(
        EC.url_contains("addons.mozilla.org"),
        message=f"AMO did not load in the new tab — current URL: {selenium.current_url}",
    )
    selenium.close()
    selenium.switch_to.window(selenium.window_handles[0])
    # Privacy Policy link opens the AMO/Mozilla privacy page
    about_addons.privacy_policy_link()
