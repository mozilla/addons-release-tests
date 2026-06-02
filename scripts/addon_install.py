"""Programmatic add-on install helpers for webext tests.

The standard AMO "Add to Firefox" button is only present on the latest
version card. Older versions only expose a plain download link, which
Firefox treats as a file save rather than an install. To exercise the
update flow we need a way to start the install of an arbitrary version
*through the same chrome path* the UI uses — which is what
``AddonManager.installAddonFromAOM`` does. This helper triggers it from
Marionette's chrome context, leaving the standard install confirmation
door-hanger for foxpuppet to drive.
"""


def install_from_xpi_url(driver, xpi_url):
    """Kick off a Firefox add-on install for ``xpi_url`` and return when
    the install permission door-hanger is showing.

    The caller is expected to accept (or cancel) the door-hanger using
    foxpuppet's ``firefox.browser.wait_for_notification`` API.

    Returns the chrome-side result string for diagnostics
    (``installAddonFromAOM called`` on the happy path).
    """
    return driver.execute_async_script(
        """
        const callback = arguments[arguments.length - 1];
        const url = arguments[0];
        (async () => {
            try {
                const { AddonManager } = ChromeUtils.importESModule(
                    "resource://gre/modules/AddonManager.sys.mjs"
                );
                const win = Services.wm.getMostRecentWindow('navigator:browser');
                const install = await AddonManager.getInstallForURL(url, {
                    triggeringPrincipal: Services.scriptSecurityManager.getSystemPrincipal(),
                });
                if (!install) { callback('no install returned'); return; }
                AddonManager.installAddonFromAOM(
                    win.gBrowser.selectedBrowser,
                    Services.io.newURI(url),
                    install
                );
                callback('installAddonFromAOM called');
            } catch (e) {
                callback('error: ' + e.message);
            }
        })();
        """,
        xpi_url,
    )


def install_older_version_via_chrome(driver, xpi_url):
    """Switch into chrome context and call :func:`install_from_xpi_url`.

    The chrome-context switch is what makes the call reach Firefox's
    command system — see ``scripts.kbd`` for the same trick applied to
    chrome-level keyboard shortcuts.
    """
    with driver.context(driver.CONTEXT_CHROME):
        return install_from_xpi_url(driver, xpi_url)
