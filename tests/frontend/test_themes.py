"""A python file that contains tests regarding themes, categories"""
import pytest

from selenium.webdriver.support.select import Select

from pages.desktop.frontend.search import Search
from pages.desktop.frontend.themes import Themes


@pytest.mark.parametrize(
    "count, category",
    enumerate(
        [
            "Abstract",
            "Causes",
            "Fashion",
            "Film and TV",
            "Firefox",
            "Foxkeh",
            "Holiday",
            "Music",
            "Nature",
            "Other",
            "Scenery",
            "Seasonal",
            "Solid",
            "Sports",
            "Websites",
        ]
    ),
)
@pytest.mark.nondestructive
def test_themes_categories(base_url, selenium, count, category):
    """Tests that theme categories are displayed correctly."""
    themes = Themes(selenium, base_url).open()
    assert "Categories" in themes.categories.categories_list_header.text
    # clicking through each Theme Category
    assert category in themes.categories.category_list[count].category_button_name
    themes.categories.category_list[count].click()
    category_results = Search(selenium, base_url)
    # checking that search results within that category are sorted correctly
    category_results.wait_for_contextcard_update(category)
    select = Select(category_results.filter_by_sort)
    assert "Most Users" in select.first_selected_option.text


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_themes_landing_header(base_url, selenium):
    """Tests the header section on the themes landing page."""
    themes = Themes(selenium, base_url).open()
    # checking that 'Themes' is underlined in the header menu
    assert "Themes" in themes.header.is_active_link
    assert "Themes" in themes.title
    assert "Change your browser's appearance" in themes.header_summary


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_recommended_themes(base_url, selenium):
    """Tests that recommended themes are shown on the landing page."""
    themes = Themes(selenium, base_url).open()
    shelf_items = themes.shelves.recommended_addons.list
    assert "Recommended themes" in themes.shelves.recommended_addons.card_header
    # the following statements are checking that each shelf has three themes
    # and each theme has a name, preview and number of users
    assert len(shelf_items) == 3
    for item in shelf_items:
        assert item.name
        assert item.addon_icon_preview.is_displayed()
        assert item.addon_users_preview.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_browse_more_recommended_themes(base_url, selenium):
    """Tests navigation to the full list of recommended themes."""
    themes = Themes(selenium, base_url).open()
    themes.shelves.recommended_addons.browse_all()
    assert "type=statictheme" in selenium.current_url
    search_results = Search(selenium, base_url)
    select = Select(search_results.filter_by_badging)
    assert select.first_selected_option.text == "Recommended"
    for result in search_results.result_list.search_results:
        assert "Recommended" in result.promoted_badge_label


@pytest.mark.nondestructive
def test_top_rated_themes(base_url, selenium):
    """Tests that top-rated themes are displayed on the themes page."""
    themes = Themes(selenium, base_url).open()
    shelf_items = themes.shelves.top_rated_addons.list
    assert "Top rated themes" in themes.shelves.top_rated_addons.card_header
    # the following statements are checking that each shelf has three themes
    # and each theme has a name, preview and number of users
    assert len(shelf_items) == 3
    for item in shelf_items:
        assert item.name
        assert item.addon_icon_preview.is_displayed()
        assert item.addon_users_preview.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_browse_more_top_rated_themes(base_url, selenium):
    """Tests navigation to the full list of top-rated themes."""
    themes = Themes(selenium, base_url).open()
    themes.shelves.top_rated_addons.browse_all()
    assert "sort=rating&type=statictheme" in selenium.current_url
    search_results = Search(selenium, base_url)
    ratings = search_results.result_list.themes
    for rating in ratings:
        assert rating.rating >= 4


@pytest.mark.nondestructive
def test_trending_themes(base_url, selenium):
    """Tests that trending themes are shown on the themes page."""
    themes = Themes(selenium, base_url).open()
    shelf_items = themes.shelves.trending_addons.list
    assert "Trending themes" in themes.shelves.trending_addons.card_header
    # the following statements are checking that each shelf has three themes
    # and each theme has a name, preview and number of users
    assert len(shelf_items) == 3
    for item in shelf_items:
        assert item.name
        assert item.addon_icon_preview.is_displayed()
        assert item.addon_users_preview.is_displayed()


@pytest.mark.sanity
@pytest.mark.nondestructive
def test_browse_more_trending_themes(base_url, selenium):
    """Tests navigation to the full list of trending themes."""
    themes = Themes(selenium, base_url).open()
    themes.shelves.trending_addons.browse_all()
    assert "sort=hotness&type=statictheme" in selenium.current_url
    search_results = Search(selenium, base_url)
    # trending add-ons don't have a predictable order so we
    # check that search results are displayed for this sort type
    assert len(search_results.result_list.themes) == 25
