import time

import pytest
import random

from pages.desktop.about_addons import AboutAddons
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


@pytest.mark.prod_only
@pytest.mark.firefox_release
@pytest.mark.skip(reason='Still investigating why this test has started failing recently')
def test_about_addons_search(selenium, base_url):
    selenium.get('about:addons')
    about_addons = AboutAddons(selenium).wait_for_page_to_load()
    amo_search_results = about_addons.search_box('privacy')
    # verify that the query string is registered in AMO search results page title
    amo_search_results.wait_for_contextcard_update('privacy')
    # verify that the search query produced results (this is a popular query so we expect
    # to see the first page of results to be fully populated, i.e. 25 items)
    amo_search_results.search_results_list_loaded(25)
    assert 'privacy' in amo_search_results.result_list.extensions[0].name.lower()


@pytest.mark.prod_only
@pytest.mark.firefox_release
def test_about_addons_find_more_addons(selenium, base_url, wait):
    selenium.get('about:addons')
    about_addons = AboutAddons(selenium).wait_for_page_to_load()
    amo_home = about_addons.click_find_more_addons()
    # checks that the button redirects correctly to AMO homepage
    wait.until(lambda _: amo_home.primary_hero.is_displayed())


@pytest.mark.prod_only
@pytest.mark.firefox_release
def test_about_addons_addon_cards(selenium, base_url, wait):
    selenium.get('about:addons')
    about_addons = AboutAddons(selenium)
    # waits for the list of addon cards to be loaded (currently we have minimum 7 cards)
    wait.until(
        lambda _: len([el.disco_addon_name for el in about_addons.addon_cards_items])
        >= 7
    )
    # theme images are slower to load, so we need to wait for them to be visible too
    wait.until(lambda _: about_addons.addon_cards_items[0].theme_image.is_displayed())
    for item in about_addons.addon_cards_items:
        # extension cards should have the following elements
        if item.is_extension_card():
            assert item.disco_addon_name.is_displayed()
            assert item.disco_addon_author.is_displayed()
            assert len(item.disco_extension_summary) > 0
            assert item.disco_extension_rating.is_displayed()
            assert item.disco_extension_users.is_displayed()
            assert item.extension_image.is_displayed()
        else:
            # theme cards should have only these items
            assert item.disco_addon_name.is_displayed()
            assert item.disco_addon_author.is_displayed()
            assert item.theme_image.is_displayed()


@pytest.mark.prod_only
@pytest.mark.firefox_release
def test_about_addons_addon_cards_author_link(selenium, base_url, wait):
    selenium.get('about:addons')
    about_addons = AboutAddons(selenium)
    # waiting for the addon cards data to be retrieved (the author names in this case)
    wait.until(
        lambda _: len([el.disco_addon_author for el in about_addons.addon_cards_items])
        >= 7
    )
    disco_addon_name = about_addons.addon_cards_items[0].disco_addon_name.text
    # clicking on the author link should open the addon detail page on AMO
    amo_detail_page = about_addons.addon_cards_items[0].click_disco_addon_author()
    # checking that the expected detail page was opened
    wait.until(lambda _: disco_addon_name == amo_detail_page.name)


@pytest.mark.prod_only
@pytest.mark.firefox_release
def test_about_addons_addon_stats_match_amo(selenium, base_url, wait):
    selenium.get('about:addons')
    about_addons = AboutAddons(selenium)
    # waiting for the addon cards data to be retrieved (the author names in this case)
    wait.until(
        lambda _: len([el.disco_addon_author for el in about_addons.addon_cards_items])
        >= 7
    )
    disco_addon_name = about_addons.addon_cards_items[1].disco_addon_name.text
    disco_rating_score = about_addons.addon_cards_items[1].rating_score
    disco_users = about_addons.addon_cards_items[1].user_count
    # clicking on the author link should open the addon detail page on AMO
    amo_detail_page = about_addons.addon_cards_items[1].click_disco_addon_author()
    wait.until(lambda _: disco_addon_name == amo_detail_page.name)
    # check that the rating and the users from about:addons are matching with AMO
    assert disco_rating_score == amo_detail_page.stats.rating_score_tile
    assert disco_users == amo_detail_page.stats.stats_users_count


@pytest.mark.prod_only
@pytest.mark.firefox_release
def test_about_addons_install_extension(
    selenium, base_url, wait, firefox, firefox_notifications
):
    selenium.get('about:addons')
    about_addons = AboutAddons(selenium)
    # waiting for the addon cards data to be retrieved (the install buttons in this case)
    wait.until(
        lambda _: len([el.install_button for el in about_addons.addon_cards_items]) >= 7
    )
    disco_addon_name = about_addons.addon_cards_items[1].disco_addon_name.text
    disco_addon_author = about_addons.addon_cards_items[1].disco_addon_author.text
    # install the recommended extension
    about_addons.addon_cards_items[1].install_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    time.sleep(2)
    # some addons will open support pages in new tabs after installation;
    # we need to return to the first (about:addons) tab if that happens
    if len(selenium.window_handles) > 1:
        selenium.switch_to.window(selenium.window_handles[0])
    # open the manage Extensions page to verify that the addon was installed correctly
    about_addons.click_extensions_side_button()
    # verify that the extension installed is present in manage Extensions; if the names
    # don't match (which happens sometimes due to differences between AMO names and manifest
    # names), check that the add-on author is the same as an alternative check;
    try:
        assert disco_addon_name in [el.text for el in about_addons.installed_addon_name]
    except AssertionError:
        about_addons.installed_addon_cards[0].click()
        wait.until(
            lambda _: disco_addon_author == about_addons.installed_addon_author_name
        )


@pytest.mark.prod_only
@pytest.mark.firefox_release
def test_about_addons_install_theme(
    selenium, base_url, wait, firefox, firefox_notifications
):
    selenium.get('about:addons')
    about_addons = AboutAddons(selenium)
    # waiting for the addon cards data to be retrieved (the install buttons in this case)
    wait.until(
        lambda _: len([el.install_button for el in about_addons.addon_cards_items]) >= 7
    )
    disco_theme_name = about_addons.addon_cards_items[0].disco_addon_name.text
    # make a note of the image source of the theme we are about to install
    disco_theme_image = about_addons.addon_cards_items[0].theme_image.get_attribute(
        'src'
    )
    # install the recommended theme
    about_addons.addon_cards_items[0].install_button.click()
    firefox.browser.wait_for_notification(
        firefox_notifications.AddOnInstallConfirmation
    ).install()
    about_addons.click_themes_side_button()
    # check that installed theme should be first on the manage Themes page
    assert 'true' in about_addons.enabled_theme_active_status
    assert disco_theme_image == about_addons.enabled_theme_image
    try:
        assert disco_theme_name in about_addons.installed_addon_name[0].text
    # currently, there can be some mismatches between addon names in the Recommendations pane
    # (where the addon details are fetched from AMO) and the installed addons pane
    # (where the details are fetched from the addon manifest); if this occurs, we don't
    # want the test to fail because this is a long-standing issue with no prospect of being
    # fixed in the near future; instead, we fall back to verifying that the theme images
    # are the same in the Recommendations pane and the installed Themes pane
    except AssertionError:
        assert disco_theme_image == about_addons.enabled_theme_image
