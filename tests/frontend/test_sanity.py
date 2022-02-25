import pytest
import random

from pages.desktop.frontend.details import Detail
from pages.desktop.frontend.language_tools import LanguageTools


# For the scope of each of the custom markers used for sanity tests, see the pytest.ini file


@pytest.mark.nondestructive
@pytest.mark.prod_only
def test_language_tools_landing_page(selenium, base_url, variables):
    page = LanguageTools(selenium, base_url).open().wait_for_page_to_load()
    # verify the information present on the landing page
    assert variables['language_tools_page_header'] in page.language_tools_header
    assert variables['dictionaries_info'] in page.dictionaries_info_text
    assert variables['language_packs_info'] in page.language_packs_info_text
    # we don't always know the number of supported languages in advance,
    # but we can make sure we are in close range to what we always supported
    assert len(page.supported_languages_list) in range(120, 140)


@pytest.mark.nondestructive
@pytest.mark.prod_only
@pytest.mark.firefox_release
def test_install_language_pack(
    selenium, base_url, variables, firefox, firefox_notifications
):
    page = LanguageTools(selenium, base_url).open().wait_for_page_to_load()
    lang_packs_list = page.available_language_packs
    # pick a random language pack from the list and install it
    random.choice(lang_packs_list).click()
    lang_pack_detail = Detail(selenium, base_url).wait_for_page_to_load()
    lang_pack_detail.install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    assert 'Remove' in lang_pack_detail.button_text
    # uninstall the language pack and check that install button changes state
    lang_pack_detail.install()
    assert 'Add to Firefox' in lang_pack_detail.button_text


@pytest.mark.sanity
@pytest.mark.prod_only
@pytest.mark.firefox_release
def test_install_dictionary(
    selenium, base_url, variables, firefox, firefox_notifications
):
    page = LanguageTools(selenium, base_url).open().wait_for_page_to_load()
    dictionaries_list = page.available_dictionaries
    # pick a random dictionary from the list and install it
    random.choice(dictionaries_list).click()
    dictionary_detail = Detail(selenium, base_url).wait_for_page_to_load()
    dictionary_detail.install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    assert 'Remove' in dictionary_detail.button_text
    # uninstall the dictionary and check that install button changes state
    dictionary_detail.install()
    assert 'Add to Firefox' in dictionary_detail.button_text


@pytest.mark.sanity
@pytest.mark.prod_only
@pytest.mark.firefox_release
def test_install_extension(
    selenium, base_url, variables, firefox, firefox_notifications
):
    extension = variables['install_extension']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    assert 'Remove' in addon.button_text
    # uninstall the extension and check that install button changes state
    addon.install()
    assert 'Add to Firefox' in addon.button_text


@pytest.mark.sanity
@pytest.mark.prod_only
@pytest.mark.firefox_release
def test_install_theme(selenium, base_url, variables, firefox, firefox_notifications):
    extension = variables['install_theme']
    selenium.get(f'{base_url}/addon/{extension}')
    addon = Detail(selenium, base_url).wait_for_page_to_load()
    addon.install()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    assert 'Remove' in addon.button_text
    # uninstall the theme and check that install button changes state
    addon.install()
    assert 'Install Theme' in addon.button_text
