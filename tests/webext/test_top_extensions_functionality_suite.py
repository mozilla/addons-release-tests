import time

import pytest

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.desktop.about_addons import AboutAddons

TOP_N_EXTENSIONS = 3

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

@pytest.mark.webext
def test_suite_top_listed_extensions_install(
    selenium, base_url, firefox, firefox_notifications, wait
):
    """Install the first ``TOP_N_EXTENSIONS`` extension cassettes returned
    by the about:addons Recommendations feed (Firefox's curated "top
    extensions"). Each install must complete without error and the
    Extensions tab must end up containing one entry per install, on top of
    the always-present WAF Bypass helper that the conftest ships.

    Not every cassette is guaranteed installable on stage — some xpis return
    HTTP errors and surface `addon-install-failed-notification` instead of
    the confirmation door-hanger. The install loop polls for either the
    confirmation or a failure popup and only counts confirmations toward
    ``installs_done``; failed candidates are dismissed and the next card is
    tried.
    """
    from selenium.webdriver.common.by import By

    def _active_install_popup_id():
        """Return the id of the currently-displayed install popupnotification,
        or ``None`` when no install popup is visible. Polled to disambiguate
        the confirmation/permissions doorhanger from the failure popup."""
        with selenium.context(selenium.CONTEXT_CHROME):
            for n in selenium.find_elements(
                By.CSS_SELECTOR, "#notification-popup popupnotification"
            ):
                if n.get_property("hidden"):
                    continue
                pid = n.get_property("id")
                if pid in (
                    "addon-install-confirmation-notification",
                    "addon-webext-permissions-notification",
                    "addon-install-failed-notification",
                ):
                    return pid
        return None

    def _dismiss_failed_install():
        with selenium.context(selenium.CONTEXT_CHROME):
            for n in selenium.find_elements(
                By.CSS_SELECTOR, "#notification-popup popupnotification"
            ):
                if n.get_property("id") == "addon-install-failed-notification":
                    try:
                        n.find_element(
                            By.CSS_SELECTOR, ".popup-notification-closebutton"
                        ).click()
                    except Exception:
                        pass
                    return

    selenium.get("about:addons")
    page = AboutAddons(selenium, base_url).wait_for_page_to_load()
    page.click_recommendations_side_button()

    # The cards re-render after each install (the install button is replaced
    # by Manage and indices can shift). Each iteration re-scans the feed and
    # picks the first extension cassette whose install button is still
    # visible — that's the "next un-installed" cassette regardless of where
    # disco moved it.
    installs_done = 0
    tried_names = set()
    while installs_done < TOP_N_EXTENSIONS:
        next_card = None
        next_name = None
        for c in page.addon_cards_items:
            if not c.is_extension_card():
                continue
            # An un-installed cassette keeps its install button visible; an
            # installed one flips it to hidden and shows Manage instead.
            install_btn = c.find_element(
                *c._addon_install_button_locator
            )
            if install_btn.get_attribute("hidden") is not None:
                continue
            name = c.disco_addon_name.text
            if name in tried_names:
                continue
            next_card = c
            next_name = name
            break
        assert next_card is not None, (
            f"No more un-installed extension cassettes after installing "
            f"{installs_done} (tried {len(tried_names)} candidates: {tried_names})"
        )
        tried_names.add(next_name)

        next_card.install_button.click()
        # Poll until Firefox commits to one of the install terminal states.
        # ``addon-progress-notification`` is a transient indicator we ignore.
        # Confirmation = happy path; failure = stage cannot serve this xpi —
        # dismiss and move on to the next candidate.
        popup_id = WebDriverWait(selenium, 20).until(
            lambda d: _active_install_popup_id(),
            message="Neither confirmation nor failure popup appeared after install click",
        )
        if popup_id == "addon-install-failed-notification":
            _dismiss_failed_install()
            # Refresh so the disco feed re-renders with the failed candidate
            # back in its uninstalled state, then try the next card.
            selenium.get("about:addons")
            page = AboutAddons(selenium, base_url).wait_for_page_to_load()
            page.click_recommendations_side_button()
            continue

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
