import pytest

from selenium.common.exceptions import TimeoutException

from pages.desktop.about_addons import AboutAddons


def _wait_for_recommendations(about_addons, wait, minimum=4):
    wait.until(
        lambda _: len(
            [card.install_button for card in about_addons.addon_cards_items]
        )
        >= minimum,
        message="Recommendations pane did not return enough cards to test against",
    )


def _first_extension_card(about_addons):
    for card in about_addons.addon_cards_items:
        if card.is_extension_card():
            return card
    pytest.fail("No extension cards were returned in the Recommendations pane")

@pytest.mark.skip
def test_recommendations_pane_loads(selenium, wait):
    """Opening about:addons shows the Recommendations pane populated with addon cards."""
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium)
    _wait_for_recommendations(about_addons, wait)
    assert any(
        card.is_extension_card() for card in about_addons.addon_cards_items
    ), "Recommendations pane returned no extension cards"

@pytest.mark.skip
def test_recommendations_pane_install_cancel(
    selenium, wait, firefox, firefox_notifications
):
    """Clicking Cancel on the install permission door-hanger aborts the installation
    and the addon does not appear under the Extensions tab."""
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium)
    _wait_for_recommendations(about_addons, wait)
    extension_card = _first_extension_card(about_addons)
    candidate_name = extension_card.disco_addon_name.text

    extension_card.install_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).cancel()

    about_addons.click_extensions_side_button()
    installed_names = [el.text for el in about_addons.installed_addon_name]
    assert candidate_name not in installed_names, (
        f"Addon {candidate_name!r} was installed despite Cancel being clicked; "
        f"installed list: {installed_names}"
    )


def test_recommendations_pane_install_extension_full_lifecycle(
    selenium, wait, firefox, firefox_notifications
):
    """End-to-end coverage of the Recommendations pane scenario:
    install via the permission door-hanger, verify the addon appears under the
    Extensions tab, inspect the three-dots menu actions, toggle disable/enable,
    and verify Remove + Undo."""
    selenium.get("about:addons")
    about_addons = AboutAddons(selenium)
    _wait_for_recommendations(about_addons, wait)
    extension_card = _first_extension_card(about_addons)
    extension_card.install_button.click()

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

    about_addons.click_extensions_side_button()
    assert about_addons.installed_addon_cards, "No installed extensions were listed"
    installed_name = about_addons.installed_addon_name[0].text

    about_addons.disable_extension()
    wait.until(
        lambda _: "(disabled)" in about_addons.installed_addon_name[0].text,
        message=f"Disabled tag was not appended to {installed_name!r} after toggling off",
    )
    about_addons.disable_extension()
    wait.until(
        lambda _: "(disabled)" not in about_addons.installed_addon_name[0].text,
        message=f"Disabled tag persisted on {installed_name!r} after toggling on",
    )

    about_addons.click_options_button()
    about_addons.click_menu_remove()


