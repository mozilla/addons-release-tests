import pytest

from selenium.webdriver.support.select import Select

from pages.desktop.extensions import Extensions
from pages.desktop.search import Search


@pytest.mark.parametrize(
    'count, category',
    enumerate([
        'Alerts & Updates',
        'Appearance',
        'Bookmarks',
        'Download Management',
        'Feeds, News & Blogging',
        'Games & Entertainment',
        'Language Support',
        'Other',
        'Photos, Music & Videos',
        'Privacy & Security',
        'Search Tools',
        'Shopping',
        'Social & Communication',
        'Tabs',
        'Web Development',
    ])
)
@pytest.mark.nondestructive
def test_extensions_categories(base_url, selenium, count, category):
    extensions = Extensions(selenium, base_url).open()
    # clicking through each Category listed on Extensions homepage
    extensions.categories.category_list[count].click()
    category_results = Search(selenium, base_url)
    # checking that category search results are loaded and sorted by users
    category_results.wait_for_contextcard_update(category)
    select = Select(category_results.filter_by_sort)
    assert 'Most Users' in select.first_selected_option.text


@pytest.mark.nondestructive
def test_extension_landing_header(base_url, selenium):
    extensions = Extensions(selenium, base_url).open()
    # checking that 'Extensions' is underlined in the header menu
    assert 'Extensions' in extensions.header.is_active_link
    assert 'Extensions' in extensions.title
    assert 'Explore powerful tools and features' \
           in extensions.header_summary


@pytest.mark.nondestructive
def test_recommended_extensions_shelf(base_url, selenium):
    extensions = Extensions(selenium, base_url).open()
    shelf_items = extensions.shelves.recommended_addons.list
    assert 'Recommended extensions' in extensions.shelves.recommended_addons.card_header
    # the following statements are checking that each shelf has four addons
    # and each addon has a name, icon and number of users
    assert len(shelf_items) == 4
    for item in shelf_items:
        assert item.name
        assert item.addon_icon_preview.is_displayed()
        assert item.addon_users_preview.is_displayed()


@pytest.mark.nondestructive
def test_browse_more_recommended_extensions(base_url, selenium):
    extensions = Extensions(selenium, base_url).open()
    extensions.shelves.recommended_addons.browse_all()
    assert 'type=extension' in selenium.current_url
    search_results = Search(selenium, base_url)
    select = Select(search_results.filter_by_badging)
    assert select.first_selected_option.text == 'Recommended'
    for result in search_results.result_list.extensions:
        assert 'Recommended' in result.promoted_badge_label


@pytest.mark.nondestructive
def test_top_rated_extensions(base_url, selenium):
    extensions = Extensions(selenium, base_url).open()
    shelf_items = extensions.shelves.top_rated_addons.list
    assert 'Top rated extensions' in extensions.shelves.top_rated_addons.card_header
    # the following statements are checking that each shelf has four addons
    # and each addon has a name, icon and number of users
    assert len(shelf_items) == 4
    for item in shelf_items:
        assert item.name
        assert item.addon_icon_preview.is_displayed()
        assert item.addon_users_preview.is_displayed()


@pytest.mark.nondestructive
def test_browse_more_top_rated_extensions(base_url, selenium):
    extensions = Extensions(selenium, base_url).open()
    extensions.shelves.top_rated_addons.browse_all()
    assert 'sort=rating&type=extension' in selenium.current_url
    search_results = Search(selenium, base_url)
    select = Select(search_results.filter_by_badging)
    assert select.first_selected_option.text == 'Recommended'
    for result in search_results.result_list.extensions:
        assert 'Recommended' in result.promoted_badge_label
    # using a list slice below (normal len is 25) to validate rating ordering
    # because not all addons in the list have a rating on stage
    ratings = search_results.result_list.extensions[0:16]
    for rating in ratings:
        assert rating.rating >= 4


@pytest.mark.nondestructive
def test_trending_extensions(base_url, selenium):
    extensions = Extensions(selenium, base_url).open()
    shelf_items = extensions.shelves.trending_addons.list
    assert 'Trending extensions' in extensions.shelves.trending_addons.card_header
    # the following statements are checking that each shelf has four addons
    # and each addon has a name, icon and number of users
    assert len(shelf_items) == 4
    for item in shelf_items:
        assert item.name
        assert item.addon_icon_preview.is_displayed()
        assert item.addon_users_preview.is_displayed()


@pytest.mark.nondestructive
def test_browse_more_trending_extensions(base_url, selenium):
    extensions = Extensions(selenium, base_url).open()
    extensions.shelves.trending_addons.browse_all()
    assert 'sort=hotness&type=extension' in selenium.current_url
    search_results = Search(selenium, base_url)
    select = Select(search_results.filter_by_badging)
    assert select.first_selected_option.text == 'Recommended'
    for result in search_results.result_list.extensions:
        assert 'Recommended' in result.promoted_badge_label
