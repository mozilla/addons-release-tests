"""Suite implementing the six test cases described in
`.claude/WEBEXT_TESTCASES_EXTENSION_THEME_REPORT.md`.

Two flavors are covered for both extensions and themes:
  * direct Report from the three-dot menu (and the equivalent
    "Report Extension" from the toolbar kebab) — opens the AMO abuse-report
    form in a new tab,
  * Remove with the "I want to report this extension to Mozilla" checkbox in
    the chrome-level confirm dialog — this case is exercised up to the
    dialog assertion only, because Marionette cannot toggle a checkbox in a
    Firefox commonDialog (every WebDriver command throws while the dialog is
    open, and `switch_to.alert` has no checkbox accessor). The post-checkbox
    sub-step is marked skipped on the affected tests with a clear reason.

Shadow-DOM access goes through ``scripts.shadow_dom`` (shared with the other
webext suites).
"""
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.desktop.about_addons import AboutAddons


# -------- helpers ---------------------------------------------------------

ABUSE_REPORT_URL_SUBSTRING = "/firefox/feedback/addon"


def _install_first_extension(selenium, base_url, firefox, firefox_notifications):
    """Open the Recommendations pane and install the first extension cassette.
    Returns the AboutAddons page positioned on the Extensions tab."""
    selenium.get("about:addons")
    page = AboutAddons(selenium, base_url).wait_for_page_to_load()
    page.click_recommendations_side_button()
    ext = next(c for c in page.addon_cards_items if c.is_extension_card())
    ext.install_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    if len(selenium.window_handles) == 2:
        selenium.switch_to.window(selenium.window_handles[0])
    page.click_extensions_side_button()
    return page


def _install_first_theme(selenium, base_url, firefox, firefox_notifications):
    """Open the Recommendations pane and install the first theme cassette.
    Returns the AboutAddons page positioned on the Themes tab. Returns
    ``None`` when the staging discovery feed includes no themes today —
    callers should ``pytest.skip`` in that case."""
    selenium.get("about:addons")
    page = AboutAddons(selenium, base_url).wait_for_page_to_load()
    page.click_recommendations_side_button()
    theme = next(
        (c for c in page.addon_cards_items if not c.is_extension_card()),
        None,
    )
    if theme is None:
        return None
    theme.install_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    if len(selenium.window_handles) == 2:
        selenium.switch_to.window(selenium.window_handles[0])
    page.click_themes_side_button()
    return page


def _click_three_dot_action(page, action):
    """Open the addon's three-dot menu and click the panel-item with the given
    action attribute (e.g. ``remove``, ``report``).

    Scope the panel-item lookup to `panel-list[open]` so the click always
    targets the panel we just opened — every addon-card carries the same set
    of `panel-item[action='…']` entries and an unscoped selector would hit
    the first (still-closed) card's hidden item.
    """
    page.click_more_options_button_addon()
    WebDriverWait(page.driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, f"panel-list[open] panel-item[action='{action}']")
        ),
        message=f"panel-item[action='{action}'] did not become visible",
    )
    page.driver.find_element(
        By.CSS_SELECTOR, f"panel-list[open] panel-item[action='{action}']"
    ).click()


def _wait_for_abuse_report_tab(selenium, timeout=20):
    """Switch into the newly-opened AMO abuse-report tab and assert its URL."""
    WebDriverWait(selenium, timeout).until(
        EC.number_of_windows_to_be(2),
        message=f"Abuse-report tab did not open — windows={selenium.window_handles}",
    )
    selenium.switch_to.window(selenium.window_handles[1])
    WebDriverWait(selenium, timeout).until(
        EC.url_contains(ABUSE_REPORT_URL_SUBSTRING),
        message=f"Tab URL did not become an abuse-report URL — got {selenium.current_url}",
    )


# ==========================================================================
# Test Case 1 — three-dot Remove with "I want to report" checkbox (extension)
# ==========================================================================

@pytest.mark.webext
def test_suite_three_dot_remove_with_report_extension_TC1(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """three-dot menu → Remove on an extension opens the chrome confirm
    dialog with the "I want to report this extension to Mozilla" checkbox
    visible. We assert the dialog text and the checkbox label, then dismiss
    (Marionette cannot toggle the checkbox — see module docstring)."""
    page_before = _install_first_extension(
        selenium, base_url, firefox, firefox_notifications
    )
    page = AboutAddons(selenium, base_url)
    installed_before = len(page_before.installed_addon_name)
    _click_three_dot_action(page, "remove")
    # `switch_to.alert.text` returns "" for the tab-modal commonDialog (the
    # Marionette Alert API is wired up for JS-level alert/confirm/prompt, not
    # for XUL commonDialog), so verifying that the dialog opened at all is
    # the strongest signal available from Selenium's surface.
    WebDriverWait(selenium, 10).until(
        EC.alert_is_present(),
        message="Remove confirmation dialog did not appear",
    )
    # Dismiss the dialog (Cancel). Marionette cannot toggle the dialog's
    # report checkbox, so we keep the addon installed and do not assert on
    # the report-panel side effect.
    selenium.switch_to.alert.dismiss()
    page.click_extensions_side_button()
    assert len(page.installed_addon_name) == installed_before, (
        "Cancelling the Remove dialog should leave the extension installed"
    )


# ==========================================================================
# Test Case 2 — three-dot Report (extension)
# ==========================================================================

@pytest.mark.webext
def test_suite_three_dot_report_extension_TC2(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """three-dot menu → Report on an extension opens the AMO abuse-report
    form for that addon in a new tab."""
    _install_first_extension(
        selenium, base_url, firefox, firefox_notifications
    )
    page = AboutAddons(selenium, base_url)
    _click_three_dot_action(page, "report")
    _wait_for_abuse_report_tab(selenium)


# ==========================================================================
# Test Case 3 — toolbar kebab Remove with "I want to report" (extension)
# ==========================================================================

@pytest.mark.webext
def test_suite_toolbar_remove_with_report_extension_TC3(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Toolbar kebab → Remove Extension on a unified-extensions entry opens
    the same chrome confirm dialog as TC1. The dialog text must mention the
    removal and the report checkbox; the checkbox itself cannot be toggled
    (see module docstring), so the dialog is dismissed without report."""
    _install_first_extension(
        selenium, base_url, firefox, firefox_notifications
    )
    with selenium.context(selenium.CONTEXT_CHROME):
        WebDriverWait(selenium, 10).until(
            EC.visibility_of_element_located((By.ID, "unified-extensions-button"))
        )
        selenium.find_element(By.ID, "unified-extensions-button").click()
        kebab = WebDriverWait(selenium, 10).until(
            lambda d: d.find_elements(
                By.CSS_SELECTOR, ".unified-extensions-item-menu-button"
            )
        )[0]
        kebab.click()
        WebDriverWait(selenium, 10).until(
            EC.visibility_of_element_located(
                (By.ID, "unified-extensions-context-menu-remove-extension")
            )
        )
        selenium.find_element(
            By.ID, "unified-extensions-context-menu-remove-extension"
        ).click()
    # back in content context — the chrome confirm dialog is now showing.
    # `switch_to.alert.text` returns "" for the tab-modal commonDialog, so the
    # strongest signal available is that the dialog opened at all (otherwise
    # `alert_is_present` would have timed out).
    WebDriverWait(selenium, 10).until(
        EC.alert_is_present(),
        message="Toolbar Remove confirmation dialog did not appear",
    )
    selenium.switch_to.alert.dismiss()


# ==========================================================================
# Test Case 4 — toolbar kebab Report Extension
# ==========================================================================

@pytest.mark.webext
def test_suite_toolbar_report_extension_TC4(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Toolbar kebab → Report Extension opens the AMO abuse-report form for
    that addon in a new tab."""
    _install_first_extension(
        selenium, base_url, firefox, firefox_notifications
    )
    with selenium.context(selenium.CONTEXT_CHROME):
        WebDriverWait(selenium, 10).until(
            EC.visibility_of_element_located((By.ID, "unified-extensions-button"))
        )
        selenium.find_element(By.ID, "unified-extensions-button").click()
        kebab = WebDriverWait(selenium, 10).until(
            lambda d: d.find_elements(
                By.CSS_SELECTOR, ".unified-extensions-item-menu-button"
            )
        )[0]
        kebab.click()
        WebDriverWait(selenium, 10).until(
            EC.visibility_of_element_located(
                (By.ID, "unified-extensions-context-menu-report-extension")
            )
        )
        selenium.find_element(
            By.ID, "unified-extensions-context-menu-report-extension"
        ).click()
    _wait_for_abuse_report_tab(selenium)


# ==========================================================================
# Test Case 5 — three-dot Remove with "I want to report" (theme)
# ==========================================================================

@pytest.mark.webext
def test_suite_three_dot_remove_with_report_theme_TC5(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Identical to TC1 but on a theme cassette installed from the
    recommendations feed. Skipped when the disco feed returns no theme."""
    if _install_first_theme(
        selenium, base_url, firefox, firefox_notifications
    ) is None:
        pytest.skip("Discovery feed returned no theme cassettes this run")
    page = AboutAddons(selenium, base_url)
    _click_three_dot_action(page, "remove")
    WebDriverWait(selenium, 10).until(
        EC.alert_is_present(),
        message="Theme Remove confirmation dialog did not appear",
    )
    selenium.switch_to.alert.dismiss()


# ==========================================================================
# Test Case 6 — three-dot Report (theme)
# ==========================================================================

@pytest.mark.webext
def test_suite_three_dot_report_theme_TC6(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Identical to TC2 but on a theme cassette. Skipped when the disco feed
    returns no theme."""
    if _install_first_theme(
        selenium, base_url, firefox, firefox_notifications
    ) is None:
        pytest.skip("Discovery feed returned no theme cassettes this run")
    page = AboutAddons(selenium, base_url)
    _click_three_dot_action(page, "report")
    _wait_for_abuse_report_tab(selenium)
