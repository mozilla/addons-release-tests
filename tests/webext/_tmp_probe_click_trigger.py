"""Probe: does Selenium's `.click()` on the `<moz-button class="more-options-button">`
actually open the addon-card's panel-list? Compare against a JS click."""
import json
import time

import pytest
from selenium.webdriver.common.by import By

from pages.desktop.about_addons import AboutAddons


def _state(driver):
    return driver.execute_script(
        """
        const lists = [...document.querySelectorAll('panel-list')].map(l => ({
            id: l.id,
            open: l.hasAttribute('open'),
            box: l.getBoundingClientRect().width,
        }));
        const items = [...document.querySelectorAll("panel-item[action='remove']")].map(p => ({
            visible: p.getBoundingClientRect().width > 0,
            offsetParent: !!p.offsetParent,
        }));
        return { lists, removeItems: items };
        """
    )


@pytest.mark.webext
def test_probe_click(selenium, base_url, firefox, firefox_notifications, wait):
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
    time.sleep(2)

    print("\n=== before any click ===")
    print(json.dumps(_state(selenium), indent=2))

    # Selenium .click() on the moz-button.
    triggers = selenium.find_elements(By.CSS_SELECTOR, ".more-options-button")
    print(f"\nfound {len(triggers)} triggers")
    for i, t in enumerate(triggers):
        print(f"  trigger[{i}] displayed={t.is_displayed()} tag={t.tag_name}")

    print("\n=== about to selenium-click trigger[0] ===")
    triggers[0].click()
    time.sleep(2)
    print(json.dumps(_state(selenium), indent=2))

    # Then try a JS click as a comparison.
    print("\n=== about to JS-click trigger[0] ===")
    selenium.execute_script(
        "document.querySelectorAll('.more-options-button')[0].click();"
    )
    time.sleep(2)
    print(json.dumps(_state(selenium), indent=2))
