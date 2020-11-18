import pytest
from pages.desktop.home import Home
from pages.desktop.search import Search


# Tests covering the homepage header
@pytest.mark.nondestructive
def test_click_header_explore(base_url, selenium):
    page = Home(selenium, base_url).open()
    page.header.click_explore()
    assert 'Add-ons for Firefox' in selenium.title


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


# Tests covering promo shelves
@pytest.mark.nondestructive
def test_browse_all_button_loads_correct_page(base_url, selenium):
    page = Home(selenium, base_url).open()
    page.recommended_extensions.browse_all
    assert 'type=extension' in selenium.current_url
    search_page = Search(selenium, base_url)
    for result in search_page.result_list.extensions:
        assert result.promoted_badge


@pytest.mark.skip(reason="this test requires more optimization")
@pytest.mark.parametrize(
    'i, page_url',
    enumerate(['language-tools', 'android']))
@pytest.mark.nondestructive
def test_more_dropdown_navigates_correctly(base_url, selenium, i, page_url):
    page = Home(selenium, base_url).open()
    page.header.more_menu(item=i)
    assert page_url in selenium.current_url


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
    page.wait_for_current_url(links)


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
    page.wait_for_current_url(links)


@pytest.mark.desktop_only
@pytest.mark.parametrize(
    "count, links",
    enumerate(
        [
            "firefox/lockwise/",
            "monitor.firefox",
            "firefox/browsers/",
            "getpocket.com",
        ]
    ),
)
@pytest.mark.nondestructive
def test_products_footer_links(base_url, selenium, count, links):
    page = Home(selenium, base_url).open()
    page.footer.products_links[count].click()
    page.wait_for_current_url(links)


@pytest.mark.desktop_only
@pytest.mark.parametrize(
    "count, links",
    enumerate(["twitter.com", "facebook.com", "youtube.com/c/firefox", ]),
)
@pytest.mark.nondestructive
def test_social_footer_links(base_url, selenium, count, links):
    page = Home(selenium, base_url).open()
    page.footer.social_links[count].click()
    page.wait_for_current_url(links)


@pytest.mark.desktop_only
@pytest.mark.parametrize(
    "count, links",
    enumerate(["privacy/websites/", "privacy/websites/", "legal/terms/mozilla", ]),
)
@pytest.mark.nondestructive
def test_legal_footer_links(base_url, selenium, count, links):
    page = Home(selenium, base_url).open()
    page.footer.legal_links[count].click()
    page.wait_for_current_url(links)


@pytest.mark.nondestructive
def test_change_language(base_url, selenium):
    page = Home(selenium, base_url).open()
    value = 'Deutsch'
    page.footer.language_picker(value)
    assert "de/firefox" in selenium.current_url
    assert "Erweiterungen" in page.header.extensions_text
