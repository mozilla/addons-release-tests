"""Probe: dump the structure of an installed addon card to find the
current selectors for the three-dot 'More' button and the panel items
(Remove / Report / Manage) it opens."""
import json
import time

import pytest
from selenium.webdriver.common.by import By

from pages.desktop.about_addons import AboutAddons


@pytest.mark.webext
def test_dump_more_options_dom(
    selenium, base_url, firefox, firefox_notifications, wait
):
    # Install one extension so an addon-card lives under the Extensions tab.
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

    # Dump the structure of the first addon-card.
    info = selenium.execute_script(
        """
        const out = {};
        const cards = [...document.querySelectorAll('addon-card')];
        out.addonCardCount = cards.length;
        if (!cards.length) return out;
        const card = cards[0];
        out.cardName = card.querySelector('.addon-name')?.textContent?.trim();
        // 1) Does the legacy locator resolve from the document?
        out.docOptionsButton = !!document.querySelector(
            "button[data-l10n-id='addon-options-button']"
        );
        // 2) Does the addon-card have an open shadowRoot?
        out.hasShadow = !!card.shadowRoot;
        // 3) Dump every <button> inside the addon-card (light DOM).
        out.cardButtons = [...card.querySelectorAll('button')].map(b => ({
            id: b.id,
            cls: b.className,
            l10n: b.getAttribute('data-l10n-id'),
            action: b.getAttribute('action'),
            tag: b.tagName.toLowerCase(),
            text: (b.textContent || '').trim().slice(0, 40),
        }));
        // 4) Dump every panel-list / panel-item the card exposes.
        out.panelLists = [...card.querySelectorAll('panel-list')].map(p => ({
            id: p.id,
            cls: p.className,
        }));
        out.panelItems = [...card.querySelectorAll('panel-item')].map(p => ({
            action: p.getAttribute('action'),
            l10n: p.getAttribute('data-l10n-id'),
            text: (p.textContent || '').trim().slice(0, 60),
        }));
        // 5) Look for the more-options trigger by class.
        out.moreOptsByClass = [...card.querySelectorAll('.more-options-button')].map(b => ({
            tag: b.tagName.toLowerCase(),
            cls: b.className,
            l10n: b.getAttribute('data-l10n-id'),
            action: b.getAttribute('action'),
            visible: b.getBoundingClientRect().width > 0,
        }));
        // 6) Search for any element with the l10n id without tag restriction.
        out.docByL10n = [...document.querySelectorAll("[data-l10n-id='addon-options-button']")].map(e => ({
            tag: e.tagName.toLowerCase(),
            cls: e.className,
        }));
        // 7) Click the more-options trigger and check what happens.
        const trigger = card.querySelector('.more-options-button');
        if (trigger) {
            trigger.click();
        }
        return out;
        """
    )
    print("\n=== MORE-OPTIONS DOM PROBE ===")
    print(json.dumps(info, indent=2))
    print("=== END PROBE ===\n")

    # After the JS clicked the trigger, check whether the panel-items become visible.
    time.sleep(1)
    post = selenium.execute_script(
        """
        const items = [...document.querySelectorAll('panel-item')].map(p => ({
            action: p.getAttribute('action'),
            tag: p.tagName.toLowerCase(),
            visible: p.getBoundingClientRect().width > 0,
        }));
        const lists = [...document.querySelectorAll('panel-list')].map(l => ({
            id: l.id,
            open: l.hasAttribute('open') || (l.getBoundingClientRect().width > 0),
        }));
        return { items, lists };
        """
    )
    print("\n=== AFTER CLICK ===")
    print(json.dumps(post, indent=2))

    # Probe the addon detail page Back button.
    selenium.get("about:addons")
    # navigate to the freshly-installed addon via its Manage panel-item by
    # clicking it manually through JS to bypass widget timing.
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    WebDriverWait(selenium, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "addon-card"))
    )
    selenium.execute_script(
        """
        const card = document.querySelector('addon-card');
        const btn = card.querySelector('.more-options-button');
        btn.click();
        """
    )
    time.sleep(1)
    selenium.execute_script(
        """
        const expand = document.querySelector("panel-item[action='expand']");
        expand && expand.click();
        """
    )
    time.sleep(2)
    detail = selenium.execute_script(
        """
        const out = {};
        out.goBackByAction = [...document.querySelectorAll("[action='go-back']")].map(e => ({
            tag: e.tagName.toLowerCase(),
            cls: e.className,
            l10n: e.getAttribute('data-l10n-id'),
        }));
        out.goBackByL10n = [...document.querySelectorAll(
            "[data-l10n-id='go-back-button'], [data-l10n-id='addon-detail-go-back']"
        )].map(e => ({
            tag: e.tagName.toLowerCase(),
            cls: e.className,
            l10n: e.getAttribute('data-l10n-id'),
            action: e.getAttribute('action'),
        }));
        out.backCandidates = [
            ...document.querySelectorAll('button,moz-button,[role=button]')
        ].filter(b => /back/i.test(
            (b.getAttribute('data-l10n-id') || '') + ' ' +
            (b.getAttribute('action') || '') + ' ' +
            (b.textContent || '')
        )).map(b => ({
            tag: b.tagName.toLowerCase(),
            cls: b.className,
            l10n: b.getAttribute('data-l10n-id'),
            action: b.getAttribute('action'),
            text: (b.textContent || '').trim().slice(0, 40),
        }));
        return out;
        """
    )
    print("\n=== DETAIL PAGE GO-BACK ===")
    print(json.dumps(detail, indent=2))
