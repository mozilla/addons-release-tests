"""Trace what happens during the SECOND install after a full first install."""
import time
import pytest
from selenium.webdriver.common.by import By

from pages.desktop.about_addons import AboutAddons


@pytest.mark.webext
def test_inspect(selenium, base_url, firefox, firefox_notifications, wait):
    selenium.get("about:addons")
    page = AboutAddons(selenium, base_url).wait_for_page_to_load()
    page.click_recommendations_side_button()
    # First install — full flow
    first_card = None
    for c in page.addon_cards_items:
        if c.is_extension_card():
            first_card = c
            break
    print(f"\nFIRST card: name={first_card.disco_addon_name.text}")
    first_card.install_button.click()
    firefox.browser.wait_for_notification(firefox_notifications.AddOnInstallConfirmation).install()
    firefox.browser.wait_for_notification(firefox_notifications.AddOnInstallComplete).close()
    print(f"AFTER first install completion")

    # Now look at the disco state
    time.sleep(2)
    cards_state = selenium.execute_script("""
        return [...document.querySelectorAll('.card.addon')].map((c, i) => {
            const installBtn = c.querySelector('button[action=install-addon]');
            const manageBtn = c.querySelector('button[action=manage-addon]');
            return {
                idx: i,
                name: c.querySelector('.disco-addon-name')?.textContent.trim().slice(0, 30),
                installL10n: installBtn?.getAttribute('data-l10n-id'),
                installHidden: installBtn?.hasAttribute('hidden'),
                manageHidden: manageBtn?.hasAttribute('hidden'),
            };
        });
    """)
    print(f"\nCards state after 1st install:")
    for c in cards_state:
        print(f"  [{c['idx']}] {c['name']!r} l10n={c['installL10n']} instHidden={c['installHidden']} mngHidden={c['manageHidden']}")

    # Find next un-installed extension
    next_card = None
    for c in page.addon_cards_items:
        if not c.is_extension_card():
            continue
        install_btn = c.find_element(*c._addon_install_button_locator)
        if install_btn.get_attribute("hidden") is None:
            next_card = c
            print(f"\nNEXT extension card: {c.disco_addon_name.text}")
            break

    # Try the install
    print(f"\nClicking next card install...")
    next_card.install_button.click()
    # Watch for confirmation appearing
    for i in range(40):
        time.sleep(0.5)
        with selenium.context(selenium.CONTEXT_CHROME):
            state = selenium.execute_script("""
                const notif = document.getElementById('notification-popup');
                if (!notif) return null;
                const ids = [...notif.querySelectorAll('popupnotification')].map(p => ({id: p.id, hidden: p.hidden}));
                return {state: notif.state, ids};
            """)
        print(f"  t={i*0.5:.1f}s notif={state}")
        if state and state.get('state') == 'open':
            for n in state.get('ids', []):
                if not n['hidden']:
                    print(f"  ✓ active notification: {n['id']}")
                    return
