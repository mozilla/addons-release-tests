"""Shadow-DOM helpers for Firefox-driven webext tests.

Many controls in `about:addons` are Mozilla custom elements
(``moz-input-search``, ``moz-button``, ``moz-toggle`` ...) whose real content
lives inside shadow DOM. Marionette does not expose
``WebElement.shadow_root`` on Firefox, so any access into a shadow root has
to go through ``execute_script``. These helpers wrap the JS so test code
stays readable.
"""

# All helpers take a Selenium ``driver`` and a host CSS selector that resolves
# to the *outer* custom element. Pass the **inner** selector relative to the
# host's ``shadowRoot``.


def shadow_query(driver, host_css, inner_css):
    """Return the first element matching ``inner_css`` inside the shadow root
    of the element matching ``host_css``. Returns ``None`` when the host
    cannot be found or when nothing matches inside its shadow root."""
    return driver.execute_script(
        """
        const host = document.querySelector(arguments[0]);
        if (!host || !host.shadowRoot) return null;
        return host.shadowRoot.querySelector(arguments[1]);
        """,
        host_css,
        inner_css,
    )


def shadow_query_all(driver, host_css, inner_css):
    """Return all elements matching ``inner_css`` inside ``host_css``'s shadow
    root. Returns an empty list if the host or shadow root are missing."""
    return driver.execute_script(
        """
        const host = document.querySelector(arguments[0]);
        if (!host || !host.shadowRoot) return [];
        return [...host.shadowRoot.querySelectorAll(arguments[1])];
        """,
        host_css,
        inner_css,
    )


def shadow_visible(driver, host_css, inner_css):
    """``True`` when ``inner_css`` resolves inside ``host_css``'s shadow root
    and the matched element has a non-zero bounding box."""
    return bool(
        driver.execute_script(
            """
            const host = document.querySelector(arguments[0]);
            if (!host || !host.shadowRoot) return false;
            const el = host.shadowRoot.querySelector(arguments[1]);
            if (!el) return false;
            const rect = el.getBoundingClientRect();
            return rect.width > 0 && rect.height > 0;
            """,
            host_css,
            inner_css,
        )
    )


def shadow_click(driver, host_css, inner_css=None):
    """Click an element inside ``host_css``'s shadow root.

    When ``inner_css`` is ``None`` the host element itself is clicked — useful
    for components like ``moz-toggle`` whose event wiring lives on the host
    and is bypassed by clicking the inner shadow ``<button>``.
    """
    return driver.execute_script(
        """
        const host = document.querySelector(arguments[0]);
        if (!host) throw new Error('Host not found: ' + arguments[0]);
        if (!arguments[1]) {
            host.click();
            return true;
        }
        const inner = host.shadowRoot && host.shadowRoot.querySelector(arguments[1]);
        if (!inner) throw new Error('Inner not found: ' + arguments[1]);
        inner.click();
        return true;
        """,
        host_css,
        inner_css,
    )
