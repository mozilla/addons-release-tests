import pytest
from selenium.webdriver import ActionChains
from pages.desktop.home import Home
from pages.desktop.search import Search


# Tests covering the homepage header
@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_click_header_explore(base_url, selenium):
    page = Home(selenium, base_url).open()
    page.header.click_explore()
    assert "Explore" in page.header.is_active_link
    assert "Add-ons for Firefox" in selenium.title


@pytest.mark.nondestructive
def test_click_header_extensions(base_url, selenium):
    page = Home(selenium, base_url).open()
    ext_page = page.header.click_extensions()
    assert "Extensions" in page.header.is_active_link
    assert "Extensions" in ext_page.title


@pytest.mark.nondestructive
def test_click_header_themes(base_url, selenium):
    page = Home(selenium, base_url).open()
    themes_page = page.header.click_themes()
    assert "Themes" in page.header.is_active_link
    assert "Themes" in themes_page.text


@pytest.mark.nondestructive
def test_logo_routes_to_home(base_url, selenium):
    page = Home(selenium, base_url).open()
    home = page.header.click_title()
    assert home.primary_hero.is_displayed()


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_developer_hub_link(base_url, selenium):
    page = Home(selenium, base_url).open()
    page.header.click_developer_hub()
    assert "/developers/" in selenium.current_url


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_extension_workshop_link(base_url, selenium):
    page = Home(selenium, base_url).open()
    page.header.click_extension_workshop()


@pytest.mark.nondestructive
def test_search_field_is_displayed(base_url, selenium):
    page = Home(selenium, base_url).open()
    assert page.search.search_field.is_displayed()


@pytest.mark.parametrize(
    "count, page_url", enumerate(
        ["Dictionaries and Language Packs",
         "Firefox Android"])
)
@pytest.mark.desktop_only
@pytest.mark.nondestructive
@pytest.mark.skip
def test_more_dropdown_navigates_correctly(base_url, selenium, count, page_url):
    page = Home(selenium, base_url).open()
    page.header.more_menu(item=count)
    # assert page_url in selenium.current_url
    page.wait_for_title_update(page_url)


# Tests covering the homepage primary and secondary heroes
@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_primary_hero(base_url, selenium):
    page = Home(selenium, base_url).open()
    # several assertions that validate the presence of elements in the primary hero
    assert page.hero_banner.primary_hero_image.is_displayed()
    assert "Recommended".upper() in page.hero_banner.primary_hero_title
    hero_extension = page.hero_banner.primary_hero_extension
    assert page.hero_banner.primary_hero_extension_summary.is_displayed()
    page.hero_banner.click_hero_extension_link()
    page.wait_for_title_update(hero_extension)


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_hero_changes_with_refresh(base_url, selenium):
    page = Home(selenium, base_url).open()
    first_hero_extension = page.hero_banner.primary_hero_extension
    selenium.refresh()
    second_hero_extension = page.hero_banner.primary_hero_extension
    assert first_hero_extension != second_hero_extension


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_secondary_hero_message(base_url, selenium):
    page = Home(selenium, base_url).open()
    headline = "Extensions are like apps"
    description = "They add features to Firefox"
    assert headline in page.secondary_hero.secondary_hero_headline
    assert description in page.secondary_hero.secondary_hero_description
    page.secondary_hero.see_all_extensions()
    page.wait_for_title_update("Extensions")


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_secondary_hero_modules(base_url, selenium):
    page = Home(selenium, base_url).open()
    for module in page.secondary_hero.secondary_hero_modules:
        assert module.module_icon.is_displayed()
        assert module.module_description.is_displayed()


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_click_module_link(base_url, selenium):
    page = Home(selenium, base_url).open()
    # some module links will open in a new tab
    for module in page.secondary_hero.secondary_hero_modules:
        module.click_secondary_module_link()


# Tests covering promo shelves
@pytest.mark.nondestructive
def test_recommended_extensions_shelf(base_url, selenium):
    page = Home(selenium, base_url).open()
    assert "Recommended extensions" in page.recommended_extensions.card_header
    shelf_items = page.recommended_extensions.list
    assert len(shelf_items) == 4
    for item in shelf_items:
        item.shelf_item_elements(item)


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_see_more_recommended_extensions(base_url, selenium):
    page = Home(selenium, base_url).open()
    page.recommended_extensions.browse_all
    assert "type=extension" in selenium.current_url
    search_page = Search(selenium, base_url)
    for result in search_page.result_list.extensions:
        assert result.has_recommended_badge


@pytest.mark.nondestructive
def test_popular_themes_shelf(base_url, selenium):
    page = Home(selenium, base_url).open()
    assert "Popular themes" in page.popular_themes.card_header
    shelf_items = page.popular_themes.list
    assert len(shelf_items) == 3
    for item in shelf_items:
        item.shelf_item_elements(item)


@pytest.mark.nondestructive
def test_see_more_popular_themes(base_url, selenium):
    page = Home(selenium, base_url).open()
    page.popular_themes.browse_all
    sort = "users"
    search_page = Search(selenium, base_url)
    results = [getattr(result, sort) for result in search_page.result_list.themes]
    assert sorted(results, reverse=True) == results


@pytest.mark.nondestructive
def test_popular_extensions_shelf(base_url, selenium):
    page = Home(selenium, base_url).open()
    assert "Popular extensions" in page.popular_extensions.card_header
    shelf_items = page.popular_extensions.list
    assert len(shelf_items) == 4
    for item in shelf_items:
        item.shelf_item_elements(item)


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_see_more_popular_extensions(base_url, selenium):
    page = Home(selenium, base_url).open()
    page.popular_extensions.browse_all
    sort = "users"
    search_page = Search(selenium, base_url)
    results = [getattr(result, sort) for result in search_page.result_list.extensions]
    assert sorted(results, reverse=True) == results
    for result in search_page.result_list.extensions:
        assert result.has_recommended_badge


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_recommended_themes_shelf(base_url, selenium):
    page = Home(selenium, base_url).open()
    assert "Recommended themes" in page.recommended_themes.card_header
    shelf_items = page.recommended_themes.list
    assert len(shelf_items) == 3
    for item in shelf_items:
        item.shelf_item_elements(item)


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_see_more_recommended_themes(base_url, selenium):
    page = Home(selenium, base_url).open()
    page.recommended_themes.browse_all
    assert "type=statictheme" in selenium.current_url
    search_page = Search(selenium, base_url)
    for result in search_page.result_list.themes:
        assert result.has_recommended_badge


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_featured_collection_shelf(base_url, selenium):
    page = Home(selenium, base_url).open()
    page.featured_collections.see_collection_details()
    assert "/firefox/collections/" in selenium.current_url


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_shelf_item_rating(base_url, selenium):
    page = Home(selenium, base_url).open()
    shelf_item = page.recommended_extensions.list[0].root
    # add-on ratings are displayed when hovering over a shelf item
    page.wait_for_page_to_load()
    action = ActionChains(selenium)
    action.move_to_element(shelf_item).perform()
    assert page.recommended_extensions.list[0].addon_rating_preview.is_displayed()


@pytest.mark.parametrize(
    'count, category',
    enumerate([
        'Abstract',
        'Nature',
        'Film',
        'Scenery',
        'Music',
        'Seasonal',
    ])
)
@pytest.mark.nondestructive
@pytest.mark.desktop_only
def test_theme_categories_shelf(base_url, selenium, count, category):
    page = Home(selenium, base_url).open()
    assert 'Change the way Firefox looks' in page.theme_category.shelf_summary
    categories = page.theme_category.list
    categories[count].category_icon.is_displayed()
    assert category in categories[count].name
    categories[count].click()
    category_results = Search(selenium, base_url)
    category_results.wait_for_contextcard_update(category)


# Tests covering the homepage footer
@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_mozilla_footer_link(base_url, selenium):
    page = Home(selenium, base_url).open()
    page.footer.mozilla_link.click()
    assert "mozilla.org" in selenium.current_url


@pytest.mark.desktop_only
@pytest.mark.parametrize(
    "count, links",
    enumerate(
        [
            "about",
            "blog.mozilla.org",
            "extensionworkshop",
            "developers",
            "AMO/Policy",
            "discourse",
            "#Contact_us",
            "review_guide",
            "status",
        ]
    ),
)
@pytest.mark.nondestructive
def test_addons_footer_links(base_url, selenium, count, links):
    page = Home(selenium, base_url).open()
    page.footer.addon_links[count].click()
    assert links in selenium.current_url


@pytest.mark.desktop_only
@pytest.mark.parametrize(
    "count, links",
    enumerate(
        [
            "firefox/new",
            "firefox/mobile",
            "mixedreality.mozilla.org",
            "firefox",
        ]
    ),
)
@pytest.mark.nondestructive
def test_browsers_footer_links(base_url, selenium, count, links):
    page = Home(selenium, base_url).open()
    page.footer.browsers_links[count].click()
    assert links in selenium.current_url


@pytest.mark.desktop_only
@pytest.mark.parametrize(
    "count, links",
    enumerate(
        [
            "firefox/lockwise/",
            "monitor.firefox",
            "send.firefox",
            "firefox/browsers/",
            "getpocket.com",
        ]
    ),
)
@pytest.mark.nondestructive
def test_products_footer_links(base_url, selenium, count, links):
    page = Home(selenium, base_url).open()
    page.footer.products_links[count].click()
    assert links in selenium.current_url


@pytest.mark.desktop_only
@pytest.mark.parametrize(
    "count, links",
    enumerate(["twitter.com", "facebook.com", "youtube.com/user/firefoxchannel", ]),
)
@pytest.mark.nondestructive
def test_social_footer_links(base_url, selenium, count, links):
    page = Home(selenium, base_url).open()
    page.footer.social_links[count].click()
    assert links in selenium.current_url


@pytest.mark.desktop_only
@pytest.mark.parametrize(
    "count, links",
    enumerate(["privacy/websites/", "privacy/websites/", "legal/terms/mozilla", ]),
)
@pytest.mark.nondestructive
def test_legal_footer_links(base_url, selenium, count, links):
    page = Home(selenium, base_url).open()
    page.footer.legal_links[count].click()
    assert links in selenium.current_url


@pytest.mark.nondestructive
def test_change_language(base_url, selenium):
    page = Home(selenium, base_url).open()
    value = 'Deutsch'
    page.footer.language_picker(value)
    assert "de/firefox" in selenium.current_url
    assert "Erweiterungen" in page.header.extensions_text
