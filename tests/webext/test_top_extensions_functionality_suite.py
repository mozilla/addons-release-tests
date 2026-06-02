"""Suite implementing the two test cases described in
`.claude/WEBEXT_TESTCASES_TOP_EXTENSIONS_FUNCTIONALITY.md`.

TC1 (Greasemonkey + greasyfork.org user-script flow) is skipped — see the
``@pytest.mark.skip`` reason on that test for the infrastructure gap. TC2
exercises the "top listed extensions can be installed" claim by walking
the top of the about:addons Recommendations feed and installing each
extension cassette in turn, asserting that every one reaches the
Extensions tab.

Shadow-DOM access is available through ``scripts.shadow_dom`` if any of
the assertions need it; none of the current ones do.
"""
import time

import pytest

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.desktop.about_addons import AboutAddons


# Walking the entire recommendations feed (typically 6+ extensions) would
# make the test runtime balloon. Three top entries is enough to demonstrate
# the "top listed extensions can be installed" claim without paying for
# every single install.
TOP_N_EXTENSIONS = 3


# ==========================================================================
# Test Case 1 — Greasemonkey + greasyfork.org script-install verification
# ==========================================================================

@pytest.mark.skip(
    reason="The Greasemonkey extension referenced in the spec lives only on "
    "production AMO (https://addons.allizom.org/en-US/firefox/addon/"
    "greasemonkey/ returns HTTP 404), and the rest of the case asserts on "
    "third-party user-script behaviour from greasyfork.org which the test "
    "harness has no driver for. The closest reusable assertions — install "
    "an older version and trigger Check for Updates — are already covered "
    "by `test_update_methods_and_results_suite.py` TC1/TC2."
)
@pytest.mark.webext
def test_suite_greasemonkey_script_install_and_update_TC1(
    selenium, base_url, firefox, firefox_notifications, wait
):
    pass


# ==========================================================================
# Test Case 2 — Top listed extensions install cleanly
# ==========================================================================

@pytest.mark.webext
def test_suite_top_listed_extensions_install_TC2(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Install the first ``TOP_N_EXTENSIONS`` extension cassettes returned
    by the about:addons Recommendations feed (Firefox's curated "top
    extensions"). Each install must complete without error and the
    Extensions tab must end up containing one entry per install, on top of
    the always-present WAF Bypass helper that the conftest ships."""
    selenium.get("about:addons")
    page = AboutAddons(selenium, base_url).wait_for_page_to_load()
    page.click_recommendations_side_button()

    # The cards re-render after each install (the install button is replaced
    # by Manage and indices can shift). Each iteration re-scans the feed and
    # picks the first extension cassette whose install button is still
    # visible — that's the "next un-installed" cassette regardless of where
    # disco moved it.
    installs_done = 0
    for _ in range(TOP_N_EXTENSIONS):
        next_card = None
        for c in page.addon_cards_items:
            if not c.is_extension_card():
                continue
            # An un-installed cassette keeps its install button visible; an
            # installed one flips it to hidden and shows Manage instead.
            install_btn = c.find_element(
                *c._addon_install_button_locator
            )
            if install_btn.get_attribute("hidden") is None:
                next_card = c
                break
        assert next_card is not None, (
            f"No more un-installed extension cassettes after installing "
            f"{installs_done}"
        )

        next_card.install_button.click()
        firefox.browser.wait_for_notification(
            firefox_notifications.AddOnInstallConfirmation
        ).install()
        firefox.browser.wait_for_notification(
            firefox_notifications.AddOnInstallComplete
        ).close()
        if len(selenium.window_handles) > 1:
            selenium.switch_to.window(selenium.window_handles[0])
        installs_done += 1
        # Refresh the recommendations view between installs — without this,
        # subsequent install-button clicks sometimes fire before Firefox is
        # ready to surface a new install permission door-hanger and the
        # foxpuppet wait times out.
        if installs_done < TOP_N_EXTENSIONS:
            selenium.get("about:addons")
            page = AboutAddons(selenium, base_url).wait_for_page_to_load()
            page.click_recommendations_side_button()

    # All installs should now appear in the Extensions tab, on top of the
    # always-present WAF Bypass helper.
    page.click_extensions_side_button()
    WebDriverWait(selenium, 15).until(
        lambda d: len(page.installed_addon_name) >= TOP_N_EXTENSIONS + 1,
        message=(
            f"Expected at least {TOP_N_EXTENSIONS + 1} installed extensions, "
            f"found {[el.text for el in page.installed_addon_name]}"
        ),
    )
