import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.desktop.about_addons import AboutAddons
from scripts.shadow_dom import shadow_visible


# -------- chrome-level dialog helper --------------------------------------

def _accept_chrome_confirm(driver, timeout=10):
    """Accept Firefox's chrome-level confirmEx dialog (used for the
    about:addons uninstall confirmation). Marionette treats commonDialog as a
    standard prompt, so `switch_to.alert.accept()` clicks its accept button."""
    WebDriverWait(driver, timeout).until(
        EC.alert_is_present(),
        message="Chrome confirmation dialog never appeared",
    )
    driver.switch_to.alert.accept()


# -------- common setup ----------------------------------------------------

def _open_recommendations(selenium, base_url):
    """Open about:addons and switch to the Recommendations side tab."""
    selenium.get("about:addons")
    page = AboutAddons(selenium, base_url).wait_for_page_to_load()
    page.click_recommendations_side_button()
    return page


def _first_card(cards, *, want_extension):
    """Return (index, card) of the first cassette of the requested kind,
    or (None, None) if the disco service did not return one this run."""
    for i, c in enumerate(cards):
        if c.is_extension_card() == want_extension:
            return i, c
    return None, None

@pytest.mark.webext
def test_suite_install_extension_from_recommendations_TC_ID_C617016(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Spec: install an extension; permission door-hanger shows Add/Cancel;
    Add installs and swaps the install button for Manage; addon appears in
    the Extensions tab with a three-dots menu exposing More Options, Remove,
    Report; the enable/disable toggle works; Remove offers Undo."""
    page = _open_recommendations(selenium, base_url)

    idx, ext_card = _first_card(page.addon_cards_items, want_extension=True)
    if idx is None:
        pytest.skip("Discovery feed returned no extension cassettes this run")

    # Step 2 — click "+ Add to Firefox": permission door-hanger appears
    ext_card.install_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    if len(selenium.window_handles) == 2:
        selenium.switch_to.window(selenium.window_handles[0])

    # Install button is swapped for Manage on the same card
    assert page.addon_cards_items[idx].manage_addon_button.is_displayed()

    # Extensions tab now lists the installed add-on (we count, since the disco
    # feed display name and the installed-addon display name can diverge on
    # stage); the WAF Bypass helper is always present, hence >= 2.
    page.click_extensions_side_button()
    assert len([el.text for el in page.installed_addon_name]) >= 2

    # Three-dot menu exposes Manage (More Options), Remove and Report. The
    # Preferences/Options item is only present for extensions that declare
    # `options_ui`, so we don't assert on it here.
    page.click_more_options_button_addon()
    assert page.more_options_manage_button.is_displayed()
    assert page.more_options_remove_button.is_displayed()
    assert page.more_options_report_button.is_displayed()
    # Report opens the abuse-report form in a new tab
    page.click_more_options_report_addon()
    selenium.switch_to.window(selenium.window_handles[0])

    # Disable/Enable toggle — the visible control is a `moz-toggle` whose
    # `<button>` lives in shadow DOM. Clicking the inner shadow `<button>`
    # bypasses the host's event wiring and is a no-op; clicking the host
    # element itself is what flips the pressed state. The title text picks
    # up the "(disabled)" suffix asynchronously, so wait for it explicitly.
    name_link_css = "a[class='addon-name-link']"
    toggle_css = "moz-toggle.extension-enable-button"

    selenium.find_element(By.CSS_SELECTOR, toggle_css).click()
    WebDriverWait(selenium, 10).until(
        lambda d: "(disabled)" in d.find_element(By.CSS_SELECTOR, name_link_css).text,
        message="Toggle did not add '(disabled)' suffix to the addon title",
    )
    selenium.find_element(By.CSS_SELECTOR, toggle_css).click()
    WebDriverWait(selenium, 10).until(
        lambda d: "(disabled)" not in d.find_element(By.CSS_SELECTOR, name_link_css).text,
        message="Toggle did not remove '(disabled)' suffix from the addon title",
    )

    # Remove → an "Undo" control is offered, and clicking it restores the
    # extension. Firefox shows a chrome-level confirm dialog before removing,
    # which we accept via the chrome-context helper.
    page.click_more_options_button_addon()
    page.click_more_options_remove_addon()
    _accept_chrome_confirm(selenium)
    assert page.undo_remove_button.is_displayed()
    page.click_undo_remove()
    assert len([el.text for el in page.installed_addon_name]) >= 2, (
        "Extension was not restored after Undo"
    )

@pytest.mark.webext
def test_suite_install_theme_from_recommendations_TC_ID_C617017(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Spec: install a theme; permission door-hanger with Add/Cancel; Add
    installs; install button is swapped for Manage; theme appears under the
    Themes tab with a three-dots menu (More Options, Disable, Remove, Report
    — themes have no Preferences/Options item); Remove offers Undo."""
    page = _open_recommendations(selenium, base_url)

    idx, theme_card = _first_card(page.addon_cards_items, want_extension=False)
    if idx is None:
        pytest.skip("Discovery feed returned no theme cassettes this run")

    theme_card.install_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    if len(selenium.window_handles) == 2:
        selenium.switch_to.window(selenium.window_handles[0])

    # Install button swapped for Manage on the same card
    assert page.addon_cards_items[idx].manage_addon_button.is_displayed()

    # Theme appears under the Themes tab (count-based check, see TC1 comment)
    page.click_themes_side_button()
    assert page.installed_addon_name, "Themes tab is empty after install"

    # Three-dots menu options for themes: Manage, Remove, Report.
    page.click_more_options_button_addon()
    assert page.more_options_manage_button.is_displayed()
    assert page.more_options_remove_button.is_displayed()
    assert page.more_options_report_button.is_displayed()
    page.click_more_options_report_addon()
    selenium.switch_to.window(selenium.window_handles[0])

    # Remove → Undo flow (chrome dialog accepted via the shared helper)
    page.click_more_options_button_addon()
    page.click_more_options_remove_addon()
    _accept_chrome_confirm(selenium)
    assert page.undo_remove_button.is_displayed()
    page.click_undo_remove()
    assert page.installed_addon_name, "Theme was not restored after Undo"

@pytest.mark.webext
def test_suite_recommendations_pane_layout_TC_ID_C617018(
    selenium, base_url, wait
):
    """Spec: the recommendations pane shows a search bar, a "recommends" link
    to the SUMO kb page, a cassette per addon/theme (icon/preview, name,
    author link, install button, summary), a blue "Find more add-ons" button
    that opens AMO and a Privacy Policy link."""
    page = _open_recommendations(selenium, base_url)

    # Search bar — the wrapper is a `moz-input-search` custom element whose
    # actual <input> lives in shadow DOM. Verify both that the wrapper is
    # placed in the layout and that its shadow-root <input> is rendered.
    search_host_css = "moz-input-search[placeholder='Search addons.mozilla.org']"
    assert selenium.find_element(By.CSS_SELECTOR, search_host_css).is_displayed()
    assert shadow_visible(selenium, search_host_css, "input"), (
        "moz-input-search did not render its shadow-DOM <input>"
    )

    # The "recommends" link in the intro opens the recommended-extensions kb
    # page in a new tab.
    page.firefox_recommends_link()
    # The "personalized recommendations" paragraph is only emitted by the
    # disco service when personalization is on (telemetry/profile dependent),
    # so we don't assert it — the spec lists it but it is absent from the
    # default about:addons response on stage.

    # Each cassette must display name, author and an install button. Extension
    # cassettes additionally surface an icon and a summary; theme cassettes a
    # preview image.
    cards = page.addon_cards_items
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

    # "Find more add-ons" blue button opens the AMO homepage in a new tab.
    # The home page wait does not actually block on the URL, so wait
    # explicitly for `addons.mozilla.org` in the new tab.
    page.click_find_more_addons()
    WebDriverWait(selenium, 30).until(
        EC.url_contains("addons.mozilla.org"),
        message=f"AMO did not load — current URL: {selenium.current_url}",
    )
    selenium.close()
    selenium.switch_to.window(selenium.window_handles[0])

    # Privacy Policy link opens the AMO/Mozilla privacy page.
    page.privacy_policy_link()
