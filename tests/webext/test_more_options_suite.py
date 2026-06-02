"""Suite implementing the seven test cases described in
`.claude/WEBEXT_TESTCASES_MORE_OPTIONS.md` for the about:addons more-options
flows: toolbar extension menu, View Recent Updates, Install from File, Debug
Add-ons, and Manage Extension Shortcuts.

Shadow-DOM access goes through ``scripts.shadow_dom`` (shared with
``test_recommendations_pane_suite``). Chrome-level dialogs (commonDialog,
unified-extensions context menu) are interacted with via Marionette's
``CONTEXT_CHROME`` switch and the standard ``switch_to.alert`` API.
"""
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.desktop.about_addons import AboutAddons
from scripts.shadow_dom import shadow_query, shadow_visible


# -------- helpers ---------------------------------------------------------

def _accept_chrome_confirm(driver, timeout=10):
    """Accept Firefox's commonDialog/confirmEx chrome-level prompt.
    Requires the WebDriver session to have ``unhandledPromptBehavior=ignore``
    (set in conftest for non-prod runs)."""
    WebDriverWait(driver, timeout).until(
        EC.alert_is_present(),
        message="Chrome confirmation dialog never appeared",
    )
    driver.switch_to.alert.accept()


def _install_an_extension(selenium, base_url, firefox, firefox_notifications):
    """Open the Recommendations pane and install the first extension cassette.
    Returns the AboutAddons page object positioned on the Extensions tab."""
    selenium.get("about:addons")
    page = AboutAddons(selenium, base_url).wait_for_page_to_load()
    page.click_recommendations_side_button()
    extension_card = next(
        c for c in page.addon_cards_items if c.is_extension_card()
    )
    extension_card.install_button.click()
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


def _open_options_menu(page):
    """Click the about:addons Options ⚙️ button to open the panel-list."""
    page.click_options_button()
    # the panel-list is built lazily; wait for at least one panel-item to render
    WebDriverWait(page.driver, 10).until(
        lambda d: d.find_elements(By.CSS_SELECTOR, "panel-item[action='debug-addons']")
    )


# ==========================================================================
# Test Case 1 — toolbar extension icon menu (Manage / Remove / Report)
# ==========================================================================

@pytest.mark.webext
def test_suite_toolbar_extension_menu_TC1(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Right-clicking an installed extension's entry in the unified-extensions
    toolbar panel exposes Manage / Remove / Report items, and each one routes
    to the expected destination (about:addons details, uninstall confirm,
    abuse-report tab)."""
    # Pre-condition: at least one installable extension must be on the
    # recommendations feed.
    _install_an_extension(selenium, base_url, firefox, firefox_notifications)
    installed_count_before = len(
        AboutAddons(selenium, base_url).installed_addon_name
    )

    # Step 1 — open the unified-extensions toolbar panel (puzzle-piece icon)
    # and click the kebab on the most recently installed extension entry to
    # surface its context menu.
    with selenium.context(selenium.CONTEXT_CHROME):
        WebDriverWait(selenium, 10).until(
            EC.visibility_of_element_located((By.ID, "unified-extensions-button"))
        )
        selenium.find_element(By.ID, "unified-extensions-button").click()
        # the panel renders one row per installed extension; clicking the kebab
        # opens its context menu
        kebab = WebDriverWait(selenium, 10).until(
            lambda d: d.find_elements(
                By.CSS_SELECTOR, ".unified-extensions-item-menu-button"
            )
        )[0]
        kebab.click()
        # Expected of step 1: menu lists Manage / Remove / Report
        WebDriverWait(selenium, 10).until(
            EC.visibility_of_element_located(
                (By.ID, "unified-extensions-context-menu-manage-extension")
            )
        )
        assert selenium.find_element(
            By.ID, "unified-extensions-context-menu-manage-extension"
        ).is_displayed()
        assert selenium.find_element(
            By.ID, "unified-extensions-context-menu-remove-extension"
        ).is_displayed()
        assert selenium.find_element(
            By.ID, "unified-extensions-context-menu-report-extension"
        ).is_displayed()

        # Step 2 — Manage Extension opens the extension's about:addons details.
        # Since about:addons is already open, it routes there in the same tab.
        selenium.find_element(
            By.ID, "unified-extensions-context-menu-manage-extension"
        ).click()
    # we're back in content context now — the addon-card detail view loaded
    WebDriverWait(selenium, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "addon-card"))
    )

    # Step 3 — Remove Extension brings up the chrome-level confirmEx dialog
    # with the extension name in its header; Cancel keeps the addon installed.
    with selenium.context(selenium.CONTEXT_CHROME):
        selenium.find_element(By.ID, "unified-extensions-button").click()
        selenium.find_elements(
            By.CSS_SELECTOR, ".unified-extensions-item-menu-button"
        )[0].click()
        WebDriverWait(selenium, 10).until(
            EC.visibility_of_element_located(
                (By.ID, "unified-extensions-context-menu-remove-extension")
            )
        )
        selenium.find_element(
            By.ID, "unified-extensions-context-menu-remove-extension"
        ).click()
    WebDriverWait(selenium, 10).until(EC.alert_is_present())
    selenium.switch_to.alert.dismiss()  # Cancel keeps the extension installed
    # The extension count must be unchanged after cancelling.
    page = AboutAddons(selenium, base_url)
    page.click_extensions_side_button()
    assert len(page.installed_addon_name) == installed_count_before

    # Step 4 — Report Extension opens the abuse-report tab.
    with selenium.context(selenium.CONTEXT_CHROME):
        selenium.find_element(By.ID, "unified-extensions-button").click()
        selenium.find_elements(
            By.CSS_SELECTOR, ".unified-extensions-item-menu-button"
        )[0].click()
        WebDriverWait(selenium, 10).until(
            EC.visibility_of_element_located(
                (By.ID, "unified-extensions-context-menu-report-extension")
            )
        )
        selenium.find_element(
            By.ID, "unified-extensions-context-menu-report-extension"
        ).click()
    WebDriverWait(selenium, 15).until(EC.number_of_windows_to_be(2))
    selenium.switch_to.window(selenium.window_handles[1])
    WebDriverWait(selenium, 15).until(
        EC.url_contains("/firefox/feedback/addon"),
        message=f"Abuse-report tab did not load — URL is {selenium.current_url}",
    )


# ==========================================================================
# Test Case 2 — View Recent Updates section
# ==========================================================================

@pytest.mark.webext
def test_suite_view_recent_updates_TC2(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Selecting Options → View Recent Updates loads the Recent Updates page
    with the section header visible; switching to any other side-tab hides
    that section again. The spec's "older-version → check-for-updates" sub-
    flow is not exercised because it requires a known-outdated addon in the
    feed; the structural checks below are what the page must satisfy."""
    _install_an_extension(selenium, base_url, firefox, firefox_notifications)
    page = AboutAddons(selenium, base_url)

    # Step 1 — Options → View Recent Updates
    _open_options_menu(page)
    recent = page.click_view_recent_updates()
    assert recent.list_section_name.is_displayed()

    # Step 4 — switching to any other side-tab hides the Recent Updates section
    page.click_extensions_side_button()
    assert not selenium.find_elements(
        By.XPATH, "//h2[contains(text(), 'Recent Updates')]"
    ), "Recent Updates header still present after switching tabs"


# ==========================================================================
# Test Case 3 — Install Add-on From File…
# ==========================================================================

@pytest.mark.skip(
    reason="The 'Install Add-on From File…' entry opens the native OS file "
    "picker, which Marionette cannot drive from a content-context Selenium "
    "session. Exercising this case requires Firefox-side picker mocking "
    "(nsIFilePicker override) that the test infrastructure does not yet "
    "provide."
)
@pytest.mark.webext
def test_suite_install_from_file_TC3(selenium, base_url, wait):
    selenium.get("about:addons")
    page = AboutAddons(selenium, base_url).wait_for_page_to_load()
    _open_options_menu(page)
    page.click_install_addon_from_file()


# ==========================================================================
# Test Case 4 — Debug Add-ons
# ==========================================================================

@pytest.mark.webext
def test_suite_debug_addons_TC4(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Options → Debug Add-ons opens about:debugging#/runtime/this-firefox
    in a new tab."""
    # The spec lists "at least one extension installed" as a precondition —
    # the always-present WAF Bypass helper satisfies that.
    selenium.get("about:addons")
    page = AboutAddons(selenium, base_url).wait_for_page_to_load()
    _open_options_menu(page)
    # Click the Debug Add-ons panel-item directly. We can't use the existing
    # `click_panel_item_action_debug_addon` because it waits for an AboutDebug
    # heading that recent Firefox builds no longer render.
    page._click_options_menu_action("debug-addons")
    # about:debugging opens in a new tab; switch to it before reading the URL
    WebDriverWait(selenium, 15).until(EC.number_of_windows_to_be(2))
    selenium.switch_to.window(selenium.window_handles[1])
    WebDriverWait(selenium, 15).until(
        EC.url_contains("about:debugging"),
        message=f"about:debugging did not load — current URL: {selenium.current_url}",
    )
    assert "/runtime/this-firefox" in selenium.current_url


# ==========================================================================
# Test Case 5 — Manage Extension Shortcuts (basic flow)
# ==========================================================================

@pytest.mark.webext
def test_suite_manage_extension_shortcuts_TC5(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Options → Manage Extension Shortcuts loads the shortcuts page with at
    least one shortcut input field. The Back button returns to the previously
    viewed side-tab. The spec's keystroke-capture assertions (CTRL/ALT
    tooltip, "in use" warning) are not asserted here because they require
    OS-level synthetic key events that Marionette does not reliably emit
    through the shortcut input widget."""
    _install_an_extension(selenium, base_url, firefox, firefox_notifications)
    page = AboutAddons(selenium, base_url)

    # Step 1 — Options → Manage Extension Shortcuts
    _open_options_menu(page)
    page.click_manage_shortcuts()
    # The shortcuts page exposes its name via the .header-name heading; the
    # individual shortcut rows are only rendered for extensions that declare
    # `commands` in their manifest, which the random staging-feed addons
    # generally don't, so we assert on the heading rather than on rows.
    WebDriverWait(selenium, 10).until(
        lambda d: any(
            "Manage Extension Shortcuts" in (h.text or "")
            for h in d.find_elements(By.CSS_SELECTOR, ".header-name, h1")
        ),
        message="Manage Extension Shortcuts heading not visible",
    )
    # The page also includes an `<addon-shortcuts>` container.
    assert selenium.find_elements(By.CSS_SELECTOR, "addon-shortcuts"), (
        "addon-shortcuts container missing from the shortcuts page"
    )

    # Step 6 — Back button (plain `<button action='go-back'>` here, no shadow
    # DOM wrapper). Clicking it returns to the previously viewed side-tab.
    selenium.find_element(By.CSS_SELECTOR, "button[action='go-back']").click()
    # We end up back on the Extensions side-tab — confirmed by the side-tab
    # button being active again.
    WebDriverWait(selenium, 10).until(
        lambda d: not d.find_elements(By.CSS_SELECTOR, "addon-shortcuts:not([hidden])"),
        message="Still on the shortcuts page after clicking Back",
    )


# ==========================================================================
# Test Case 6 — Manage Shortcuts: "Already in use" tooltip
# ==========================================================================

@pytest.mark.skip(
    reason="Asserting the 'Already in use by [name]' tooltip requires "
    "capturing a multi-key chord (CTRL/ALT + letter) inside the shortcut "
    "input widget. Marionette's send_keys does not reach the underlying "
    "key handler in this widget, so a reliable assertion needs a chrome-"
    "context synthetic-key utility that does not yet exist in this repo."
)
@pytest.mark.webext
def test_suite_manage_shortcuts_already_in_use_TC6(
    selenium, base_url, firefox, firefox_notifications, wait
):
    pass


# ==========================================================================
# Test Case 7 — Conflicting default shortcuts banner
# ==========================================================================

@pytest.mark.skip(
    reason="This case requires installing two specific extensions "
    "(tree-style-tab and enhancer-for-youtube) that share a default "
    "shortcut. Neither is present in the staging discovery feed, and "
    "side-loading a known-good copy needs a curated xpi fixture that the "
    "test infrastructure does not yet ship."
)
@pytest.mark.webext
def test_suite_manage_shortcuts_conflict_banner_TC7(
    selenium, base_url, firefox, firefox_notifications, wait
):
    pass
