import pytest

from pages.desktop.frontend.extensions import Extensions
from pages.desktop.frontend.home import Home
from pages.desktop.frontend.themes import Themes


@pytest.mark.parametrize(
    "language",
    ("it", "es-ES", "de", "fr"),
    ids=("Italiano", "Español", "Deutsch", "Français"),
)
@pytest.mark.fail
def test_header_translations(base_url, selenium, variables, language):
    selenium.get(f"{base_url}/{language}")
    page = Home(selenium, base_url).wait_for_page_to_load()
    assert (
        page.header.firefox_addons_blog_link.text
        in variables[language]["header"]["blog_link"]
    )
    assert (
        page.header.extension_workshop_link.text
        in variables[language]["header"]["extension_workshop_link"]
    )
    assert (
        page.header.developer_hub_link.text
        in variables[language]["header"]["developer_hub_link"]
    )
    assert page.header.login_button.text in variables[language]["header"]["login_link"]
    assert (
        page.header.extensions_text in variables[language]["header"]["extensions_link"]
    )
    assert page.header.themes_link.text in variables[language]["header"]["themes_link"]
    # 'More...' link and dropdown elements
    assert page.header.more_menu_link.text in variables[language]["header"]["more_link"]
    assert (
        page.header.more_menu_dropdown_sections[0].text
        in variables[language]["header"]["more_dropdown_for_firefox_section"]
    )
    assert (
        page.header.more_menu_dropdown_sections[1].text
        in variables[language]["header"]["more_dropdown_other_browsers_section"]
    )
    assert (
        page.header.more_menu_dropdown_links[0].text
        in variables[language]["header"]["more_dropdown_dictionaries_link"]
    )
    assert (
        page.header.more_menu_dropdown_links[1].text
        in variables[language]["header"]["more_dropdown_addons_for_android_link"]
    )


@pytest.mark.parametrize(
    "language",
    ("it", "es-ES", "de", "fr"),
    ids=("Italiano", "Español", "Deutsch", "Français"),
)
def test_shelf_titles_translations(base_url, selenium, variables, language):
    selenium.get(f"{base_url}/{language}")
    page = Home(selenium, base_url).wait_for_page_to_load()
    assert (
        variables[language]["home_page"]["shelf_title_recommended_extensions"]
        in page.addon_shelf_titles
    )
    assert (
        variables[language]["home_page"]["shelf_title_popular_themes"]
        in page.addon_shelf_titles
    )
    assert (
        variables[language]["home_page"]["shelf_title_recommended_themes"]
        in page.addon_shelf_titles
    )
    assert (
        variables[language]["home_page"]["shelf_title_theme_categories"]
        in page.theme_category.shelf_summary
    )


@pytest.mark.parametrize(
    "language",
    ("it", "es-ES", "de", "fr"),
    ids=("Italiano", "Español", "Deutsch", "Français"),
)
@pytest.mark.fail
def test_extensions_page_translations(base_url, selenium, variables, language):
    selenium.get(f"{base_url}/{language}/firefox/extensions/")
    page = Extensions(selenium, base_url)
    assert page.title in variables[language]["extensions_page"]["page_header"]
    assert page.header_summary in variables[language]["extensions_page"]["page_summary"]
    assert (
        page.categories.categories_list_header.text
        in variables[language]["extensions_page"]["shelf_title_categories"]
    )
    assert (
        page.shelves.recommended_addons.card_header
        in variables[language]["extensions_page"]["shelf_title_recommended_extensions"]
    )
    assert (
        page.shelves.top_rated_addons.card_header
        in variables[language]["extensions_page"]["shelf_title_top_rated_extensions"]
    )
    assert (
        page.shelves.trending_addons.card_header
        in variables[language]["extensions_page"]["shelf_title_trending_extensions"]
    )


@pytest.mark.parametrize(
    "language",
    ("it", "es-ES", "de", "fr"),
    ids=("Italiano", "Español", "Deutsch", "Français"),
)
@pytest.mark.fail
def test_themes_page_translations(base_url, selenium, variables, language):
    selenium.get(f"{base_url}/{language}/firefox/themes/")
    page = Themes(selenium, base_url)
    assert page.title in variables[language]["themes_page"]["page_header"]
    assert page.header_summary in variables[language]["themes_page"]["page_summary"]
    assert (
        page.categories.categories_list_header.text
        in variables[language]["themes_page"]["shelf_title_categories"]
    )
    assert (
        page.shelves.recommended_addons.card_header
        in variables[language]["themes_page"]["shelf_title_recommended_themes"]
    )
    assert (
        page.shelves.top_rated_addons.card_header
        in variables[language]["themes_page"]["shelf_title_top_rated_themes"]
    )
    assert (
        page.shelves.trending_addons.card_header
        in variables[language]["themes_page"]["shelf_title_trending_themes"]
    )
