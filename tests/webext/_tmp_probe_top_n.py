"""Probe: trace the 2nd install in the TOP_N loop to see why the
AddOnInstallConfirmation door-hanger never shows."""
import json
import time

import pytest
from selenium.webdriver.common.by import By

from pages.desktop.about_addons import AboutAddons


def _disco_state(d):
    return d.execute_script(
        """
        return [...document.querySelectorAll('.card.addon')].map((c, i) => {
            const install = c.querySelector('button[action="install-addon"]');
            const manage = c.querySelector('button[action="manage-addon"]');
            return {
                idx: i,
                name: c.querySelector('.disco-addon-name')?.textContent.trim().slice(0, 30),
                installL10n: install?.getAttribute('data-l10n-id'),
                installHidden: install?.hasAttribute('hidden'),
                installVisible: install ? install.getBoundingClientRect().width > 0 : null,
                manageHidden: manage?.hasAttribute('hidden'),
            };
        });
        """
    )


def _notif_state(driver):
    with driver.context(driver.CONTEXT_CHROME):
        return driver.execute_script(
            """
            const notif = document.getElementById('notification-popup');
            if (!notif) return null;
            const ids = [...notif.querySelectorAll('popupnotification')].map(p => ({
                id: p.id, hidden: p.hidden, displayed: p.getBoundingClientRect().width > 0
            }));
            return { state: notif.state, ids };
            """
        )


@pytest.mark.webext
def test_probe_top_n(selenium, base_url, firefox, firefox_notifications, wait):
    selenium.get("about:addons")
    page = AboutAddons(selenium, base_url).wait_for_page_to_load()
    page.click_recommendations_side_button()

    print("\n=== Iteration 1 — initial state ===")
    for s in _disco_state(selenium):
        print(f"  [{s['idx']}] {s['name']!r} l10n={s['installL10n']} hidden={s['installHidden']} visible={s['installVisible']}")

    # First install via the same flow as the failing test.
    ext = next(c for c in page.addon_cards_items if c.is_extension_card())
    print(f"\nFirst install: {ext.disco_addon_name.text}")
    ext.install_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallComplete
    ).close()
    if len(selenium.window_handles) > 1:
        selenium.switch_to.window(selenium.window_handles[0])

    # Refresh between installs (mirror what TC2 does).
    selenium.get("about:addons")
    page = AboutAddons(selenium, base_url).wait_for_page_to_load()
    page.click_recommendations_side_button()
    time.sleep(1)

    print("\n=== Iteration 2 — after refresh ===")
    for s in _disco_state(selenium):
        print(f"  [{s['idx']}] {s['name']!r} l10n={s['installL10n']} hidden={s['installHidden']} visible={s['installVisible']}")

    next_card = None
    for c in page.addon_cards_items:
        if not c.is_extension_card():
            continue
        install_btn = c.find_element(*c._addon_install_button_locator)
        if install_btn.get_attribute("hidden") is None:
            next_card = c
            break
    print(f"\n2nd next_card: {next_card.disco_addon_name.text if next_card else 'NONE'}")

    if next_card is None:
        return

    # Run iteration 2 + 3 like the failing test does.
    for iteration_idx in (2, 3):
        print(f"\n=== Iteration {iteration_idx} body ===")
        if iteration_idx > 2:
            next_card = None
            for c in page.addon_cards_items:
                if not c.is_extension_card():
                    continue
                install_btn = c.find_element(*c._addon_install_button_locator)
                if install_btn.get_attribute("hidden") is None:
                    next_card = c
                    break
            if next_card is None:
                print("No more uninstalled cards")
                return
            print(f"Next card: {next_card.disco_addon_name.text}")
        print(f"State BEFORE click: {_notif_state(selenium)}")
        next_card.install_button.click()
        print(f"State right after click: {_notif_state(selenium)}")
        try:
            conf = firefox.browser.wait_for_notification(
                firefox_notifications.AddOnInstallConfirmation
            )
            print(f"foxpuppet got AddOnInstallConfirmation")
            conf.install()
            firefox.browser.wait_for_notification(
                firefox_notifications.AddOnInstallComplete
            ).close()
            print(f"Iteration {iteration_idx} OK")
        except Exception as e:
            print(f"FAILED at iter {iteration_idx}: {type(e).__name__}: {e}")
            print(f"State at failure: {_notif_state(selenium)}")
            return
        if iteration_idx < 3:
            selenium.get("about:addons")
            page = AboutAddons(selenium, base_url).wait_for_page_to_load()
            page.click_recommendations_side_button()
            time.sleep(2)
