"""OS-aware keyboard helpers for Firefox webext tests.

Firefox chrome-level commands (e.g. the Add-ons Manager open shortcut) are
bound to different modifier keys on different operating systems:

* macOS uses **Cmd** (Selenium's ``Keys.COMMAND``) as the primary modifier
* Windows / Linux use **Ctrl** (``Keys.CONTROL``)

In addition, those commands are only invoked when the keystroke is sent
while Marionette is in **chrome** context — content-context ActionChains
chords are silently swallowed. ``send_chord_in_chrome`` wraps both of those
quirks.

Examples
--------
>>> # Open the Add-ons Manager from anywhere — Cmd+Shift+A on macOS,
>>> # Ctrl+Shift+A on Windows / Linux.
>>> send_chord_in_chrome(driver, [primary_modifier(), Keys.SHIFT], "a")

>>> # Disable an extension on its detail page — Alt+Shift+D on every OS
>>> # (Alt is Option on macOS, both surface as Keys.ALT in Selenium).
>>> send_chord_in_chrome(driver, [Keys.ALT, Keys.SHIFT], "d")
"""
import platform

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


def is_mac():
    """``True`` when the host running the tests is macOS."""
    return platform.system() == "Darwin"


def primary_modifier():
    """Return Cmd on macOS, Ctrl elsewhere — the modifier Firefox uses for
    its primary chrome-level shortcuts."""
    return Keys.COMMAND if is_mac() else Keys.CONTROL


def send_chord(driver, modifiers, key):
    """Press the given modifiers, send the key, release in reverse order.

    Runs in whatever Marionette context is currently active. Use
    :func:`send_chord_in_chrome` for shortcuts that target Firefox chrome
    commands.
    """
    chain = ActionChains(driver)
    for m in modifiers:
        chain = chain.key_down(m)
    chain = chain.send_keys(key)
    for m in reversed(modifiers):
        chain = chain.key_up(m)
    chain.perform()


def send_chord_in_chrome(driver, modifiers, key):
    """Same as :func:`send_chord` but switched into Marionette's chrome
    context so the chord reaches Firefox's command system."""
    with driver.context(driver.CONTEXT_CHROME):
        send_chord(driver, modifiers, key)
