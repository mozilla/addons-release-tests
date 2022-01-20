import pytest

from selenium.webdriver import ActionChains

from pages.desktop.frontend.home import Home
from pages.desktop.frontend.search import Search
from scripts import reusables


# Tests covering the homepage header
@pytest.mark.nondestructive
def test_click_header_extensions(base_url, selenium):
    page = Home(selenium, base_url).open()
    ext_page = page.header.click_extensions()
    assert 'Extensions' in ext_page.title


@pytest.mark.nondestructive
def test_click_header_themes(base_url, selenium):
    page = Home(selenium, base_url).open()
    themes_page = page.header.click_themes()
    assert 'Themes' in themes_page.text


@pytest.mark.nondestructive
def test_logo_routes_to_home(base_url, selenium):
    page = Home(selenium, base_url).open()
    home = page.header.click_title()
    assert home.primary_hero.is_displayed()


@pytest.mark.nondestructive
def test_firefox_addons_blog_link(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.header.click_firefox_addons_blog()
    page.wait_for_current_url('/blog/')


@pytest.mark.nondestructive
def test_developer_hub_link(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.header.click_developer_hub()
    assert '/developers/' in selenium.current_url


@pytest.mark.nondestructive
def test_extension_workshop_link(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.header.click_extension_workshop()
    assert 'extensionworkshop' in selenium.current_url


@pytest.mark.parametrize(
    'count, title',
    enumerate(
        [
            'Dictionaries and Language Packs',
            'Add-ons for Firefox Android',
        ]
    ),
)
@pytest.mark.nondestructive
def test_more_dropdown_navigates_correctly(base_url, selenium, count, title):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    # clicks on a link in the More menu and verifies that the correct page opens
    page.header.more_menu(item=count)
    page.wait_for_title_update(title)


# Tests covering the homepage primary and secondary heroes
@pytest.mark.nondestructive
def test_primary_hero(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    # several assertions that validate the presence of elements in the primary hero
    assert page.hero_banner.primary_hero_image.is_displayed()
    assert 'Recommended'.upper() in page.hero_banner.primary_hero_title
    hero_extension = page.hero_banner.primary_hero_extension_name
    assert page.hero_banner.primary_hero_extension_summary.is_displayed()
    # clicks on the Get extension button and checks that the correct detail page opens
    addon_detail = page.hero_banner.click_hero_extension_link()
    assert hero_extension in addon_detail.name


@pytest.mark.nondestructive
def test_secondary_hero_message(base_url, selenium, variables):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    assert (
        variables['secondary_hero_title'] in page.secondary_hero.secondary_hero_headline
    )
    assert (
        variables['secondary_hero_summary']
        in page.secondary_hero.secondary_hero_description
    )
    # checks that the message link opens the Extensions landing page
    extensions = page.secondary_hero.see_all_extensions()
    assert 'Extensions' in extensions.title


@pytest.mark.nondestructive
def test_secondary_hero_modules(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    # check that each of the three secondary hero modules has an icon and a short description
    for module in page.secondary_hero.secondary_hero_modules:
        assert module.module_icon.is_displayed()
        assert module.module_description.is_displayed()


@pytest.mark.parametrize(
    'count, module',
    enumerate(
        [
            'First module',
            'Second module',
            'Third module',
        ]
    ),
)
@pytest.mark.nondestructive
def test_click_module_link(base_url, selenium, count, module):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    # checks that the content linked in the secondary modules is available
    module = page.secondary_hero.secondary_hero_modules
    module[count].click_secondary_module_link()


# Tests covering promo shelves
@pytest.mark.nondestructive
def test_browse_all_recommended_extensions(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.recommended_extensions.browse_all()
    assert 'type=extension' in selenium.current_url
    search_page = Search(selenium, base_url)
    for result in search_page.result_list.extensions:
        assert result.promoted_badge


@pytest.mark.nondestructive
def test_home_recommended_extensions_shelf(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    assert "Recommended extensions" in page.recommended_extensions.card_header
    shelf_items = page.recommended_extensions.list
    # verifies that each shelf extension has the necessary components
    assert len(shelf_items) == 4
    for item in shelf_items:
        assert item.name.is_displayed()
        assert item.addon_icon_preview.is_displayed()
        assert item.addon_users_preview.is_displayed()


@pytest.mark.nondestructive
def test_home_see_more_popular_themes(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.popular_themes.browse_all()
    sort = "users"
    search_page = Search(selenium, base_url).wait_for_page_to_load()
    # checking that popular themes results are indeed sorted by users
    results = [getattr(result, sort) for result in search_page.result_list.themes]
    assert sorted(results, reverse=True) == results


@pytest.mark.nondestructive
def test_home_popular_themes_shelf(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    assert "Popular themes" in page.popular_themes.card_header
    shelf_items = page.popular_themes.list
    # verifies that each shelf themes has the necessary components
    assert len(shelf_items) == 3
    for item in shelf_items:
        assert item.name.is_displayed()
        assert item.addon_icon_preview.is_displayed()
        assert item.addon_users_preview.is_displayed()


@pytest.mark.nondestructive
def test_home_see_more_recommended_themes(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.recommended_themes.browse_all()
    assert "type=statictheme" in selenium.current_url
    search_page = Search(selenium, base_url)
    for result in search_page.result_list.themes:
        assert result.promoted_badge


@pytest.mark.nondestructive
def test_home_shelf_item_rating(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    shelf_item = page.recommended_extensions.list[0].root
    # wait for the shelf to become intractable (scrolled into view)
    reusables.scroll_into_view(selenium, shelf_item)
    # add-on ratings are displayed when hovering over a shelf item
    action = ActionChains(selenium)
    action.move_to_element(shelf_item).perform()
    assert page.recommended_extensions.list[0].addon_rating_preview.is_displayed()


@pytest.mark.nondestructive
def test_home_see_more_links(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    count = 0
    # clicks through each link in the homepage shelves and checks that the content is available
    while count < len(page.see_more_links_in_shelves):
        page.click_see_more_links(count)
        count += 1


@pytest.mark.parametrize(
    'count, category',
    enumerate(
        [
            'Abstract',
            'Nature',
            'Film',
            'Scenery',
            'Music',
            'Seasonal',
        ]
    ),
)
@pytest.mark.nondestructive
def test_theme_categories_shelf(base_url, selenium, count, category):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    # verifying the elements present in the homepage Theme Category shelf
    assert 'Change the way Firefox looks' in page.theme_category.shelf_summary
    categories = page.theme_category.list
    categories[count].category_icon.is_displayed()
    assert category in categories[count].name
    # checking that search results within that category are loaded
    categories[count].click()
    category_results = Search(selenium, base_url)
    category_results.wait_for_contextcard_update(category)


# Tests covering the homepage footer
@pytest.mark.nondestructive
def test_mozilla_footer_link(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.footer.mozilla_link.click()
    assert 'mozilla.org' in selenium.current_url


@pytest.mark.parametrize(
    'count, link',
    enumerate(
        [
            'about',
            'blog',
            'extensionworkshop',
            'developers',
            'add-on-policies',
            'blog.mozilla.org',
            'discourse',
            'Contact_us',
            'review_guide',
            'mozilla.org',  # temporary
        ]
    ),
)
@pytest.mark.nondestructive
def test_addons_footer_links(base_url, selenium, count, link):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.footer.addon_links[count].click()
    page.wait_for_current_url(link)


@pytest.mark.parametrize(
    'count, links',
    enumerate(
        [
            'firefox/new',
            'firefox/browsers/mobile/',
            'mixedreality.mozilla.org',
            'firefox/enterprise/',
        ]
    ),
)
@pytest.mark.nondestructive
def test_browsers_footer_links(base_url, selenium, count, links):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.footer.browsers_links[count].click()
    page.wait_for_current_url(links)


@pytest.mark.parametrize(
    'count, links',
    enumerate(
        [
            'firefox/browsers/',
            'products/vpn/',
            'relay.firefox.com/',
            'monitor.firefox',
            'getpocket.com',
        ]
    ),
)
@pytest.mark.nondestructive
def test_products_footer_links(base_url, selenium, count, links):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.footer.products_links[count].click()
    page.wait_for_current_url(links)


@pytest.mark.parametrize(
    'count, links',
    enumerate(
        [
            'twitter.com',
            'instagram.com',
            'youtube.com',
        ]
    ),
)
@pytest.mark.nondestructive
def test_social_footer_links(base_url, selenium, count, links):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.footer.social_links[count].click()
    page.wait_for_current_url(links)


@pytest.mark.parametrize(
    'count, links',
    enumerate(
        [
            'privacy/websites/',
            'privacy/websites/',
            'legal/terms/mozilla',
        ]
    ),
)
@pytest.mark.nondestructive
def test_legal_footer_links(base_url, selenium, count, links):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    page.footer.legal_links[count].click()
    page.wait_for_current_url(links)


@pytest.mark.nondestructive
def test_change_language(base_url, selenium):
    page = Home(selenium, base_url).open().wait_for_page_to_load()
    value = 'Deutsch'
    page.footer.language_picker(value)
    assert 'de/firefox' in selenium.current_url
    assert 'Erweiterungen' in page.header.extensions_text
