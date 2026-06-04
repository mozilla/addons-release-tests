import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pages.desktop.about_addons import AboutAddons
from pages.desktop.frontend.versions import Versions
from scripts.addon_install import install_older_version_via_chrome


# -------- helpers ---------------------------------------------------------

def _install_older_version_from_amo(
    selenium, base_url, firefox, firefox_notifications, variables
):
    """Open the AMO "all versions" page for the extension referenced by
    ``addon_version_update_webext`` and install ``versions_list[1]`` — the
    spec asks for *not the latest* version so a subsequent update check
    finds a newer one.

    AMO renders an "Add to Firefox" install button only on the latest
    version card; older versions expose a plain download link. To start an
    install of the older version through the same chrome path the UI uses
    we read the XPI URL off the older card and call
    ``AddonManager.installAddonFromAOM`` from chrome context — see
    ``scripts.addon_install``.
    """
    selenium.get(variables["addon_version_update_webext"])
    versions_page = Versions(selenium, base_url).wait_for_page_to_load()
    # Read the older card's XPI URL via the same `.AddonVersionCard` markup
    # the page object exposes.
    xpi_url = selenium.execute_script(
        """
        const cards = [...document.querySelectorAll('.AddonVersionCard')];
        if (cards.length < 2) return null;
        return cards[1].querySelector('.InstallButtonWrapper-download-link')?.href;
        """
    )
    assert xpi_url, (
        f"Older version card had no download link — only "
        f"{len(versions_page.versions_list)} version cards are listed"
    )
    install_older_version_via_chrome(selenium, xpi_url)
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    if len(selenium.window_handles) > 1:
        selenium.switch_to.window(selenium.window_handles[0])


def _wait_check_for_updates_finished(selenium, timeout=20):
    """Block until the about:addons ``#updates-message`` element reports a
    finished state. The element is hidden/empty before a check; after the
    check completes it carries a ``state`` attribute (e.g. ``installed``,
    ``none-found``, ``manual-updates-found``)."""
    WebDriverWait(selenium, timeout).until(
        lambda d: bool(
            d.execute_script(
                "return document.getElementById('updates-message')"
                "?.getAttribute('state');"
            )
        ),
        message="Check for Updates did not finish — #updates-message has no state",
    )

@pytest.mark.webext
def test_suite_check_for_updates_after_older_install(
    selenium, base_url, firefox, firefox_notifications, variables, wait
):
    """Install an older version of the AMO test extension referenced by
    ``addon_version_update_webext``. Open about:addons → Extensions, click
    Options ⚙️ → Check for Updates, and assert the in-page confirmation
    (``#updates-message`` state attribute) is set."""
    _install_older_version_from_amo(
        selenium, base_url, firefox, firefox_notifications, variables
    )
    selenium.get("about:addons")
    page = AboutAddons(selenium, base_url).wait_for_page_to_load()
    page.click_extensions_side_button()
    # Options ⚙️ → Check for Updates
    page.click_options_button()
    WebDriverWait(selenium, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "panel-item[action='check-for-updates']")
        ),
    )
    page.click_check_for_updates()
    _wait_check_for_updates_finished(selenium)

@pytest.mark.webext
def test_suite_toggle_auto_update_and_check(
    selenium, base_url, firefox, firefox_notifications, variables, wait
):
    """Install an older version (same as TC1), navigate to the Extensions
    tab, then through the Options menu un-check
    "Update Add-ons Automatically" and trigger Check for Updates. The
    "un-check" action is exercised by clicking the
    ``set-update-automatically`` panel-item — the checkable item flips
    state on click, so the test asserts the ``checked`` attribute changes
    after the click before going on to verify the update check completes."""
    _install_older_version_from_amo(
        selenium, base_url, firefox, firefox_notifications, variables
    )
    selenium.get("about:addons")
    page = AboutAddons(selenium, base_url).wait_for_page_to_load()
    page.click_extensions_side_button()

    # Step 5 — toggle "Update Add-ons Automatically"
    auto_update_selector = "panel-item[action='set-update-automatically']"
    page.click_options_button()
    WebDriverWait(selenium, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, auto_update_selector))
    )
    state_before = selenium.execute_script(
        "return document.querySelector(arguments[0]).hasAttribute('checked');",
        auto_update_selector,
    )
    selenium.find_element(By.CSS_SELECTOR, auto_update_selector).click()
    # Re-open the Options menu and confirm the attribute toggled
    page.click_options_button()
    WebDriverWait(selenium, 10).until(
        lambda d: d.execute_script(
            "return document.querySelector(arguments[0]).hasAttribute('checked');",
            auto_update_selector,
        )
        != state_before,
        message="Update Add-ons Automatically toggle did not change state",
    )

    # Step 6 — Check for Updates and assert the in-page confirmation surfaces
    page.click_check_for_updates()
    _wait_check_for_updates_finished(selenium)
